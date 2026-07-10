#!/usr/bin/env python3
import argparse
from collections import Counter
from pathlib import Path

from common import read_jsonl, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Index a standardized probe run.")
    parser.add_argument("run", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    meta_path = args.run / "meta.json"
    meta = {}
    if meta_path.exists():
        import json

        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    events = read_jsonl(args.run / "events.jsonl")
    by_type = Counter(str(row.get("type", "unknown")) for row in events)
    by_event = Counter(str(row.get("event", "unknown")) for row in events)
    blobs = sorted(str(path.relative_to(args.run)) for path in (args.run / "blobs").rglob("*") if path.is_file())
    result = {
        "schema": 1,
        "run": str(args.run),
        "caseId": meta.get("caseId", ""),
        "probe": meta.get("probe", ""),
        "eventCount": len(events),
        "types": [{"type": key, "count": by_type[key]} for key in sorted(by_type)],
        "events": [{"event": key, "count": by_event[key]} for key in sorted(by_event)],
        "blobs": blobs,
    }
    out = args.json_out or args.run / "run-index.json"
    write_json(out, result)
    print(f"RUN_INDEXED:{out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
