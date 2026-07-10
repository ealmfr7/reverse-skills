#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


RULES = [
    (
        "reverse-investigation-workflow",
        {"case", "evidence", "artifact", "run", "scope", "investigation", "apk", "har", "pcap", "capture"},
        {".apk", ".xapk", ".aab", ".jar", ".aar", ".har", ".pcap", ".pcapng"},
        "Create/maintain case structure, artifacts, runs, and evidence index.",
    ),
    (
        "android-reversing-workflow",
        {"apk", "xapk", "aab", "android", "jadx", "dex", "smali", "frida", "objection", "package", "lib.so", ".so"},
        {".apk", ".xapk", ".aab", ".jar", ".aar", ".dex", ".so"},
        "Route Android APK/static/dynamic/native reversing.",
    ),
    (
        "android-frida-hooking",
        {"frida", "hook", "hooking", "java.use", "interceptor", "runtime", "attach", "spawn"},
        {".js"},
        "Create or reason about runtime hooks.",
    ),
    (
        "android-anti-analysis-and-obfuscation",
        {
            "root",
            "emulator",
            "vmos",
            "anti-debug",
            "anti-frida",
            "pinning",
            "attestation",
            "integrity",
            "safetynet",
            "keymaster",
            "obfuscation",
            "packed",
        },
        set(),
        "Classify Android anti-analysis, attestation, pinning, packing, and obfuscation protections.",
    ),
    (
        "web-api-reverse-engineering",
        {"web", "url", "har", "javascript", "js", "bundle", "graphql", "websocket", "devtools", "curl", "api", "endpoint"},
        {".har", ".html", ".js", ".map"},
        "Analyze browser/API behavior and client-side assets.",
    ),
    (
        "udp-protocol-reverse-engineering",
        {"udp", "pcap", "pcapng", "datagram", "packet", "quic", "dtls", "sendto", "recvfrom", "protocol"},
        {".pcap", ".pcapng"},
        "Analyze UDP/custom protocol captures.",
    ),
    (
        "reverse-probe-tooling-workflow",
        {"script", "probe", "analyzer", "jsonl", "schema", "events", "runner", "stdout", "stderr", "frida"},
        {".js", ".py", ".jsonl"},
        "Standardize probes, analyzers, event schemas, and run outputs.",
    ),
    (
        "reverse-docs-workflow",
        {"doc", "docs", "finding", "findings", "report", "decision", "hypothesis", "markdown", "index", "writeup"},
        {".md"},
        "Organize findings, decisions, reports, and documentation indexes.",
    ),
    (
        "rev-ghidra",
        {"ghidra", "native", "arm64", "jni", "decompile", "offset", "symbol", "struct"},
        {".so", ".bin", ".elf"},
        "Analyze native binaries with Ghidra-oriented workflow.",
    ),
]


def route(goal: str, artifacts: list[str]) -> dict:
    text = " ".join([goal, *artifacts]).lower()
    suffixes = {Path(artifact.lower()).suffix for artifact in artifacts}
    selected: list[str] = []
    reasons: dict[str, str] = {}

    for skill, keywords, extensions, reason in RULES:
        if any(keyword in text for keyword in keywords) or suffixes.intersection(extensions):
            selected.append(skill)
            reasons[skill] = reason

    if not selected:
        selected.extend(["reverse-investigation-workflow", "reverse-docs-workflow"])
        reasons["reverse-investigation-workflow"] = "Default case/evidence structure for unclear reversing tasks."
        reasons["reverse-docs-workflow"] = "Default notes/findings structure for unclear reversing tasks."

    ordered = []
    for skill in [
        "reverse-investigation-workflow",
        "android-reversing-workflow",
        "web-api-reverse-engineering",
        "udp-protocol-reverse-engineering",
        "android-frida-hooking",
        "android-anti-analysis-and-obfuscation",
        "rev-ghidra",
        "reverse-probe-tooling-workflow",
        "reverse-docs-workflow",
    ]:
        if skill in selected and skill not in ordered:
            ordered.append(skill)

    return {
        "skills": ordered,
        "reasons": {skill: reasons[skill] for skill in ordered},
        "firstSteps": first_steps(ordered),
    }


def first_steps(skills: list[str]) -> list[str]:
    steps = []
    if "reverse-investigation-workflow" in skills:
        steps.append("Create/select case and record scope, target, artifacts, and authorization.")
    if "android-reversing-workflow" in skills:
        steps.append("Fingerprint APK/app and choose static, dynamic, traffic, or native route.")
    if "android-anti-analysis-and-obfuscation" in skills:
        steps.append("Scan for root/emulator/Frida/pinning/attestation/packing signals and plan comparison runs.")
    if "web-api-reverse-engineering" in skills:
        steps.append("Fingerprint URL/HAR/JS and build endpoint inventory.")
    if "udp-protocol-reverse-engineering" in skills:
        steps.append("Summarize PCAP/datagrams and identify peers, lengths, prefixes, and sessions.")
    if "reverse-probe-tooling-workflow" in skills:
        steps.append("Standardize probes/analyzers and write run outputs as JSONL plus indexes.")
    if "reverse-docs-workflow" in skills:
        steps.append("Promote durable claims into numbered findings/decisions with evidence links.")
    return steps


def main() -> int:
    parser = argparse.ArgumentParser(description="Route a reverse engineering task to local skills.")
    parser.add_argument("goal")
    parser.add_argument("--artifact", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = route(args.goal, args.artifact)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("SKILLS:" + ",".join(result["skills"]))
        for step in result["firstSteps"]:
            print("STEP:" + step)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
