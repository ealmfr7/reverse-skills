#!/usr/bin/env python3
"""Summarize a HAR file and emit sanitized endpoint inventories."""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlparse


THIRD_PARTY_HINTS = (
    "google-analytics",
    "googletagmanager",
    "doubleclick",
    "facebook",
    "segment",
    "amplitude",
    "mixpanel",
    "sentry",
    "datadog",
    "hotjar",
    "intercom",
    "zendesk",
    "stripe",
    "paypal",
    "cloudflare",
)

API_PATH_RE = re.compile(
    r"(^|/)(api|v\d+|graphql|rest|auth|oauth|session|token|users?|account|profile|"
    r"orders?|checkout|payment|search|upload|download|files?|messages?|notifications?)"
    r"(/|$)",
    re.IGNORECASE,
)
GRAPHQL_OP_RE = re.compile(r"\b(query|mutation|subscription)\s+([A-Za-z_][A-Za-z0-9_]*)")
SENSITIVE_HEADERS = {
    "authorization",
    "cookie",
    "set-cookie",
    "x-csrf-token",
    "x-xsrf-token",
    "x-api-key",
    "api-key",
}


def load_har(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "log" not in data or "entries" not in data["log"]:
        raise ValueError("not a HAR file: expected log.entries")
    return data


def header_names(headers: list[dict]) -> set[str]:
    return {h.get("name", "").lower() for h in headers if h.get("name")}


def is_third_party(host: str) -> bool:
    return any(hint in host.lower() for hint in THIRD_PARTY_HINTS)


def looks_api(path: str, mime: str, request_headers: set[str]) -> bool:
    if API_PATH_RE.search(path):
        return True
    if "application/json" in mime.lower():
        return True
    if "x-requested-with" in request_headers or "authorization" in request_headers:
        return True
    return False


def extract_graphql(req: dict) -> list[dict]:
    post = req.get("postData") or {}
    text = post.get("text") or ""
    parsed_url = urlparse(req.get("url", ""))
    query_params = dict(parse_qsl(parsed_url.query, keep_blank_values=True))
    if not text and ("query" in query_params or "operationName" in query_params):
        text = json.dumps(
            {
                "query": query_params.get("query", ""),
                "operationName": query_params.get("operationName"),
                "variables": query_params.get("variables"),
            }
        )
    if not text:
        return []
    operations = []
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = None
    payloads = parsed if isinstance(parsed, list) else [parsed] if isinstance(parsed, dict) else []
    for payload in payloads:
        query = str(payload.get("query") or "")
        op_name = payload.get("operationName")
        match = GRAPHQL_OP_RE.search(query)
        if match or op_name:
            operations.append(
                {
                    "kind": match.group(1) if match else "?",
                    "name": op_name or match.group(2),
                    "has_variables": bool(payload.get("variables")),
                }
            )
    if not operations:
        for match in GRAPHQL_OP_RE.finditer(text):
            operations.append({"kind": match.group(1), "name": match.group(2), "has_variables": "variables" in text})
    return operations


def analyze(path: str) -> dict:
    har = load_har(path)
    entries = har["log"]["entries"]
    hosts = collections.Counter()
    methods = collections.Counter()
    statuses = collections.Counter()
    content_types = collections.Counter()
    auth_signals = collections.Counter()
    third_party = collections.Counter()
    endpoints: dict[tuple[str, str, str], dict] = {}
    graphql_ops: dict[tuple[str, str], dict] = {}
    websockets = []

    for entry in entries:
        req = entry.get("request", {})
        res = entry.get("response", {})
        method = req.get("method", "?")
        url = req.get("url", "")
        parsed = urlparse(url)
        host = parsed.netloc
        req_headers = header_names(req.get("headers", []))
        res_headers = header_names(res.get("headers", []))
        mime = (res.get("content", {}) or {}).get("mimeType", "")
        status = str(res.get("status", "?"))

        hosts[host] += 1
        methods[method] += 1
        statuses[status] += 1
        if mime:
            content_types[mime.split(";")[0]] += 1
        if is_third_party(host):
            third_party[host] += 1
        for name in sorted((req_headers | res_headers) & SENSITIVE_HEADERS):
            auth_signals[name] += 1

        if parsed.scheme in {"ws", "wss"}:
            messages = entry.get("_webSocketMessages") or entry.get("webSocketMessages") or []
            websockets.append(
                {
                    "method": method,
                    "url": url,
                    "host": host,
                    "path": parsed.path or "/",
                    "message_count": len(messages),
                    "message_directions": dict(collections.Counter(msg.get("type", "?") for msg in messages if isinstance(msg, dict))),
                }
            )

        gql_ops = extract_graphql(req)
        for op in gql_ops:
            key = (op["kind"], op["name"])
            item = graphql_ops.setdefault(key, {**op, "count": 0, "endpoints": []})
            item["count"] += 1
            gql_endpoint = f"{method} {host}{parsed.path or '/'}"
            if gql_endpoint not in item["endpoints"]:
                item["endpoints"].append(gql_endpoint)

        if parsed.path.endswith("/graphql") or "graphql" in parsed.path.lower():
            if not gql_ops:
                key = ("?", "?")
                item = graphql_ops.setdefault(key, {"kind": "?", "name": "?", "has_variables": False, "count": 0, "endpoints": []})
                item["count"] += 1

        if looks_api(parsed.path, mime, req_headers):
            query_keys = [k for k, _ in parse_qsl(parsed.query, keep_blank_values=True)]
            key = (method, host, parsed.path or "/")
            item = endpoints.setdefault(
                key,
                {
                    "method": method,
                    "host": host,
                    "path": parsed.path or "/",
                    "query_keys": sorted(set(query_keys)),
                    "statuses": [],
                    "mime_types": [],
                    "request_headers": sorted(req_headers - SENSITIVE_HEADERS),
                    "sensitive_headers_present": sorted(req_headers & SENSITIVE_HEADERS),
                    "count": 0,
                },
            )
            item["count"] += 1
            if status not in item["statuses"]:
                item["statuses"].append(status)
            clean_mime = mime.split(";")[0] if mime else "?"
            if clean_mime not in item["mime_types"]:
                item["mime_types"].append(clean_mime)
            item["query_keys"] = sorted(set(item["query_keys"]) | set(query_keys))

    return {
        "har": path,
        "entry_count": len(entries),
        "hosts": dict(hosts.most_common()),
        "methods": dict(methods.most_common()),
        "statuses": dict(statuses.most_common()),
        "content_types": dict(content_types.most_common()),
        "auth_signals": dict(auth_signals.most_common()),
        "third_party_hosts": dict(third_party.most_common()),
        "endpoints": sorted(endpoints.values(), key=lambda item: (item["host"], item["path"], item["method"])),
        "graphql_operations": sorted(graphql_ops.values(), key=lambda item: (item["name"] == "?", item["kind"], item["name"])),
        "websockets": websockets,
    }


def print_summary(data: dict):
    print(f"=== HAR Summary: {data['har']} ===")
    print(f"Entries: {data['entry_count']}")
    print()
    print("Top hosts:")
    for host, count in list(data["hosts"].items())[:12]:
        label = " third-party?" if is_third_party(host) else ""
        print(f"  {count:4}  {host}{label}")
    print()
    print("Methods:", " ".join(f"{k}={v}" for k, v in data["methods"].items()) or "none")
    print("Statuses:", " ".join(f"{k}={v}" for k, v in data["statuses"].items()) or "none")
    print()
    print("Auth/session header signals:")
    if data["auth_signals"]:
        for name, count in data["auth_signals"].items():
            print(f"  {count:4}  {name}")
    else:
        print("  none detected")
    print()
    print("Likely API endpoints:")
    if data["endpoints"]:
        for item in data["endpoints"]:
            q = f" query={','.join(item['query_keys'])}" if item["query_keys"] else ""
            sens = f" sensitive_headers={','.join(item['sensitive_headers_present'])}" if item["sensitive_headers_present"] else ""
            print(f"  {item['method']:7} {item['host']}{item['path']} count={item['count']}{q}{sens}")
    else:
        print("  none detected")
    print()
    print("GraphQL operations:")
    if data["graphql_operations"]:
        for op in data["graphql_operations"]:
            print(f"  {op['kind']} {op['name']} count={op['count']}")
    else:
        print("  none detected")
    print()
    print("WebSocket candidates:")
    if data["websockets"]:
        for ws in data["websockets"][:20]:
            print(f"  {ws['method']:7} {ws['url']}")
    else:
        print("  none detected")


def write_markdown(data: dict, path: Path):
    lines = ["# HAR Endpoint Inventory", ""]
    lines.append(f"Entries: {data['entry_count']}")
    lines.append("")
    lines.append("## Endpoints")
    lines.append("")
    lines.append("| Method | Host | Path | Count | Auth Signals |")
    lines.append("|---|---|---|---:|---|")
    for item in data["endpoints"]:
        auth = ", ".join(item["sensitive_headers_present"]) or "-"
        lines.append(f"| `{item['method']}` | `{item['host']}` | `{item['path']}` | {item['count']} | {auth} |")
    lines.append("")
    lines.append("## GraphQL Operations")
    lines.append("")
    if data["graphql_operations"]:
        for op in data["graphql_operations"]:
            lines.append(f"- `{op['kind']} {op['name']}` count={op['count']}")
    else:
        lines.append("None detected.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("har", help="Path to a HAR file")
    parser.add_argument("--json-out", help="Write sanitized summary JSON")
    parser.add_argument("--markdown-out", help="Write endpoint inventory Markdown")
    args = parser.parse_args()
    try:
        data = analyze(args.har)
        print_summary(data)
        if args.json_out:
            Path(args.json_out).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        if args.markdown_out:
            write_markdown(data, Path(args.markdown_out))
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
