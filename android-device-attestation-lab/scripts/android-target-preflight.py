#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_FRIDA_SERVER_PATH = "/data/local/tmp/frida-server"
GUM_THREAD_RE = re.compile(r"gum|frida|gmain|gdbus|linjector|pool-frida", re.IGNORECASE)


def run_adb(args: list[str], device: str | None = None) -> subprocess.CompletedProcess[str]:
    cmd = ["adb"]
    if device:
        cmd.extend(["-s", device])
    cmd.extend(args)
    return subprocess.run(cmd, text=True, capture_output=True)


def parse_adb_devices(output: str) -> list[str]:
    devices: list[str] = []
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(parts[0])
    return devices


def list_adb_devices() -> list[str]:
    return parse_adb_devices(run_adb(["devices"]).stdout)


def package_installed(device: str, package: str) -> bool:
    return run_adb(["shell", "pm", "path", package], device=device).returncode == 0


def pidof_package(device: str, package: str) -> str | None:
    result = run_adb(["shell", "pidof", package], device=device)
    pid = result.stdout.strip().split()
    return pid[0] if result.returncode == 0 and pid else None


def current_foreground(device: str) -> str:
    result = run_adb(["shell", "dumpsys", "activity", "activities"], device=device)
    if result.returncode != 0:
        return ""
    for line in result.stdout.splitlines():
        if "mResumedActivity" in line or "topResumedActivity" in line:
            return line.strip()
    return ""


def frida_server_running(device: str) -> bool:
    return "frida-server" in run_adb(["shell", "ps", "-A"], device=device).stdout


def frida_server_binary_exists(device: str, path: str) -> bool:
    return run_adb(["shell", "ls", path], device=device).returncode == 0


def start_frida_server(device: str, path: str) -> None:
    quoted = "'" + path.replace("'", "'\\''") + "'"
    run_adb(["shell", f"nohup {quoted} >/data/local/tmp/frida-server.log 2>&1 &"], device=device)


def force_stop_package(device: str, package: str) -> None:
    run_adb(["shell", "am", "force-stop", package], device=device)


def gum_threads(device: str, pid: str | None) -> list[str]:
    if not pid:
        return []
    result = run_adb(["shell", "ps", "-T", "-p", pid], device=device)
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if GUM_THREAD_RE.search(line)]


def choose_device(package: str, preferred_device: str | None) -> tuple[str | None, list[str], list[str]]:
    devices = list_adb_devices()
    if preferred_device:
        return preferred_device, devices, []
    matches = [device for device in devices if package_installed(device, package)]
    if len(matches) == 1:
        return matches[0], devices, []
    if not matches:
        return None, devices, [f"No connected adb device has package {package!r} installed"]
    return None, devices, [f"Multiple connected adb devices have package {package!r} installed: {', '.join(matches)}"]


def preflight(
    package: str,
    device: str | None,
    foreground_regex: str | None,
    *,
    start_frida: bool,
    frida_server_path: str,
    force_stop_if_gum: bool,
) -> dict[str, Any]:
    chosen, devices, issues = choose_device(package, device)
    report: dict[str, Any] = {
        "ready": False,
        "device": chosen,
        "connectedDevices": devices,
        "package": package,
        "packageInstalled": False,
        "pid": None,
        "foreground": "",
        "foregroundMatches": None,
        "fridaServerRunning": False,
        "fridaServerPath": frida_server_path,
        "fridaServerBinaryExists": None,
        "fridaServerStartAttempted": False,
        "fridaServerStarted": False,
        "gumThreads": [],
        "forceStopAttempted": False,
        "issues": issues,
    }
    if not chosen:
        return report

    report["packageInstalled"] = package_installed(chosen, package)
    if not report["packageInstalled"]:
        report["issues"].append(f"Package {package!r} is not installed on device {chosen!r}")
        return report

    foreground = current_foreground(chosen)
    report["foreground"] = foreground
    if foreground_regex:
        report["foregroundMatches"] = bool(re.search(foreground_regex, foreground))
        if not report["foregroundMatches"]:
            report["issues"].append("foreground activity does not match --foreground-regex")

    pid = pidof_package(chosen, package)
    report["pid"] = pid
    report["gumThreads"] = gum_threads(chosen, pid)
    if report["gumThreads"] and force_stop_if_gum:
        report["forceStopAttempted"] = True
        force_stop_package(chosen, package)
        pid = pidof_package(chosen, package)
        report["pid"] = pid
        report["gumThreads"] = gum_threads(chosen, pid)
    if report["gumThreads"]:
        report["issues"].append("residual Gum/Frida threads detected in target process")

    report["fridaServerRunning"] = frida_server_running(chosen)
    if start_frida and not report["fridaServerRunning"]:
        report["fridaServerStartAttempted"] = True
        report["fridaServerBinaryExists"] = frida_server_binary_exists(chosen, frida_server_path)
        if report["fridaServerBinaryExists"]:
            start_frida_server(chosen, frida_server_path)
            report["fridaServerRunning"] = frida_server_running(chosen)
            report["fridaServerStarted"] = report["fridaServerRunning"]
        else:
            report["issues"].append(f"frida-server binary not found at {frida_server_path!r}")

    if start_frida and not report["fridaServerRunning"]:
        report["issues"].append("frida-server is not running")

    report["ready"] = bool(report["packageInstalled"] and not report["issues"])
    return report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check whether a connected Android target is ready for a dynamic analysis run.")
    parser.add_argument("--device", help="ADB serial to check. If omitted, select the only device with --package installed.")
    parser.add_argument("--package", required=True, help="Android package name.")
    parser.add_argument("--foreground-regex", help="Regex expected in dumpsys foreground activity.")
    parser.add_argument("--start-frida-server", action="store_true", help="Start frida-server from --frida-server-path when it is not already running.")
    parser.add_argument("--frida-server-path", default=DEFAULT_FRIDA_SERVER_PATH, help="Device path used by --start-frida-server.")
    parser.add_argument("--force-stop-if-gum", action="store_true", help="Force-stop the target package if residual Gum/Frida threads are detected.")
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    parser.add_argument("--fail-if-not-ready", action="store_true", help="Exit 2 if readiness checks fail.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    report = preflight(
        args.package,
        args.device,
        args.foreground_regex,
        start_frida=args.start_frida_server,
        frida_server_path=args.frida_server_path,
        force_stop_if_gum=args.force_stop_if_gum,
    )
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(text, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    if args.fail_if_not_ready and not report["ready"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
