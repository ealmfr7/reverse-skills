#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from common import CASE_SUBDIRS, VALID_AUTH, VALID_PLATFORMS, VALID_STATUSES, now_iso, write_yaml_like


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a structured reverse engineering case directory.")
    parser.add_argument("case_id", help="Stable case id, e.g. 2026-07-10-likee-live")
    parser.add_argument("--root", default=".", help="Workspace root that will contain cases/")
    parser.add_argument("--target", required=True)
    parser.add_argument("--platform", choices=sorted(VALID_PLATFORMS), default="android")
    parser.add_argument("--country", default="unknown")
    parser.add_argument("--authorization", choices=sorted(VALID_AUTH), default="unknown")
    parser.add_argument("--goal", required=True)
    parser.add_argument("--status", choices=sorted(VALID_STATUSES), default="active")
    args = parser.parse_args()

    case_dir = Path(args.root) / "cases" / args.case_id
    if case_dir.exists():
        print(f"ERROR: case already exists: {case_dir}", file=sys.stderr)
        return 1

    for subdir in CASE_SUBDIRS:
        (case_dir / subdir).mkdir(parents=True, exist_ok=True)

    data = {
        "id": args.case_id,
        "target": args.target,
        "platform": args.platform,
        "country": args.country,
        "status": args.status,
        "authorization": args.authorization,
        "goal": args.goal,
        "created_at": now_iso(),
        "skills_used": [],
        "artifact_policy": {
            "secrets_redacted": True,
            "raw_tokens_allowed": False,
        },
    }
    write_yaml_like(case_dir / "case.yaml", data)
    (case_dir / "README.md").write_text(f"# {args.case_id}\n\n{args.goal}\n", encoding="utf-8")
    (case_dir / "timeline.md").write_text(f"# Timeline\n\n- {now_iso()} case created\n", encoding="utf-8")
    (case_dir / "notes" / "hypotheses.md").write_text("# Hypotheses\n", encoding="utf-8")
    (case_dir / "notes" / "findings.md").write_text("# Findings\n", encoding="utf-8")
    (case_dir / "notes" / "unknowns.md").write_text("# Unknowns\n", encoding="utf-8")

    print(f"CASE_CREATED:{case_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
