#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_COMMANDS = {
    "getprop.txt": ["shell", "getprop"],
    "settings-global.txt": ["shell", "settings", "list", "global"],
    "settings-secure.txt": ["shell", "settings", "list", "secure"],
    "packages.txt": ["shell", "pm", "list", "packages"],
    "connectivity.txt": ["shell", "dumpsys", "connectivity"],
    "wifi.txt": ["shell", "dumpsys", "wifi"],
    "sensorservice.txt": ["shell", "dumpsys", "sensorservice"],
    "ip-link.txt": ["shell", "ip", "-o", "link", "show"],
}

IMPORTANT_PROPS = (
    "ro.product.model",
    "ro.product.manufacturer",
    "ro.product.brand",
    "ro.product.device",
    "ro.product.name",
    "ro.build.fingerprint",
    "ro.build.version.release",
    "ro.build.version.sdk",
    "ro.build.version.security_patch",
    "ro.boot.verifiedbootstate",
    "ro.boot.flash.locked",
    "ro.boot.vbmeta.device_state",
    "ro.hardware",
    "ro.kernel.qemu",
)

IMPORTANT_SETTINGS = (
    "adb_enabled",
    "adb_wifi_enabled",
    "development_settings_enabled",
    "http_proxy",
    "mock_location",
    "wait_for_debugger",
    "private_dns_mode",
    "location_mode",
)

SUSPICIOUS_PACKAGE_PATTERNS = (
    "magisk",
    "supersu",
    "kernelsu",
    "apatch",
    "frida",
    "xposed",
    "lsposed",
    "substrate",
    "emulator",
    "virtual",
)


def run_adb(args: list[str], serial: str | None) -> subprocess.CompletedProcess[str]:
    cmd = ["adb"]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(args)
    return subprocess.run(cmd, text=True, capture_output=True)


def parse_getprop(raw: str) -> dict[str, str]:
    props: dict[str, str] = {}
    pattern = re.compile(r"^\[([^\]]+)\]: \[(.*)\]$")
    for line in raw.splitlines():
        match = pattern.match(line.strip())
        if match:
            props[match.group(1)] = match.group(2)
    return props


def parse_settings(raw: str) -> dict[str, str]:
    settings: dict[str, str] = {}
    for line in raw.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            settings[key.strip()] = value.strip()
    return settings


def parse_packages(raw: str) -> list[str]:
    packages = []
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("package:"):
            packages.append(line.removeprefix("package:"))
    return packages


def summarize(raw: dict[str, str], packages: list[str]) -> dict[str, Any]:
    props = parse_getprop(raw.get("getprop.txt", ""))
    settings = {
        **parse_settings(raw.get("settings-global.txt", "")),
        **parse_settings(raw.get("settings-secure.txt", "")),
    }
    package_names = parse_packages(raw.get("packages.txt", ""))
    suspicious = [
        package
        for package in package_names
        if any(pattern in package.lower() for pattern in SUSPICIOUS_PACKAGE_PATTERNS)
    ]
    return {
        "capturedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "properties": {key: props.get(key) for key in IMPORTANT_PROPS if key in props},
        "settings": {key: settings.get(key) for key in IMPORTANT_SETTINGS if key in settings},
        "requestedPackages": packages,
        "requestedPackageState": {
            package: {
                "installed": package in package_names,
            }
            for package in packages
        },
        "packageCount": len(package_names),
        "suspiciousPackages": suspicious[:50],
        "rawFiles": sorted(raw),
    }


def capture(serial: str | None, packages: list[str], raw_out: Path | None) -> dict[str, Any]:
    commands = dict(BASE_COMMANDS)
    for package in packages:
        safe = re.sub(r"[^a-zA-Z0-9_.-]+", "_", package)
        commands[f"package-{safe}.txt"] = ["shell", "dumpsys", "package", package]

    raw: dict[str, str] = {}
    errors: dict[str, str] = {}
    for name, adb_args in commands.items():
        result = run_adb(adb_args, serial)
        raw[name] = result.stdout
        if result.returncode != 0:
            errors[name] = result.stderr.strip()
        if raw_out:
            path = raw_out / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(result.stdout, encoding="utf-8", errors="replace")

    report = summarize(raw, packages)
    report["serial"] = serial
    report["errors"] = errors
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Capture public Android environment signals over ADB for device attestation baselines.")
    parser.add_argument("-s", "--serial", help="ADB serial.")
    parser.add_argument("--package", action="append", default=[], help="Package name to include in package-state capture. May be repeated.")
    parser.add_argument("--raw-out", type=Path, help="Optional directory for raw command stdout files.")
    parser.add_argument("--json-out", type=Path, help="Optional summary JSON output path.")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    report = capture(args.serial, args.package, args.raw_out)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(text, end="")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
