#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ARTIFACT_NAMES = (
    "env-probe.json",
    "verification.json",
    "flow-result.json",
    "root-diff.json",
    "attestation-summary.json",
)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected JSON object")
    return data


def first_present(run_dir: Path, *names: str) -> dict[str, Any]:
    for name in names:
        data = read_json(run_dir / name)
        if data:
            return data
    return {}


def nested(data: dict[str, Any], *keys: str) -> Any:
    value: Any = data
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def metrics(run_dir: Path) -> dict[str, Any]:
    env = first_present(run_dir, "env-probe.json", "attestation/env-probe.json")
    verification = first_present(run_dir, "verification.json", "attestation/verification.json")
    flow = first_present(run_dir, "flow-result.json")
    root_diff = first_present(run_dir, "root-diff.json", "analysis/root-diff.json")

    key_attestation = env.get("key_attestation", {}) if isinstance(env.get("key_attestation"), dict) else {}
    checks = verification.get("checks", {}) if isinstance(verification.get("checks"), dict) else {}
    backend_strict = nested(verification, "policy", "backendStrict")
    root_comparison = root_diff.get("rootComparison", {}) if isinstance(root_diff.get("rootComparison"), dict) else {}

    return {
        "chainPresent": key_attestation.get("chain_present", key_attestation.get("chainPresent")),
        "chainLength": key_attestation.get("chain_length", key_attestation.get("chainLength")),
        "attestationSecurityLevel": checks.get("attestationSecurityLevel"),
        "keymasterSecurityLevel": checks.get("keymasterSecurityLevel"),
        "deviceLocked": checks.get("deviceLocked"),
        "verifiedBootState": checks.get("verifiedBootState"),
        "backendStrict": backend_strict.get("passed") if isinstance(backend_strict, dict) else None,
        "signatureValid": flow.get("signatureValid"),
        "exactGoogleRootMatch": root_comparison.get("exactGoogleRootMatch"),
        "spkiGoogleRootMatch": root_comparison.get("spkiGoogleRootMatch"),
    }


def compare(left_dir: Path, right_dir: Path, left_label: str, right_label: str) -> dict[str, Any]:
    left = metrics(left_dir)
    right = metrics(right_dir)
    differences = {
        key: {"left": left.get(key), "right": right.get(key)}
        for key in sorted(set(left) | set(right))
        if left.get(key) != right.get(key)
    }
    next_steps: list[str] = []
    if "backendStrict" in differences or "signatureValid" in differences:
        next_steps.append("treat key possession and backend trust as separate claims")
    if "exactGoogleRootMatch" in differences or "spkiGoogleRootMatch" in differences:
        next_steps.append("preserve exact-root and SPKI-root comparisons separately")
    if "attestationSecurityLevel" in differences or "keymasterSecurityLevel" in differences:
        next_steps.append("compare hardware-backed vs software-backed attestation levels")
    if "deviceLocked" in differences or "verifiedBootState" in differences:
        next_steps.append("verify bootloader and verified boot state against the physical baseline")
    if not next_steps:
        next_steps.append("promote matching evidence into a finding with both run paths")

    return {
        "leftLabel": left_label,
        "rightLabel": right_label,
        "leftRun": str(left_dir),
        "rightRun": str(right_dir),
        "leftMetrics": left,
        "rightMetrics": right,
        "differences": differences,
        "nextSteps": next_steps,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two Android attestation lab run folders.")
    parser.add_argument("left_run", type=Path)
    parser.add_argument("right_run", type=Path)
    parser.add_argument("--left-label", default="left")
    parser.add_argument("--right-label", default="right")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    report = compare(args.left_run, args.right_run, args.left_label, args.right_label)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(text, end="")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
