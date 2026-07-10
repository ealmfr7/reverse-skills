#!/usr/bin/env python3
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit


SECRET_KEYS = re.compile(r"(authorization|cookie|token|secret|password|passwd|api[-_]?key|session)", re.I)
GRAPHQL_RE = re.compile(r"\b(query|mutation|subscription)\s+([A-Za-z_][A-Za-z0-9_]*)?", re.I)


def scrub_url(url: str) -> str:
    parsed = urlsplit(url)
    return parsed._replace(query="", fragment="").geturl()


def parse_body(text: str):
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


def graphql_from_body(body):
    if not isinstance(body, dict):
        return []
    candidates = []
    query = body.get("query")
    if isinstance(query, str):
        match = GRAPHQL_RE.search(query)
        kind = match.group(1).lower() if match else "query"
        name = body.get("operationName") or (match.group(2) if match else None) or "anonymous"
        candidates.append({"kind": kind, "name": name})
    return candidates


def endpoint_from_request(method: str, url: str, status=None):
    parsed = urlsplit(url)
    scheme = parsed.scheme.lower()
    return {
        "method": method.upper(),
        "scheme": scheme,
        "host": parsed.netloc,
        "path": parsed.path or "/",
        "url": scrub_url(url),
        "status": status,
    }


def load_har(data):
    entries = []
    for entry in data.get("log", {}).get("entries", []):
        req = entry.get("request", {})
        resp = entry.get("response", {})
        post = req.get("postData", {}) if isinstance(req.get("postData"), dict) else {}
        entries.append(
            {
                "method": req.get("method", "GET"),
                "url": req.get("url", ""),
                "status": resp.get("status"),
                "body": post.get("text", ""),
            }
        )
    return entries


def load_mitm(data):
    flows = data if isinstance(data, list) else data.get("flows", [])
    entries = []
    for flow in flows:
        req = flow.get("request", {})
        resp = flow.get("response", {}) or {}
        url = req.get("url") or req.get("pretty_url") or ""
        content = req.get("content") or req.get("text") or ""
        if isinstance(content, list):
            content = bytes(content).decode("utf-8", "replace")
        entries.append(
            {
                "method": req.get("method", "GET"),
                "url": url,
                "status": resp.get("status_code"),
                "body": content,
            }
        )
    return entries


def summarize(path: Path):
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    entries = load_har(data) if isinstance(data, dict) and "log" in data else load_mitm(data)

    endpoint_counts = Counter()
    endpoint_statuses = defaultdict(set)
    graphql = Counter()
    websockets = Counter()

    for entry in entries:
        url = entry["url"]
        if not url:
            continue
        endpoint = endpoint_from_request(entry["method"], url, entry["status"])
        key = (endpoint["method"], endpoint["scheme"], endpoint["host"], endpoint["path"], endpoint["url"])
        endpoint_counts[key] += 1
        if endpoint["status"] is not None:
            endpoint_statuses[key].add(endpoint["status"])

        if endpoint["scheme"] in {"ws", "wss"} or entry["status"] == 101:
            websockets[(endpoint["host"], endpoint["path"], endpoint["url"])] += 1

        for op in graphql_from_body(parse_body(entry.get("body", ""))):
            graphql[(op["kind"], op["name"], endpoint["url"])] += 1

    endpoints = []
    for key, count in sorted(endpoint_counts.items()):
        method, scheme, host, path_value, url = key
        endpoints.append(
            {
                "method": method,
                "scheme": scheme,
                "host": host,
                "path": path_value,
                "url": url,
                "count": count,
                "statuses": sorted(endpoint_statuses[key]),
            }
        )

    return {
        "endpoints": endpoints,
        "graphql_operations": [
            {"kind": kind, "name": name, "endpoint": endpoint, "count": count}
            for (kind, name, endpoint), count in sorted(graphql.items())
        ],
        "websockets": [
            {"host": host, "path": path_value, "url": url, "count": count}
            for (host, path_value, url), count in sorted(websockets.items())
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize HAR or mitmproxy JSON traffic without secret values.")
    parser.add_argument("capture", help="HAR file or mitmproxy JSON export")
    parser.add_argument("--json-out", help="Write structured summary JSON")
    args = parser.parse_args()

    try:
        summary = summarize(Path(args.capture))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    text = json.dumps(summary, indent=2, sort_keys=True)
    if SECRET_KEYS.search(text):
        # The summary should only contain scrubbed URLs and metadata. This guard
        # catches accidental future regressions.
        print("ERROR: summary contains sensitive-looking key names", file=sys.stderr)
        return 1
    if args.json_out:
        Path(args.json_out).write_text(text + "\n", encoding="utf-8")

    print(f"ENDPOINTS:{len(summary['endpoints'])}")
    print(f"GRAPHQL:{len(summary['graphql_operations'])}")
    print(f"WEBSOCKETS:{len(summary['websockets'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
