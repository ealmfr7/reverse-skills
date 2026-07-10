from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EVENT_TYPES = {"event", "status", "blob", "error"}
REQUIRED_EVENT_FIELDS = {"schema", "type", "event", "ts", "source", "data"}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip().lower()).strip("-")
    return slug or "probe"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                row = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: expected object")
            rows.append(row)
    return rows


def validate_event(row: dict[str, Any], *, line_no: int) -> list[str]:
    errors = []
    missing = sorted(REQUIRED_EVENT_FIELDS - set(row))
    if missing:
        errors.append(f"line {line_no}: missing {', '.join(missing)}")
    if row.get("schema") != 1:
        errors.append(f"line {line_no}: schema must be 1")
    if row.get("type") not in EVENT_TYPES:
        errors.append(f"line {line_no}: invalid type {row.get('type')!r}")
    if not isinstance(row.get("event"), str) or not row.get("event"):
        errors.append(f"line {line_no}: event must be a non-empty string")
    if not isinstance(row.get("source"), str) or not row.get("source"):
        errors.append(f"line {line_no}: source must be a non-empty string")
    if not isinstance(row.get("data"), dict):
        errors.append(f"line {line_no}: data must be an object")
    if not isinstance(row.get("ts"), int | float):
        errors.append(f"line {line_no}: ts must be numeric")
    return errors


def next_run_dir(runs_root: Path, name: str) -> Path:
    runs_root.mkdir(parents=True, exist_ok=True)
    numbers = []
    for path in runs_root.iterdir():
        if path.is_dir() and re.match(r"^\d{4}-", path.name):
            numbers.append(int(path.name[:4]))
    return runs_root / f"{max(numbers, default=0) + 1:04d}-{slugify(name)}"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
