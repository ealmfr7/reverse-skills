from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


DOC_SUBDIRS = [
    "findings",
    "hypotheses",
    "experiments",
    "decisions",
    "runbooks",
    "reports/final",
    "reports/interim",
    "archive/superseded",
]

DOC_PREFIX = {
    "finding": "F",
    "hypothesis": "H",
    "experiment": "R",
    "decision": "D",
    "runbook": "RB",
    "report": "REP",
}

DOC_DIR = {
    "finding": "findings",
    "hypothesis": "hypotheses",
    "experiment": "experiments",
    "decision": "decisions",
    "runbook": "runbooks",
    "report": "reports/interim",
}

VALID_TYPES = set(DOC_PREFIX)
VALID_STATUSES = {"draft", "active", "superseded", "rejected", "final"}


def now_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "untitled"


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end].splitlines()
    body = text[end + 5 :]
    data = {}
    current_key = None
    for line in raw:
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key:
            data.setdefault(current_key, []).append(line[4:].strip().strip('"'))
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        if value == "[]":
            data[key] = []
        elif value in {"null", "~"}:
            data[key] = None
        elif value:
            data[key] = value.strip('"')
        else:
            data[key] = []
    return data, body


def write_frontmatter(path: Path, data: dict, body: str) -> None:
    lines = ["---"]
    for key, value in data.items():
        if isinstance(value, list):
            if value:
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {json.dumps(str(item))}")
            else:
                lines.append(f"{key}: []")
        elif value is None:
            lines.append(f"{key}: null")
        else:
            lines.append(f"{key}: {yaml_scalar(str(value))}")
    lines.append("---")
    path.write_text("\n".join(lines) + "\n\n" + body.lstrip(), encoding="utf-8")


def yaml_scalar(value: str) -> str:
    if re.match(r"^[A-Za-z0-9_.:/ -]+$", value) and value.strip() == value and value:
        return value
    return json.dumps(value)


def next_id(docs_dir: Path, doc_type: str) -> str:
    prefix = DOC_PREFIX[doc_type]
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d{{4}})-")
    numbers = []
    for path in docs_dir.rglob("*.md"):
        match = pattern.match(path.name)
        if match:
            numbers.append(int(match.group(1)))
            continue
        data, _ = parse_frontmatter(path)
        doc_id = str(data.get("id", ""))
        match = re.match(rf"^{re.escape(prefix)}-(\d{{4}})$", doc_id)
        if match:
            numbers.append(int(match.group(1)))
    return f"{prefix}-{max(numbers, default=0) + 1:04d}"


def doc_path(docs_dir: Path, doc_type: str, doc_id: str, title: str) -> Path:
    return docs_dir / DOC_DIR[doc_type] / f"{doc_id}-{slugify(title)}.md"


def iter_docs(docs_dir: Path):
    for path in sorted(docs_dir.rglob("*.md")):
        if path.name == "INDEX.md":
            continue
        data, body = parse_frontmatter(path)
        if data:
            yield path, data, body
