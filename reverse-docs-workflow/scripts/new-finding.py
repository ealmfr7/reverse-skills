#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from common import doc_path, next_id, now_date, write_frontmatter


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a numbered reverse engineering finding document.")
    parser.add_argument("docs_dir")
    parser.add_argument("title")
    parser.add_argument("--target", default="unknown")
    parser.add_argument("--case-id", default="")
    parser.add_argument("--status", default="active", choices=["draft", "active", "superseded", "rejected", "final"])
    parser.add_argument("--evidence", action="append", default=[])
    args = parser.parse_args()

    docs_dir = Path(args.docs_dir)
    if not docs_dir.exists():
        print(f"ERROR: docs directory not found: {docs_dir}", file=sys.stderr)
        return 2

    doc_id = next_id(docs_dir, "finding")
    path = doc_path(docs_dir, "finding", doc_id, args.title)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "id": doc_id,
        "type": "finding",
        "status": args.status,
        "title": args.title,
        "target": args.target,
        "case_id": args.case_id,
        "created_at": now_date(),
        "supersedes": [],
        "superseded_by": None,
        "evidence": args.evidence,
    }
    body = f"# {args.title}\n\n## Claim\n\n## Evidence\n\n## Notes\n"
    write_frontmatter(path, data, body)
    print(f"FINDING_CREATED:{path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
