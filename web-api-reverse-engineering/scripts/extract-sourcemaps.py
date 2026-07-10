#!/usr/bin/env python3
"""Extract embedded sources from JavaScript source map files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


def iter_maps(root: Path):
    if root.is_file() and root.name.endswith(".map"):
        yield root
        return
    for path in root.rglob("*.map"):
        if path.is_file():
            yield path


def safe_parts(source: str) -> list[str]:
    source = re.sub(r"^[a-zA-Z]+://", "", source)
    source = source.replace("webpack://", "").replace("webpack:/", "")
    parts = []
    for part in source.replace("\\", "/").split("/"):
        if part in {"", ".", ".."}:
            continue
        clean = re.sub(r"[^A-Za-z0-9._-]+", "_", part)
        if clean:
            parts.append(clean)
    return parts or ["source.txt"]


def unique_path(base: Path, parts: list[str]) -> Path:
    candidate = base.joinpath(*parts)
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    parent = candidate.parent
    for i in range(2, 10_000):
        alt = parent / f"{stem}-{i}{suffix}"
        if not alt.exists():
            return alt
    raise RuntimeError(f"could not allocate unique path for {candidate}")


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def extract(root: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    maps = []
    extracted = 0
    for map_path in iter_maps(root):
        try:
            data = json.loads(map_path.read_text(encoding="utf-8", errors="replace"))
        except json.JSONDecodeError:
            maps.append({"map": str(map_path), "error": "invalid-json", "sources_extracted": 0})
            continue
        source_root = str(data.get("sourceRoot") or "").strip("/")
        sources = data.get("sources") or []
        contents = data.get("sourcesContent") or []
        item = {"map": str(map_path), "sources": [], "sources_extracted": 0}
        for index, source in enumerate(sources):
            if index >= len(contents) or contents[index] is None:
                item["sources"].append({"source": source, "embedded": False})
                continue
            content = str(contents[index])
            parts = safe_parts(source)
            if source_root:
                parts = safe_parts(source_root) + parts
            dest = unique_path(out, parts)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
            rel = dest.relative_to(out).as_posix()
            item["sources"].append({"source": source, "embedded": True, "file": rel, "sha256": sha256(content)})
            item["sources_extracted"] += 1
            extracted += 1
        maps.append(item)
    return {"root": str(root), "out": str(out), "maps": maps, "extracted_sources": extracted}


def print_summary(data: dict):
    print(f"=== Source Map Extraction: {data['root']} ===")
    print(f"Maps: {len(data['maps'])}")
    print(f"Extracted sources: {data['extracted_sources']}")
    for item in data["maps"]:
        print(f"  {item['map']}: {item.get('sources_extracted', 0)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Dump directory or .map file")
    parser.add_argument("--out", required=True, help="Output directory for extracted sources")
    parser.add_argument("--json-out", help="Write extraction manifest JSON")
    args = parser.parse_args()
    root = Path(args.path)
    if not root.exists():
        print(f"error: path not found: {root}", file=sys.stderr)
        return 1
    data = extract(root, Path(args.out))
    print_summary(data)
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
