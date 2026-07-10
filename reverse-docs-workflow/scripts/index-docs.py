#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from common import iter_docs


def main() -> int:
    parser = argparse.ArgumentParser(description="Index reverse engineering documentation by frontmatter.")
    parser.add_argument("docs_dir")
    parser.add_argument("--json-out")
    args = parser.parse_args()

    docs_dir = Path(args.docs_dir)
    documents = []
    for path, data, _body in iter_docs(docs_dir):
        item = {
            "id": data.get("id", ""),
            "type": data.get("type", ""),
            "status": data.get("status", ""),
            "title": data.get("title", path.stem),
            "path": str(path.relative_to(docs_dir)),
            "target": data.get("target", ""),
            "case_id": data.get("case_id", ""),
            "evidence": data.get("evidence", []),
            "superseded_by": data.get("superseded_by"),
        }
        documents.append(item)

    result = {"documents": documents}
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")

    md = docs_dir / "INDEX.md"
    lines = ["# Documentation Index", "", "| ID | Type | Status | Title | Path |", "|---|---|---|---|---|"]
    for item in documents:
        lines.append(f"| {item['id']} | {item['type']} | {item['status']} | {item['title']} | {item['path']} |")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"DOCS_INDEXED:{len(documents)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
