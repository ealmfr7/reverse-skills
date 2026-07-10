#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected JSON object")
    return data


def bullet_list(values: list[Any]) -> list[str]:
    if not values:
        return ["- None recorded."]
    return [f"- `{value}`" for value in values]


def render(summary: dict[str, Any], verification: dict[str, Any], comparison: dict[str, Any]) -> str:
    backend = verification.get("policy", {}).get("backendStrict", {})
    checks = verification.get("checks", {})
    differences = comparison.get("differences", {})
    lines = [
        "# Android Attestation Report",
        "",
        "## Summary",
        "",
        f"- Artifacts present: {', '.join(summary.get('present', [])) or 'none'}",
        f"- backendStrict: `{backend.get('passed')}`",
        "- Key possession and backend trust are separate claims.",
        "- Exact root match and SPKI root match must be evaluated separately.",
        "",
        "## Signals",
        "",
        *bullet_list(summary.get("signals", [])),
        "",
        "## Checks",
        "",
    ]
    if checks:
        for key in sorted(checks):
            lines.append(f"- `{key}`: `{checks[key]}`")
    else:
        lines.append("- None recorded.")
    lines.extend(["", "## backendStrict Reasons", ""])
    lines.extend(bullet_list(backend.get("reasons", [])))
    lines.extend(["", "## Comparison Differences", ""])
    if differences:
        for key, value in sorted(differences.items()):
            lines.append(f"- `{key}`: left=`{value.get('left')}` right=`{value.get('right')}`")
    else:
        lines.append("- None recorded.")
    lines.extend(["", "## Next Steps", ""])
    lines.extend(bullet_list(list(summary.get("nextSteps", [])) + list(comparison.get("nextSteps", []))))
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a Markdown report from Android attestation lab JSON artifacts.")
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--verification", type=Path)
    parser.add_argument("--comparison", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    text = render(read_json(args.summary), read_json(args.verification), read_json(args.comparison))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"WROTE {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
