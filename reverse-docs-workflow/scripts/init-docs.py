#!/usr/bin/env python3
import argparse
from pathlib import Path

from common import DOC_SUBDIRS, now_date


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a structured documentation workspace.")
    parser.add_argument("--root", default=".", help="Workspace root that will contain docs/")
    parser.add_argument("--project", required=True, help="Project or investigation name")
    args = parser.parse_args()

    docs_dir = Path(args.root) / "docs"
    for subdir in DOC_SUBDIRS:
        (docs_dir / subdir).mkdir(parents=True, exist_ok=True)

    index = docs_dir / "INDEX.md"
    if not index.exists():
        index.write_text(
            f"# {args.project}\n\n"
            f"Created: {now_date()}\n\n"
            "## Active Findings\n\n"
            "## Decisions\n\n"
            "## Reports\n",
            encoding="utf-8",
        )
    (docs_dir / "glossary.md").write_text("# Glossary\n", encoding="utf-8")
    (docs_dir / "timeline.md").write_text(f"# Timeline\n\n- {now_date()} docs initialized\n", encoding="utf-8")

    print(f"DOCS_CREATED:{docs_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
