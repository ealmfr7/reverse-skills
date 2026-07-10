#!/usr/bin/env python3
"""Scan JavaScript/TypeScript/HTML assets for web API reverse-engineering signals."""

from __future__ import annotations

import argparse
import collections
import os
import re
import sys
from pathlib import Path


TEXT_EXTS = {
    ".js",
    ".mjs",
    ".cjs",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
    ".htm",
    ".json",
    ".map",
}

URL_RE = re.compile(r"https?://[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+")
PATH_RE = re.compile(
    r"""(?P<quote>["'`])(?P<path>/(?:api|v\d+|graphql|rest|auth|oauth|session|token|users?|account|profile|orders?|checkout|payment|search|upload|download|files?|messages?|notifications?)[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%{}-]*)"""
)
FETCH_RE = re.compile(r"\b(fetch|axios\.(?:get|post|put|patch|delete|request)|\w+\.request)\s*\(")
HEADER_RE = re.compile(
    r"""(?P<quote>["'`])(?P<header>authorization|x-csrf-token|x-xsrf-token|x-api-key|api-key|x-requested-with|x-signature|x-timestamp|x-nonce|cookie|set-cookie)(?P=quote)""",
    re.IGNORECASE,
)
GRAPHQL_RE = re.compile(r"\b(query|mutation|subscription)\s+([A-Za-z_][A-Za-z0-9_]*)")
WS_RE = re.compile(r"\b(WebSocket|EventSource)\s*\(|wss?://")
FRAMEWORKS = {
    "React": re.compile(r"react(?:-dom)?|__REACT_DEVTOOLS_GLOBAL_HOOK__", re.I),
    "Next.js": re.compile(r"__NEXT_DATA__|/_next/|next/router", re.I),
    "Vue": re.compile(r"\bVue\b|createApp\(|__VUE__", re.I),
    "Angular": re.compile(r"@angular|ng-version|zone\.js", re.I),
    "Svelte": re.compile(r"svelte", re.I),
    "Apollo GraphQL": re.compile(r"ApolloClient|apollo-link|__typename", re.I),
    "Axios": re.compile(r"\baxios\b", re.I),
}


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


def add_limited(counter: collections.Counter, values, limit=5000):
    for value in values:
        if len(counter) >= limit and value not in counter:
            continue
        counter[value] += 1


def scan(root: Path) -> int:
    files = list(iter_files(root))
    urls = collections.Counter()
    paths = collections.Counter()
    fetch_calls = collections.Counter()
    headers = collections.Counter()
    graphql_ops = collections.Counter()
    ws_files = []
    framework_hits = collections.Counter()

    for path in files:
        text = read_text(path)
        if not text:
            continue
        rel = str(path.relative_to(root)) if root.is_dir() else path.name

        add_limited(urls, URL_RE.findall(text))
        add_limited(paths, (m.group("path") for m in PATH_RE.finditer(text)))
        fetch_count = len(FETCH_RE.findall(text))
        if fetch_count:
            fetch_calls[rel] += fetch_count
        add_limited(headers, (m.group("header").lower() for m in HEADER_RE.finditer(text)))
        add_limited(graphql_ops, (f"{m.group(1)} {m.group(2)}" for m in GRAPHQL_RE.finditer(text)))
        if WS_RE.search(text):
            ws_files.append(rel)
        for name, pattern in FRAMEWORKS.items():
            if pattern.search(text):
                framework_hits[name] += 1

    print(f"=== JS/API Signal Scan: {root} ===")
    print(f"Files scanned: {len(files)}")
    print()

    print("Framework/library hints:")
    if framework_hits:
        for name, count in framework_hits.most_common():
            print(f"  {count:4}  {name}")
    else:
        print("  none detected")
    print()

    print("Absolute URLs:")
    if urls:
        for url, count in urls.most_common(40):
            print(f"  {count:4}  {url}")
    else:
        print("  none detected")
    print()

    print("Endpoint-shaped paths:")
    if paths:
        for path, count in paths.most_common(80):
            print(f"  {count:4}  {path}")
    else:
        print("  none detected")
    print()

    print("Fetch/axios/request call density:")
    if fetch_calls:
        for file_name, count in fetch_calls.most_common(30):
            print(f"  {count:4}  {file_name}")
    else:
        print("  none detected")
    print()

    print("Auth/signing/header names:")
    if headers:
        for header, count in headers.most_common():
            print(f"  {count:4}  {header}")
    else:
        print("  none detected")
    print()

    print("GraphQL operation candidates:")
    if graphql_ops:
        for op, count in graphql_ops.most_common(60):
            print(f"  {count:4}  {op}")
    else:
        print("  none detected")
    print()

    print("WebSocket/SSE files:")
    if ws_files:
        for file_name in ws_files[:60]:
            print(f"  {file_name}")
    else:
        print("  none detected")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="JavaScript bundle, source map, HTML file, or directory")
    args = parser.parse_args()
    root = Path(args.path)
    if not root.exists():
        print(f"error: path not found: {root}", file=sys.stderr)
        return 1
    return scan(root)


if __name__ == "__main__":
    raise SystemExit(main())
