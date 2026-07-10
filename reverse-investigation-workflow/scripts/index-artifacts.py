#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from common import read_case_id, sha256


def artifact_entries(case_dir: Path):
    logged = {}
    log_path = case_dir / "artifacts" / "artifact-log.jsonl"
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            logged[item["path"]] = item

    entries = []
    for path in sorted(case_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = str(path.relative_to(case_dir))
        if rel in {"case.yaml", "README.md", "timeline.md"} or rel.startswith("notes/"):
            continue
        item = dict(logged.get(rel, {}))
        item.setdefault("path", rel)
        item.setdefault("kind", "unknown")
        item.setdefault("phase", "unknown")
        item.setdefault("size", path.stat().st_size)
        if path.is_file() and path.stat().st_size < 100 * 1024 * 1024:
            item.setdefault("sha256", sha256(path))
        entries.append(item)
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an evidence index for a reverse engineering case.")
    parser.add_argument("case_dir")
    parser.add_argument("--json-out")
    args = parser.parse_args()

    case_dir = Path(args.case_dir)
    result = {
        "case_id": read_case_id(case_dir),
        "artifacts": artifact_entries(case_dir),
    }
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    print(f"ARTIFACTS:{len(result['artifacts'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
