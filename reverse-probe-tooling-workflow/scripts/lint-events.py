#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

from common import validate_event


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate standardized probe events JSONL.")
    parser.add_argument("events_jsonl", type=Path)
    args = parser.parse_args()

    errors = []
    count = 0
    with args.events_jsonl.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            count += 1
            try:
                row = json.loads(text)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_no}: invalid JSON: {exc}")
                continue
            if not isinstance(row, dict):
                errors.append(f"line {line_no}: expected object")
                continue
            errors.extend(validate_event(row, line_no=line_no))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"EVENTS_OK:{count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
