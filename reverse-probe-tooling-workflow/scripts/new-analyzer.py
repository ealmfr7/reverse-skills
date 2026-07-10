#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from common import slugify


ANALYZER_TEMPLATE = '''#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def iter_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def analyze(run: Path, out: Path) -> dict[str, Any]:
    events = iter_jsonl(run / "events.jsonl")
    counts = Counter(str(row.get("event", "unknown")) for row in events)
    result = {
        "run": str(run),
        "eventCount": len(events),
        "events": [{"event": key, "count": counts[key]} for key in sorted(counts)],
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze a standardized reverse probe run.")
    parser.add_argument("run", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    out = args.out or args.run / "analysis" / "__NAME__"
    result = analyze(args.run, out)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"ANALYSIS_WRITTEN:{out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a standardized Python analyzer scaffold.")
    parser.add_argument("name")
    parser.add_argument("--out", type=Path, default=Path("probes/python"))
    args = parser.parse_args()

    name = slugify(args.name)
    path = args.out / f"{name}.py"
    if path.exists():
        print(f"ERROR: analyzer already exists: {path}", file=sys.stderr)
        return 1
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(ANALYZER_TEMPLATE.replace("__NAME__", name), encoding="utf-8")
    path.chmod(0o755)
    print(f"ANALYZER_CREATED:{path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
