#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from common import VALID_STATUSES, VALID_TYPES, iter_docs


REQUIRED = {"id", "type", "status", "title", "created_at"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate reverse documentation frontmatter.")
    parser.add_argument("docs_dir")
    args = parser.parse_args()

    docs_dir = Path(args.docs_dir)
    errors = []
    seen = set()
    for path, data, _body in iter_docs(docs_dir):
        missing = sorted(REQUIRED - set(data))
        if missing:
            errors.append(f"{path}: missing {', '.join(missing)}")
        if data.get("type") not in VALID_TYPES:
            errors.append(f"{path}: invalid type {data.get('type')}")
        if data.get("status") not in VALID_STATUSES:
            errors.append(f"{path}: invalid status {data.get('status')}")
        doc_id = data.get("id")
        if doc_id in seen:
            errors.append(f"{path}: duplicate id {doc_id}")
        seen.add(doc_id)

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"DOCS_OK:{len(seen)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
