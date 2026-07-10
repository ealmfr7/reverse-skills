#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import now_iso


TEMPLATES = [
    (
        "physical-attestation-baseline",
        "Collect known-good physical-device environment and attestation evidence with android-device-attestation-lab.",
    ),
    (
        "vmos-attestation-compare",
        "Collect comparison environment evidence and compare against the physical baseline.",
    ),
    (
        "frida-attestation-observation",
        "Run bounded observational Frida traces for KeyStore/keymaster timing and evidence.",
    ),
]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip().lower()).strip("-")
    return slug or "run"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create standard Android attestation investigation run folders.")
    parser.add_argument("case_dir")
    args = parser.parse_args()

    case_dir = Path(args.case_dir)
    if not (case_dir / "case.yaml").exists():
        print(f"ERROR: not a case directory: {case_dir}", file=sys.stderr)
        return 2

    created = []
    runs_dir = case_dir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    for index, (name, description) in enumerate(TEMPLATES, start=1):
        run_dir = runs_dir / f"{index:04d}-dynamic-{slugify(name)}"
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "outputs").mkdir(exist_ok=True)
        (run_dir / "command.md").write_text(
            "# Command\n\n"
            f"Created: {now_iso()}\n\n"
            "Phase: dynamic\n\n"
            "Skill: android-device-attestation-lab\n\n"
            f"Purpose: {description}\n\n"
            "```bash\n"
            "# Fill in exact commands for this lab run.\n"
            "```\n",
            encoding="utf-8",
        )
        (run_dir / "observations.md").write_text("# Observations\n", encoding="utf-8")
        created.append(str(run_dir))

    print("ATTESTATION_RUNS_CREATED:" + ",".join(created))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
