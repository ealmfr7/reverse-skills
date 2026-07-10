#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path

from common import VALID_PHASES, now_iso


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip().lower()).strip("-")
    return slug or "run"


def next_run_number(runs_dir: Path) -> int:
    existing = []
    if runs_dir.exists():
        for path in runs_dir.iterdir():
            if path.is_dir() and re.match(r"^\d{4}-", path.name):
                existing.append(int(path.name[:4]))
    return max(existing, default=0) + 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a numbered experiment run directory inside a case.")
    parser.add_argument("case_dir")
    parser.add_argument("name", help="Short run name, e.g. dynamic-login-hook")
    parser.add_argument("--phase", required=True, choices=sorted(VALID_PHASES))
    parser.add_argument("--command", default="", help="Command or procedure used for the run")
    args = parser.parse_args()

    case_dir = Path(args.case_dir)
    if not (case_dir / "case.yaml").exists():
        print(f"ERROR: not a case directory: {case_dir}", file=sys.stderr)
        return 2

    runs_dir = case_dir / "runs"
    number = next_run_number(runs_dir)
    run_dir = runs_dir / f"{number:04d}-{args.phase}-{slugify(args.name)}"
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "command.md").write_text(
        f"# Command\n\nCreated: {now_iso()}\n\nPhase: {args.phase}\n\n```bash\n{args.command}\n```\n",
        encoding="utf-8",
    )
    (run_dir / "observations.md").write_text("# Observations\n", encoding="utf-8")
    (run_dir / "outputs").mkdir()

    print(f"RUN_CREATED:{run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
