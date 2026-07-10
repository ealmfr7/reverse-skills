#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict
from pathlib import Path


def clean_hex(value):
    return "".join(str(value or "").replace(":", "").split()).lower()


def cluster(payloads, prefix_bytes):
    groups = defaultdict(list)
    chars = prefix_bytes * 2
    for item in payloads:
        payload = clean_hex(item.get("hex") or item.get("payload_hex") or "")
        if not payload:
            continue
        key = f"len={len(payload) // 2} prefix={payload[:chars]}"
        groups[key].append(payload)
    return {
        "clusters": [
            {
                "key": key,
                "count": len(values),
                "examples": values[:10],
            }
            for key, values in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0]))
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="Cluster UDP payload hex blobs by length and prefix.")
    parser.add_argument("payloads_json", help="JSON with a payloads array")
    parser.add_argument("--prefix-bytes", type=int, default=4)
    parser.add_argument("--json-out")
    args = parser.parse_args()

    data = json.loads(Path(args.payloads_json).read_text(encoding="utf-8", errors="replace"))
    result = cluster(data.get("payloads", []), args.prefix_bytes)
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.json_out:
        Path(args.json_out).write_text(text + "\n", encoding="utf-8")
    print(f"CLUSTERS:{len(result['clusters'])}")
    for item in result["clusters"][:20]:
        print(f"{item['key']} count={item['count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
