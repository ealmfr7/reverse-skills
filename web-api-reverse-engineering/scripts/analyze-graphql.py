#!/usr/bin/env python3
"""Analyze GraphQL signals from dumped assets and HAR summary JSON."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin


TEXT_EXTS = {".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".html", ".json", ".map", ".graphql", ".gql"}
GRAPHQL_RE = re.compile(r"\b(?P<kind>query|mutation|subscription)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)")
PERSISTED_RE = re.compile(r"persistedQuery|sha256Hash|extensions\s*:\s*\{", re.I)
ENDPOINT_RE = re.compile(r"""(?P<quote>["'`])(?P<path>https?://[^"'`\s<>]*graphql[^"'`\s<>]*|/[^"'`\s<>]*graphql[^"'`\s<>]*)(?P=quote)""", re.I)


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


def add_operation(ops: dict[tuple[str, str], dict], kind: str, name: str, source: str, evidence: str | None = None):
    key = (kind, name)
    item = ops.setdefault(key, {"kind": kind, "name": name, "sources": [], "evidence": []})
    if source not in item["sources"]:
        item["sources"].append(source)
    if evidence and evidence not in item["evidence"] and len(item["evidence"]) < 5:
        item["evidence"].append(evidence.strip()[:240])


def analyze_dump(root: Path, base_url: str | None, ops: dict, endpoints: set[str], signals: set[str]):
    for path in iter_files(root):
        text = read_text(path)
        if not text:
            continue
        source = str(path.relative_to(root)) if root.is_dir() else path.name
        for match in GRAPHQL_RE.finditer(text):
            add_operation(ops, match.group("kind"), match.group("name"), source, match.group(0))
        for match in ENDPOINT_RE.finditer(text):
            target = match.group("path")
            endpoints.add(urljoin(base_url.rstrip("/") + "/", target.lstrip("/")) if base_url and target.startswith("/") else target)
        if PERSISTED_RE.search(text):
            signals.add("persisted-query")
        if "__typename" in text:
            signals.add("__typename")


def merge_har(path: Path, ops: dict, endpoints: set[str]):
    data = json.loads(path.read_text(encoding="utf-8"))
    for op in data.get("graphql_operations", []):
        add_operation(ops, op.get("kind", "?"), op.get("name", "?"), str(path), None)
        for endpoint in op.get("endpoints", []):
            parts = endpoint.split(maxsplit=1)
            if len(parts) == 2:
                host_path = parts[1]
                if "://" not in host_path:
                    endpoints.add(f"https://{host_path}")
    for endpoint in data.get("endpoints", []):
        if "graphql" in endpoint.get("path", "").lower():
            endpoints.add(f"https://{endpoint.get('host')}{endpoint.get('path')}")


def analyze(root: Path, base_url: str | None, har_json: Path | None) -> dict:
    ops: dict[tuple[str, str], dict] = {}
    endpoints: set[str] = set()
    signals: set[str] = set()
    analyze_dump(root, base_url, ops, endpoints, signals)
    if har_json:
        merge_har(har_json, ops, endpoints)
    return {
        "root": str(root),
        "endpoint_candidates": sorted(endpoints),
        "operations": sorted(ops.values(), key=lambda item: (item["kind"], item["name"])),
        "signals": sorted(signals),
    }


def write_markdown(data: dict, path: Path):
    lines = ["# GraphQL Analysis", "", "## Endpoint Candidates", ""]
    if data["endpoint_candidates"]:
        for endpoint in data["endpoint_candidates"]:
            lines.append(f"- `{endpoint}`")
    else:
        lines.append("None detected.")
    lines.extend(["", "## Operations", ""])
    if data["operations"]:
        for op in data["operations"]:
            lines.append(f"- `{op['kind']} {op['name']}`: {', '.join(op['sources'])}")
    else:
        lines.append("None detected.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_summary(data: dict):
    print(f"=== GraphQL Analysis: {data['root']} ===")
    print(f"Endpoint candidates: {len(data['endpoint_candidates'])}")
    print(f"Operations: {len(data['operations'])}")
    for op in data["operations"][:60]:
        print(f"  {op['kind']} {op['name']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Dump directory or file to scan")
    parser.add_argument("--base-url", help="Base URL for resolving relative GraphQL paths")
    parser.add_argument("--har-json", help="Sanitized JSON from har-summary.py --json-out")
    parser.add_argument("--json-out", help="Write GraphQL analysis JSON")
    parser.add_argument("--markdown-out", help="Write GraphQL analysis Markdown")
    args = parser.parse_args()
    root = Path(args.path)
    if not root.exists():
        print(f"error: path not found: {root}", file=sys.stderr)
        return 1
    data = analyze(root, args.base_url, Path(args.har_json) if args.har_json else None)
    print_summary(data)
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    if args.markdown_out:
        write_markdown(data, Path(args.markdown_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
