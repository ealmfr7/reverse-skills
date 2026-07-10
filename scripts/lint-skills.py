#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DIRECT_SCRIPT_RE = re.compile(
    r"\b(?:python3|bash)\s+(?:[A-Za-z0-9_.-]+/)?scripts/[A-Za-z0-9_.-]+\.(?:py|sh)\b"
)


def parse_frontmatter(text: str) -> tuple[dict[str, str], int]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}, 0
    data: dict[str, str] = {}
    for index, line in enumerate(lines[1:], start=1):
        if line == "---":
            return data, index + 1
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data, 0


def lint_doc(path: Path) -> list[str]:
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    frontmatter, body_start = parse_frontmatter(text)
    errors: list[str] = []

    if not frontmatter or body_start == 0:
        errors.append(f"{rel}: missing frontmatter")
        return errors

    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    if name != path.parent.name:
        errors.append(f"{rel}: name must match directory ({path.parent.name})")
    if not NAME_RE.match(name):
        errors.append(f"{rel}: invalid skill name {name!r}")
    if not description:
        errors.append(f"{rel}: missing description")
    if len("\n".join(text.splitlines()[:body_start])) > 1024:
        errors.append(f"{rel}: frontmatter exceeds 1024 characters")

    for line_no, line in enumerate(text.splitlines(), start=1):
        if "/home/" in line or ".codex/plugins/cache" in line:
            errors.append(f"{rel}:{line_no}: avoid absolute/cache paths")
        if DIRECT_SCRIPT_RE.search(line):
            errors.append(f"{rel}:{line_no}: use reverse-skill instead of direct script commands")

    return errors


def main() -> int:
    errors = []
    for path in sorted(ROOT.glob("*/SKILL.md")):
        errors.extend(lint_doc(path))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("SKILL_LINT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
