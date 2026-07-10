#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


KNOWN_ARTIFACTS = {
    "env-probe": ("env-probe.json", "attestation/env-probe.json"),
    "verification": ("verification.json", "attestation/verification.json"),
    "flow-result": ("flow-result.json",),
    "flow-comparison": ("flow-comparison.json",),
    "root-diff": ("root-diff.json", "analysis/root-diff.json"),
    "root-source": ("root-source.json", "analysis/root-source.json"),
    "android-preflight": ("android-preflight.json", "preflight.json"),
}


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def find_artifacts(root: Path) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for label, names in KNOWN_ARTIFACTS.items():
        for name in names:
            path = root / name
            if path.exists():
                found[label] = path
                break
    return found


def _bool_at(data: dict[str, Any], *path: str) -> bool | None:
    value: Any = data
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value if isinstance(value, bool) else None


def summarize(root: Path) -> dict[str, Any]:
    artifacts = find_artifacts(root)
    loaded = {label: read_json(path) for label, path in artifacts.items()}
    signals: list[str] = []
    next_steps: list[str] = []

    env = loaded.get("env-probe", {})
    key_attestation = env.get("key_attestation", {}) if isinstance(env.get("key_attestation"), dict) else {}
    if key_attestation.get("chain_present") or key_attestation.get("chainPresent"):
        signals.append("attestation-chain-present")
    chain_length = key_attestation.get("chain_length", key_attestation.get("chainLength"))
    if isinstance(chain_length, int) and chain_length > 0:
        signals.append(f"attestation-chain-length:{chain_length}")

    verification = loaded.get("verification", {})
    policy = verification.get("policy", {}) if isinstance(verification.get("policy"), dict) else {}
    backend_strict = policy.get("backendStrict", {}) if isinstance(policy.get("backendStrict"), dict) else {}
    if backend_strict.get("passed") is False:
        signals.append("backend-strict-failed")
    elif backend_strict.get("passed") is True:
        signals.append("backend-strict-passed")

    checks = verification.get("checks", {}) if isinstance(verification.get("checks"), dict) else {}
    for key in ("attestationSecurityLevel", "keymasterSecurityLevel", "verifiedBootState"):
        if checks.get(key):
            signals.append(f"{key}:{checks[key]}")
    if checks.get("deviceLocked") is False:
        signals.append("device-unlocked")

    flow = loaded.get("flow-result", {})
    if flow.get("signatureValid") is True:
        signals.append("challenge-signature-valid")
    elif flow.get("signatureValid") is False:
        signals.append("challenge-signature-invalid")
    if flow.get("diagnosticContinuedAfterRegisterFail"):
        signals.append("diagnostic-continued-after-register-fail")

    root_diff = loaded.get("root-diff", {})
    exact_root = _bool_at(root_diff, "rootComparison", "exactGoogleRootMatch")
    spki_root = _bool_at(root_diff, "rootComparison", "spkiGoogleRootMatch")
    if exact_root is not None:
        signals.append(f"exact-google-root-match:{str(exact_root).lower()}")
    if spki_root is not None:
        signals.append(f"spki-google-root-match:{str(spki_root).lower()}")

    if "env-probe" not in loaded:
        next_steps.append("collect environment and KeyStore attestation output")
    if "verification" not in loaded:
        next_steps.append("verify attestation chain, challenge, app binding, root, and revocation status")
    if "flow-result" not in loaded:
        next_steps.append("run backend nonce/register/signature flow if backend trust is in scope")
    if "root-diff" not in loaded and ("verification" in loaded or "env-probe" in loaded):
        next_steps.append("compare attestation root certificate against trusted root material")
    if "flow-comparison" not in loaded:
        next_steps.append("compare against a known-good physical-device run")

    return {
        "root": str(root),
        "artifactCount": len(loaded),
        "present": sorted(loaded),
        "missing": sorted(set(KNOWN_ARTIFACTS) - set(loaded)),
        "artifacts": {label: str(path) for label, path in sorted(artifacts.items())},
        "signals": sorted(dict.fromkeys(signals)),
        "nextSteps": next_steps,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize Android device attestation lab artifacts in a run folder.")
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    report = summarize(args.run_dir)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(text, end="")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
