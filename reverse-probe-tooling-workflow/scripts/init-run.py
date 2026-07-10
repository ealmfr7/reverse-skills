#!/usr/bin/env python3
import argparse
from pathlib import Path

from common import next_run_dir, now_iso, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a standardized probe run directory.")
    parser.add_argument("runs_root", type=Path)
    parser.add_argument("name")
    parser.add_argument("--case-id", default="")
    parser.add_argument("--probe", default="")
    parser.add_argument("--command", default="")
    args = parser.parse_args()

    run_dir = next_run_dir(args.runs_root, args.name)
    run_dir.mkdir(parents=True, exist_ok=False)
    for subdir in ("analysis", "blobs", "logs"):
        (run_dir / subdir).mkdir()
    (run_dir / "events.jsonl").write_text("", encoding="utf-8")
    (run_dir / "stdout.log").write_text("", encoding="utf-8")
    (run_dir / "stderr.log").write_text("", encoding="utf-8")
    write_json(
        run_dir / "meta.json",
        {
            "name": args.name,
            "caseId": args.case_id,
            "probe": args.probe,
            "command": args.command,
            "createdAt": now_iso(),
            "schema": 1,
        },
    )
    print(f"RUN_CREATED:{run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
