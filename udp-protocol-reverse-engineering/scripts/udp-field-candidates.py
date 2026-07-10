#!/usr/bin/env python3
import argparse
import json
import math
from collections import Counter
from pathlib import Path


def clean_hex(value):
    return "".join(str(value or "").replace(":", "").split()).lower()


def to_bytes(payload):
    return bytes.fromhex(clean_hex(payload))


def entropy(values):
    if not values:
        return 0.0
    counts = Counter(values)
    total = len(values)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def load_payloads(path):
    data = json.loads(Path(path).read_text(encoding="utf-8", errors="replace"))
    return [to_bytes(item.get("hex") or item.get("payload_hex") or "") for item in data.get("payloads", []) if item.get("hex") or item.get("payload_hex")]


def integer_at(payload, offset, width, endian):
    if offset + width > len(payload):
        return None
    return int.from_bytes(payload[offset : offset + width], endian)


def strictly_increasing(values):
    return len(values) >= 3 and all(values[i] < values[i + 1] for i in range(len(values) - 1))


def analyze(payloads):
    if not payloads:
        return {"payload_count": 0, "constant_bytes": [], "byte_entropy": [], "monotonic_counters": []}
    min_len = min(len(p) for p in payloads)

    constant_bytes = []
    byte_entropy = []
    for offset in range(min_len):
        column = [p[offset] for p in payloads]
        unique = sorted(set(column))
        if len(unique) == 1:
            constant_bytes.append({"offset": offset, "hex": f"{unique[0]:02x}"})
        byte_entropy.append({"offset": offset, "entropy": round(entropy(column), 4), "unique_values": len(unique)})

    counters = []
    for width in (1, 2, 4, 8):
        if width > min_len:
            continue
        for offset in range(0, min_len - width + 1):
            for endian in ("big", "little"):
                values = [integer_at(p, offset, width, endian) for p in payloads]
                if None not in values and strictly_increasing(values):
                    counters.append(
                        {
                            "offset": offset,
                            "width": width,
                            "endian": endian,
                            "values": values[:10],
                        }
                    )

    return {
        "payload_count": len(payloads),
        "min_length": min_len,
        "constant_bytes": constant_bytes,
        "byte_entropy": byte_entropy,
        "monotonic_counters": counters,
    }


def main():
    parser = argparse.ArgumentParser(description="Infer simple UDP binary field candidates from aligned payload samples.")
    parser.add_argument("payloads_json", help="JSON with a payloads array")
    parser.add_argument("--json-out")
    args = parser.parse_args()

    result = analyze(load_payloads(args.payloads_json))
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.json_out:
        Path(args.json_out).write_text(text + "\n", encoding="utf-8")
    print(f"PAYLOADS:{result['payload_count']}")
    print(f"CONSTANT_BYTES:{len(result['constant_bytes'])}")
    print(f"MONOTONIC_COUNTERS:{len(result['monotonic_counters'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
