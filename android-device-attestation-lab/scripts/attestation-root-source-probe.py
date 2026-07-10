#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_MAX_FILE_BYTES = 25 * 1024 * 1024


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected JSON object")
    return data


def needles_from_root_diff(root_diff: dict[str, Any]) -> dict[str, str]:
    local = root_diff.get("localRoot", {})
    if not isinstance(local, dict):
        local = {}
    needles = {}
    if local.get("sha256"):
        needles["localRootSha256"] = str(local["sha256"])
    if local.get("spkiSha256"):
        needles["localRootSpkiSha256"] = str(local["spkiSha256"])
    return needles


def iter_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(item for item in path.rglob("*") if item.is_file())
    return sorted(files)


def scan_local(paths: list[Path], needles: dict[str, str], max_file_bytes: int) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    encoded_needles = {name: value.encode("utf-8") for name, value in needles.items() if value}
    for path in iter_files(paths):
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > max_file_bytes:
            continue
        try:
            blob = path.read_bytes()
        except OSError:
            continue
        for name, needle in encoded_needles.items():
            offset = blob.find(needle)
            if offset >= 0:
                hits.append(
                    {
                        "path": str(path),
                        "needle": name,
                        "offset": offset,
                        "fileSize": size,
                    }
                )
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description="Search bounded local dumps/images for attestation root certificate source markers.")
    parser.add_argument("--root-diff", type=Path, required=True)
    parser.add_argument("--local-scan-dir", type=Path, action="append", default=[])
    parser.add_argument("--max-file-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    root_diff = read_json(args.root_diff)
    needles = needles_from_root_diff(root_diff)
    hits = scan_local(args.local_scan_dir, needles, args.max_file_bytes)
    output = {
        "mode": "local",
        "policy": "metadata-only bounded local scan; matched file contents are not copied into the report",
        "needles": needles,
        "scanRoots": [str(path) for path in args.local_scan_dir],
        "hits": hits,
    }
    text = json.dumps(output, indent=2, sort_keys=True) + "\n"
    print(text, end="")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
