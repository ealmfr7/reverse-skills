#!/usr/bin/env python3
import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def first(value):
    if isinstance(value, list):
        return value[0] if value else ""
    return value


def clean_hex(value):
    return "".join(str(value or "").replace(":", "").split()).lower()


def packet_from_tshark(item):
    layers = item.get("_source", {}).get("layers", {})
    ip = layers.get("ip", {})
    ipv6 = layers.get("ipv6", {})
    udp = layers.get("udp", {})
    frame = layers.get("frame", {})
    src = first(ip.get("ip.src") or ipv6.get("ipv6.src"))
    dst = first(ip.get("ip.dst") or ipv6.get("ipv6.dst"))
    sport = str(first(udp.get("udp.srcport") or ""))
    dport = str(first(udp.get("udp.dstport") or ""))
    payload = clean_hex(first(udp.get("udp.payload") or ""))
    return {
        "time_epoch": float(first(frame.get("frame.time_epoch") or 0) or 0),
        "frame_len": int(first(frame.get("frame.len") or 0) or 0),
        "src": src,
        "dst": dst,
        "sport": sport,
        "dport": dport,
        "udp_length": int(first(udp.get("udp.length") or 0) or 0),
        "payload_hex": payload,
        "payload_len": len(payload) // 2,
    }


def byte_entropy(hex_payloads):
    data = bytes.fromhex("".join(hex_payloads))
    if not data:
        return 0.0
    counts = Counter(data)
    total = len(data)
    return round(-sum((count / total) * math.log2(count / total) for count in counts.values()), 4)


def conversation_key(packet):
    a = (packet["src"], packet["sport"])
    b = (packet["dst"], packet["dport"])
    return tuple(sorted([a, b]))


def summarize(path):
    data = json.loads(Path(path).read_text(encoding="utf-8", errors="replace"))
    packets = [packet_from_tshark(item) for item in data]
    flows = defaultdict(list)
    conversations = defaultdict(list)
    for packet in packets:
        flows[(packet["src"], packet["sport"], packet["dst"], packet["dport"])].append(packet)
        conversations[conversation_key(packet)].append(packet)

    flow_rows = []
    for (src, sport, dst, dport), items in sorted(flows.items()):
        lengths = Counter(item["payload_len"] for item in items)
        prefixes = Counter(item["payload_hex"][:16] for item in items if item["payload_hex"])
        flow_rows.append(
            {
                "src": src,
                "sport": sport,
                "dst": dst,
                "dport": dport,
                "packet_count": len(items),
                "payload_lengths": [{"length": k, "count": v} for k, v in sorted(lengths.items())],
                "payload_prefixes": [{"hex": k, "count": v} for k, v in prefixes.most_common(10)],
                "payload_entropy": byte_entropy([item["payload_hex"] for item in items if item["payload_hex"]]),
                "first_seen": min(item["time_epoch"] for item in items),
                "last_seen": max(item["time_epoch"] for item in items),
            }
        )

    conversation_rows = []
    for ((host_a, port_a), (host_b, port_b)), items in sorted(conversations.items()):
        conversation_rows.append(
            {
                "endpoint_a": f"{host_a}:{port_a}",
                "endpoint_b": f"{host_b}:{port_b}",
                "packet_count": len(items),
                "payload_bytes": sum(item["payload_len"] for item in items),
                "first_seen": min(item["time_epoch"] for item in items),
                "last_seen": max(item["time_epoch"] for item in items),
            }
        )

    return {
        "packet_count": len(packets),
        "flow_count": len(flow_rows),
        "conversation_count": len(conversation_rows),
        "flows": flow_rows,
        "conversations": conversation_rows,
        "payloads": [{"hex": p["payload_hex"]} for p in packets if p["payload_hex"]],
    }


def main():
    parser = argparse.ArgumentParser(description="Summarize tshark JSON UDP packets into flows and payload prefixes.")
    parser.add_argument("packets_json", help="tshark -T json output with UDP fields")
    parser.add_argument("--json-out")
    args = parser.parse_args()

    result = summarize(args.packets_json)
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.json_out:
        Path(args.json_out).write_text(text + "\n", encoding="utf-8")

    print(f"PACKETS:{result['packet_count']}")
    print(f"FLOWS:{result['flow_count']}")
    for flow in result["flows"][:20]:
        print(f"{flow['src']}:{flow['sport']} -> {flow['dst']}:{flow['dport']} packets={flow['packet_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
