#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from common import parse_frontmatter, write_frontmatter


def main() -> int:
    parser = argparse.ArgumentParser(description="Mark a documentation item as superseded.")
    parser.add_argument("doc_path")
    parser.add_argument("--by", required=True, help="Replacement document id")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    path = Path(args.doc_path)
    if not path.exists():
        print(f"ERROR: document not found: {path}", file=sys.stderr)
        return 2
    data, body = parse_frontmatter(path)
    if not data:
        print(f"ERROR: document has no frontmatter: {path}", file=sys.stderr)
        return 2
    data["status"] = "superseded"
    data["superseded_by"] = args.by
    if args.reason:
        body = body.rstrip() + f"\n\n## Superseded\n\n{args.reason}\n"
    write_frontmatter(path, data, body)
    print(f"DOC_SUPERSEDED:{path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
