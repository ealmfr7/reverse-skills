#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

from common import KIND_DIR, VALID_PHASES, copy_artifact, now_iso, sha256


def main() -> int:
    parser = argparse.ArgumentParser(description="Copy an artifact into a case and append metadata.")
    parser.add_argument("case_dir")
    parser.add_argument("source")
    parser.add_argument("--kind", required=True, choices=sorted(KIND_DIR))
    parser.add_argument("--phase", required=True, choices=sorted(VALID_PHASES))
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    case_dir = Path(args.case_dir)
    src = Path(args.source)
    if not (case_dir / "case.yaml").exists():
        print(f"ERROR: not a case directory: {case_dir}", file=sys.stderr)
        return 2
    if not src.exists():
        print(f"ERROR: source not found: {src}", file=sys.stderr)
        return 2

    dst = copy_artifact(src, case_dir / KIND_DIR[args.kind])
    meta = {
        "added_at": now_iso(),
        "kind": args.kind,
        "phase": args.phase,
        "source": str(src),
        "path": str(dst.relative_to(case_dir)),
        "note": args.note,
    }
    if dst.is_file():
        meta["sha256"] = sha256(dst)
        meta["size"] = dst.stat().st_size

    meta_path = case_dir / "artifacts" / "artifact-log.jsonl"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    with meta_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(meta, sort_keys=True) + "\n")

    print(f"ARTIFACT_ADDED:{dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
