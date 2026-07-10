#!/usr/bin/env python3
import argparse
import json
import sys
import zipfile
from pathlib import Path


MARKERS = {
    "Flutter": [
        "libflutter.so",
        "libapp.so",
        "flutter_assets/",
    ],
    "React Native": [
        "index.android.bundle",
        ".hbc",
        "libhermes.so",
        "libreactnativejni.so",
    ],
    "Cordova/Capacitor": [
        "assets/www/",
        "cordova.js",
        "capacitor.config",
    ],
    "Xamarin": [
        "libmonodroid.so",
        "assemblies/",
        ".dll",
    ],
    "Unity IL2CPP": [
        "libil2cpp.so",
        "global-metadata.dat",
    ],
}


NEXT_STEPS = {
    "Flutter": "Use android-cross-platform-reversing Flutter workflow; treat JADX Java as wrapper/plugin code and inspect libapp.so/flutter_assets.",
    "React Native": "Extract JS bundle or Hermes bytecode; use web-api-reverse-engineering for JS/API review.",
    "Cordova/Capacitor": "Extract assets/www and use web-api-reverse-engineering on the web app assets.",
    "Xamarin": "Inspect managed assemblies and libmonodroid; use rev-ghidra for native glue when needed.",
    "Unity IL2CPP": "Use rev-u3d-dump with libil2cpp.so and global-metadata.dat.",
}


def match_marker(name: str, marker: str) -> bool:
    lower = name.lower()
    marker = marker.lower()
    if marker.endswith("/"):
        return marker in lower
    if marker.startswith("."):
        return lower.endswith(marker)
    return marker in lower


def fingerprint(apk: Path):
    with zipfile.ZipFile(apk) as zf:
        names = zf.namelist()

    frameworks = []
    evidence = {}
    for framework, markers in MARKERS.items():
        hits = []
        for name in names:
            if any(match_marker(name, marker) for marker in markers):
                hits.append(name)
        if hits:
            frameworks.append(framework)
            evidence[framework] = sorted(hits)[:25]

    return {
        "apk": str(apk),
        "frameworks": frameworks,
        "evidence": evidence,
        "recommended_next_steps": [NEXT_STEPS[name] for name in frameworks],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fingerprint cross-platform Android APK framework markers.")
    parser.add_argument("apk", help="APK file")
    parser.add_argument("--json-out", help="Write JSON output")
    args = parser.parse_args()

    apk = Path(args.apk)
    if not apk.is_file():
        print(f"ERROR: file not found: {apk}", file=sys.stderr)
        return 2

    try:
        result = fingerprint(apk)
    except zipfile.BadZipFile:
        print(f"ERROR: not a readable APK/ZIP: {apk}", file=sys.stderr)
        return 1

    text = json.dumps(result, indent=2, sort_keys=True)
    if args.json_out:
        Path(args.json_out).write_text(text + "\n", encoding="utf-8")

    print("FRAMEWORKS:" + (",".join(result["frameworks"]) if result["frameworks"] else "none"))
    for step in result["recommended_next_steps"]:
        print("NEXT:" + step)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
