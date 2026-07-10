#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "TOOLS.md"


def skill_docs() -> list[Path]:
    return sorted(ROOT.glob("*/SKILL.md"))


def tools_for(skill_dir: Path) -> list[str]:
    scripts = skill_dir / "scripts"
    if not scripts.exists():
        return []
    tools = []
    for path in sorted(item for item in scripts.rglob("*") if item.is_file()):
        if "__pycache__" in path.parts or path.suffix == ".pyc" or path.name.startswith("."):
            continue
        if path.name == "common.py":
            continue
        rel = path.relative_to(scripts)
        if path.suffix in {".py", ".sh", ".js"}:
            tools.append(str(rel.with_suffix("")))
        else:
            tools.append(str(rel))
    return tools


def render() -> str:
    lines = [
        "# Reverse Skill Tool Index",
        "",
        "Generated from local skill `scripts/` directories. Run:",
        "",
        "```bash",
        "python3 scripts/generate-tools-index.py --out TOOLS.md",
        "```",
        "",
    ]
    for doc in skill_docs():
        skill = doc.parent.name
        tools = tools_for(doc.parent)
        if not tools:
            continue
        lines.extend(
            [
                f"## {skill}",
                "",
                "| Tool | Command |",
                "|---|---|",
            ]
        )
        for tool in tools:
            lines.append(f"| `{tool}` | `reverse-skill {skill} {tool}` |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    content = render()
    if args.check:
        if not args.out.exists():
            print(f"TOOLS_INDEX_MISSING:{args.out}", file=sys.stderr)
            return 1
        current = args.out.read_text(encoding="utf-8")
        if current != content:
            print(f"TOOLS_INDEX_STALE:{args.out}", file=sys.stderr)
            return 1
        print(f"TOOLS_INDEX_OK:{args.out}")
        return 0

    args.out.write_text(content, encoding="utf-8")
    print(f"TOOLS_INDEX_WRITTEN:{args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
