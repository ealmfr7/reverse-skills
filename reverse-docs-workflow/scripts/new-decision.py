#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from common import doc_path, next_id, now_date, write_frontmatter


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a numbered technical decision document.")
    parser.add_argument("docs_dir")
    parser.add_argument("title")
    parser.add_argument("--status", default="active", choices=["draft", "active", "superseded", "rejected", "final"])
    parser.add_argument("--rationale", default="")
    args = parser.parse_args()

    docs_dir = Path(args.docs_dir)
    if not docs_dir.exists():
        print(f"ERROR: docs directory not found: {docs_dir}", file=sys.stderr)
        return 2

    doc_id = next_id(docs_dir, "decision")
    path = doc_path(docs_dir, "decision", doc_id, args.title)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "id": doc_id,
        "type": "decision",
        "status": args.status,
        "title": args.title,
        "created_at": now_date(),
        "supersedes": [],
        "superseded_by": None,
        "evidence": [],
    }
    body = f"# {args.title}\n\n## Decision\n\n## Rationale\n\n{args.rationale}\n\n## Consequences\n"
    write_frontmatter(path, data, body)
    print(f"DECISION_CREATED:{path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
