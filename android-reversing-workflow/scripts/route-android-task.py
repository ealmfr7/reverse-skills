#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path


RULES = [
    ("packed/dynamic DEX", ["USES_DYNAMIC_DEX=yes", "stub", "shell", "packer", "packed"], ["rev-dex-dumper", "android-reverse-engineering"]),
    ("Flutter app", ["HAS_FLUTTER=yes", "flutter"], ["android-cross-platform-reversing", "android-frida-hooking"]),
    ("React Native/Hermes app", ["HAS_REACT_NATIVE=yes", "react native", "hermes", ".hbc"], ["android-cross-platform-reversing", "web-api-reverse-engineering"]),
    ("Cordova/Capacitor app", ["HAS_CORDOVA=yes", "cordova", "capacitor"], ["android-cross-platform-reversing", "web-api-reverse-engineering"]),
    ("Xamarin app", ["HAS_XAMARIN=yes", "xamarin", "mono"], ["android-cross-platform-reversing", "rev-ghidra"]),
    ("Unity/IL2CPP app", ["HAS_UNITY=yes", "unity", "il2cpp"], ["android-cross-platform-reversing", "rev-u3d-dump"]),
    ("network/API analysis", ["USES_OKHTTP=yes", "USES_RETROFIT=yes", "api", "traffic", "http", "tls", "proxy", "okhttp", "retrofit"], ["android-traffic-analysis", "web-api-reverse-engineering", "android-frida-hooking"]),
    ("WebView/hybrid analysis", ["USES_WEBVIEW=yes", "webview", "javascriptinterface"], ["android-cross-platform-reversing", "android-frida-hooking", "web-api-reverse-engineering"]),
    ("crypto/storage analysis", ["USES_CRYPTO=yes", "crypto", "cipher", "decrypt", "encrypt", "token", "sharedpreferences"], ["android-frida-hooking", "android-reverse-engineering"]),
    ("native/JNI analysis", ["HAS_NATIVE_LIBS=yes", "NATIVE_JNI_SIGNAL=yes", ".so", "jni", "native", "arm64"], ["android-arm64-native-basics", "rev-ghidra", "rev-idapython", "android-frida-hooking"]),
    ("malware triage", ["MALWARE_SIGNAL=yes", "malware", "ioc", "suspicious", "c2", "sms", "accessibility"], ["android-malware-triage"]),
    ("device attestation lab", ["attestation", "keymaster", "keystore", "play integrity", "safetynet", "vmos", "root certificate", "google root", "spki", "backend trust", "nonce"], ["android-device-attestation-lab", "android-anti-analysis-and-obfuscation"]),
    ("APK patch/rebuild", ["patch", "rebuild", "apktool", "sign", "zipalign", "smali"], ["android-apk-patching"]),
    ("isolated native emulation", ["unicorn", "emulate", "emulation", "algorithm", "native signing"], ["rev-unicorn-debug", "android-arm64-native-basics"]),
    ("UDP/custom datagram analysis", ["udp", "datagram", "sendto", "recvfrom", "quic", "dtls", "pcap", "tshark"], ["udp-protocol-reverse-engineering", "android-frida-hooking", "rev-ghidra"]),
]


def read_input(args: argparse.Namespace) -> str:
    parts = []
    if args.text:
        parts.append(args.text)
    if args.fingerprint:
        parts.append(Path(args.fingerprint).read_text(errors="replace"))
    if not parts and not sys.stdin.isatty():
        parts.append(sys.stdin.read())
    return "\n".join(parts)


def route(text: str):
    haystack = text.lower()
    keyword_haystack = "\n".join(
        line for line in haystack.splitlines()
        if not re.match(r"^[a-z0-9_]+=(no|0|false)\s*$", line.strip())
    )
    hits = []
    for label, needles, skills in RULES:
        score = 0
        matched = []
        for needle in needles:
            n = needle.lower()
            if "=" in n:
                if re.search(rf"^{re.escape(n)}$", haystack, re.MULTILINE):
                    score += 3
                    matched.append(needle)
            elif n in keyword_haystack:
                score += 1
                matched.append(needle)
        if score:
            hits.append((score, label, matched, skills))
    hits.sort(key=lambda x: (-x[0], x[1]))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description="Route Android reversing evidence to local skills.")
    parser.add_argument("text", nargs="?", help="Task description or pasted evidence")
    parser.add_argument("--fingerprint", "-f", help="Output from scripts/fingerprint-apk.sh")
    args = parser.parse_args()

    text = read_input(args)
    if not text.strip():
        parser.error("provide task text, --fingerprint, or stdin")

    hits = route(text)
    if not hits:
        print("No strong route found.")
        print("Recommended first step: android-reversing-workflow -> android-reverse-engineering")
        return 0

    seen = []
    print("Recommended routes:")
    for score, label, matched, skills in hits[:6]:
        print(f"- {label} (score {score})")
        print(f"  matched: {', '.join(matched)}")
        print(f"  skills: {', '.join(skills)}")
        for skill in skills:
            if skill not in seen:
                seen.append(skill)

    print("\nSuggested first skill chain:")
    print(" -> ".join(seen[:6]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
