#!/usr/bin/env python3
"""Extract a structured endpoint inventory from dumped web assets."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse


TEXT_EXTS = {".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".html", ".htm", ".json", ".map"}
URL_RE = re.compile(r"""(?P<quote>["'`])(?P<url>https?://[^"'`\s<>]+|wss?://[^"'`\s<>]+)(?P=quote)""")
PATH_RE = re.compile(
    r"""(?P<quote>["'`])(?P<path>/(?:api|v\d+|graphql|rest|auth|oauth|session|token|users?|account|profile|orders?|checkout|payment|search|upload|download|files?|messages?|notifications?)[^"'`\s<>]*)(?P=quote)""",
    re.I,
)
FETCH_RE = re.compile(r"""\bfetch\s*\(\s*(?P<quote>["'`])(?P<target>[^"'`]+)(?P=quote)""", re.I)
AXIOS_RE = re.compile(r"""\baxios\.(?P<method>get|post|put|patch|delete|request)\s*\(\s*(?P<quote>["'`])(?P<target>[^"'`]+)(?P=quote)""", re.I)
GRAPHQL_RE = re.compile(r"\b(?P<kind>query|mutation|subscription)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)")
WS_RE = re.compile(r"""(?P<quote>["'`])(?P<url>wss?://[^"'`\s<>]+)(?P=quote)""", re.I)


def iter_files(root: Path):
    if root.is_file():
        yield root
        return
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_EXTS:
            yield path


def read_text(path: Path) -> str:
    data = path.read_bytes()
    if b"\x00" in data[:4096]:
        return ""
    return data.decode("utf-8", errors="ignore")


def normalize_url(target: str, base_url: str | None) -> str:
    if target.startswith(("http://", "https://", "ws://", "wss://")):
        return target
    if not base_url:
        return target
    return urljoin(base_url.rstrip("/") + "/", target.lstrip("/"))


def add_endpoint(items: dict[tuple[str, str], dict], method: str, url: str, source: str, evidence: str):
    key = (method.upper(), url)
    parsed = urlparse(url)
    item = items.setdefault(
        key,
        {
            "method": method.upper(),
            "url": url,
            "scheme": parsed.scheme,
            "host": parsed.netloc,
            "path": parsed.path or "/",
            "query": parsed.query,
            "sources": [],
            "evidence": [],
        },
    )
    if source not in item["sources"]:
        item["sources"].append(source)
    if evidence not in item["evidence"] and len(item["evidence"]) < 5:
        item["evidence"].append(evidence.strip()[:240])


def infer_context_method(text: str, start: int, default: str = "GET") -> str:
    window = text[start : start + 160].split(";")[0].lower()
    match = re.search(r"""method\s*:\s*["'`](get|post|put|patch|delete)["'`]""", window)
    if match:
        return match.group(1).upper()
    return default


def extract(root: Path, base_url: str | None) -> dict:
    endpoints: dict[tuple[str, str], dict] = {}
    graphql_ops: dict[tuple[str, str], dict] = {}

    for path in iter_files(root):
        text = read_text(path)
        if not text:
            continue
        source = str(path.relative_to(root)) if root.is_dir() else path.name

        for match in FETCH_RE.finditer(text):
            target = normalize_url(match.group("target"), base_url)
            method = infer_context_method(text, match.end(), "GET")
            add_endpoint(endpoints, method, target, source, match.group(0))

        for match in AXIOS_RE.finditer(text):
            method = match.group("method").upper()
            if method == "REQUEST":
                method = infer_context_method(text, match.end(), "GET")
            target = normalize_url(match.group("target"), base_url)
            add_endpoint(endpoints, method, target, source, match.group(0))

        for match in URL_RE.finditer(text):
            url = match.group("url")
            if url.startswith(("ws://", "wss://")):
                add_endpoint(endpoints, "WS", url, source, match.group(0))
            elif any(token in url.lower() for token in ("/api", "/graphql", "/auth", "/oauth", "/session", "/v1", "/v2")):
                method = "POST" if "graphql" in url.lower() else "GET"
                add_endpoint(endpoints, method, url, source, match.group(0))

        for match in PATH_RE.finditer(text):
            url = normalize_url(match.group("path"), base_url)
            method = "POST" if "graphql" in match.group("path").lower() else infer_context_method(text, match.end(), "GET")
            add_endpoint(endpoints, method, url, source, match.group(0))

        for match in GRAPHQL_RE.finditer(text):
            key = (match.group("kind"), match.group("name"))
            item = graphql_ops.setdefault(
                key,
                {
                    "kind": match.group("kind"),
                    "name": match.group("name"),
                    "sources": [],
                },
            )
            if source not in item["sources"]:
                item["sources"].append(source)

        for match in WS_RE.finditer(text):
            add_endpoint(endpoints, "WS", match.group("url"), source, match.group(0))

    return {
        "root": str(root),
        "base_url": base_url,
        "endpoints": sorted(endpoints.values(), key=lambda item: (item["host"], item["path"], item["method"], item["url"])),
        "graphql_operations": sorted(graphql_ops.values(), key=lambda item: (item["kind"], item["name"])),
    }


def write_markdown(data: dict, path: Path):
    lines = ["# Endpoint Inventory", ""]
    lines.append("| Method | Host | Path | Sources |")
    lines.append("|---|---|---|---|")
    for endpoint in data["endpoints"]:
        sources = ", ".join(endpoint["sources"])
        host = endpoint["host"] or "-"
        path_value = endpoint["path"] + (f"?{endpoint['query']}" if endpoint["query"] else "")
        lines.append(f"| `{endpoint['method']}` | `{host}` | `{path_value}` | {sources} |")
    lines.append("")
    lines.append("## GraphQL Operations")
    lines.append("")
    if data["graphql_operations"]:
        for op in data["graphql_operations"]:
            lines.append(f"- `{op['kind']} {op['name']}`: {', '.join(op['sources'])}")
    else:
        lines.append("None detected.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_summary(data: dict):
    print(f"=== Endpoint Inventory: {data['root']} ===")
    print(f"Endpoints: {len(data['endpoints'])}")
    print(f"GraphQL operations: {len(data['graphql_operations'])}")
    for endpoint in data["endpoints"][:40]:
        print(f"  {endpoint['method']:7} {endpoint['url']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Dump directory or file to scan")
    parser.add_argument("--base-url", help="Base URL for resolving relative paths")
    parser.add_argument("--json-out", help="Write endpoint inventory JSON")
    parser.add_argument("--markdown-out", help="Write endpoint inventory Markdown")
    args = parser.parse_args()

    root = Path(args.path)
    if not root.exists():
        print(f"error: path not found: {root}", file=sys.stderr)
        return 1

    data = extract(root, args.base_url)
    print_summary(data)
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    if args.markdown_out:
        write_markdown(data, Path(args.markdown_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
