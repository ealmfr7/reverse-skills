#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


CATEGORIES = {
    "root-detection": [r"/system/(xbin|bin)/su", r"\bsu\b", r"magisk", r"busybox", r"superuser", r"test-keys", r"ro\.debuggable"],
    "emulator-detection": [r"goldfish", r"ranchu", r"sdk_gphone", r"generic", r"emulator", r"qemu", r"vmos", r"ro\.kernel\.qemu"],
    "frida-detection": [r"frida", r"gum-js-loop", r"gadget", r"xposed", r"substrate", r"/proc/self/maps", r"linjector"],
    "native-anti-debug": [r"ptrace", r"PTRACE_TRACEME", r"TracerPid", r"prctl", r"seccomp", r"anti.?debug", r"syscall"],
    "certificate-pinning": [r"CertificatePinner", r"TrustManager", r"X509TrustManager", r"checkServerTrusted", r"network_security_config", r"pin-sha256"],
    "play-integrity-attestation": [r"IntegrityManager", r"IntegrityManagerFactory", r"SafetyNet", r"attest\(", r"KeyStore", r"key.?attestation", r"keymaster", r"MEETS_DEVICE_INTEGRITY"],
    "packing-loader": [r"DexClassLoader", r"PathClassLoader", r"loadDex", r"loadClass", r"System\.loadLibrary", r"jiagu", r"bangcle", r"legu", r"protect"],
    "java-obfuscation": [r"reflection", r"Class\.forName", r"Method\.invoke", r"StringBuilder", r"Base64\.decode"],
    "integrity-tamper-check": [r"getPackageInfo", r"GET_SIGNATURES", r"SigningInfo", r"MessageDigest", r"SHA-256", r"CRC32", r"installerPackageName"],
}

TEXT_SUFFIXES = {".java", ".kt", ".smali", ".xml", ".txt", ".json", ".properties", ".cfg", ".md", ".strings"}


def is_text_candidate(path: Path) -> bool:
    return path.name in {"AndroidManifest.xml", "apktool.yml"} or path.suffix.lower() in TEXT_SUFFIXES or path.name.endswith(".so.strings.txt")


def iter_text_files(root: Path):
    if root.is_file():
        if is_text_candidate(root):
            yield root
        return
    for path in sorted(root.rglob("*")):
        if path.is_file() and is_text_candidate(path):
            yield path


def scan(root: Path) -> dict[str, Any]:
    findings = []
    files_scanned = 0
    for path in iter_text_files(root):
        files_scanned += 1
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(path.relative_to(root)) if path != root else path.name
        for category, patterns in CATEGORIES.items():
            matches = [pattern for pattern in patterns if re.search(pattern, text, flags=re.IGNORECASE)]
            if matches:
                findings.append({"category": category, "file": rel, "signals": sorted(set(matches)), "confidence": confidence_for(category, matches)})

    categories = sorted({finding["category"] for finding in findings})
    risk_score = min(10, len(categories) + sum(1 for finding in findings if finding["confidence"] == "high") // 2)
    return {
        "root": str(root),
        "filesScanned": files_scanned,
        "riskScore": risk_score,
        "categories": categories,
        "findings": findings,
        "recommendedNext": recommendations(categories),
    }


def confidence_for(category: str, matches: list[str]) -> str:
    strong = {
        "certificate-pinning": {"CertificatePinner", "pin-sha256", "checkServerTrusted"},
        "play-integrity-attestation": {"IntegrityManager", "SafetyNet", "keymaster", "key.?attestation"},
        "native-anti-debug": {"ptrace", "PTRACE_TRACEME", "TracerPid"},
        "frida-detection": {"frida", "gum-js-loop", "/proc/self/maps"},
        "root-detection": {"/system/(xbin|bin)/su", "magisk"},
        "packing-loader": {"DexClassLoader", "jiagu", "bangcle", "legu"},
    }
    return "high" if any(match in strong.get(category, set()) for match in matches) else "medium"


def recommendations(categories: list[str]) -> list[str]:
    out = []
    if "play-integrity-attestation" in categories:
        out.append("Compare real-device vs emulator/root attestation outputs and store parsed verdicts.")
    if "frida-detection" in categories:
        out.append("Run no-Frida, attach, and spawn baselines; capture logcat and process/thread evidence.")
    if "certificate-pinning" in categories:
        out.append("Document proxy baseline and locate pinning implementation before attempting traffic capture.")
    if "packing-loader" in categories:
        out.append("Plan runtime DEX/class loading observation and memory dump workflow.")
    if "native-anti-debug" in categories:
        out.append("Use native/static xrefs and controlled strace/logcat runs to identify anti-debug checks.")
    return out or ["No strong anti-analysis category found; continue standard APK triage."]


def write_markdown(path: Path, result: dict[str, Any]) -> None:
    lines = ["# Android Anti-Analysis Triage", "", f"Files scanned: {result['filesScanned']}", f"Risk score: {result['riskScore']}/10", "", "## Categories", ""]
    lines.extend(f"- {category}" for category in result["categories"])
    lines.extend(["", "## Findings", ""])
    for finding in result["findings"]:
        lines.append(f"- `{finding['category']}` in `{finding['file']}` ({finding['confidence']}): {', '.join(finding['signals'])}")
    lines.extend(["", "## Recommended Next", ""])
    lines.extend(f"- {item}" for item in result["recommendedNext"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan decompiled Android artifacts for anti-analysis and obfuscation signals.")
    parser.add_argument("root", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--markdown-out", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = scan(args.root)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown_out:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(args.markdown_out, result)
    if args.json or not args.json_out:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"ANTI_ANALYSIS_FINDINGS:{len(result['findings'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
