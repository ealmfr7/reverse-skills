#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected JSON object")
    return data


def nested(data: dict[str, Any], *keys: str) -> Any:
    value: Any = data
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def normalize_key_attestation(report: dict[str, Any]) -> dict[str, Any]:
    key_attestation = report.get("key_attestation", {})
    if not isinstance(key_attestation, dict):
        key_attestation = {}
    checks = report.get("checks", {})
    if not isinstance(checks, dict):
        checks = {}
    parsed = key_attestation.get("parsed") or report.get("parsed_attestation") or {}
    if not isinstance(parsed, dict):
        parsed = {}
    root_of_trust = parsed.get("rootOfTrust") if isinstance(parsed.get("rootOfTrust"), dict) else {}

    certificates = key_attestation.get("certificates") or []
    if not isinstance(certificates, list):
        certificates = []
    chain_present = bool(
        key_attestation.get("chain_present")
        or key_attestation.get("chainPresent")
        or certificates
    )
    chain_length = key_attestation.get("chain_length", key_attestation.get("chainLength"))
    if not isinstance(chain_length, int):
        chain_length = len(certificates) if certificates else (1 if chain_present else 0)

    return {
        "chainPresent": chain_present,
        "chainLength": chain_length,
        "attestationSecurityLevel": parsed.get("attestationSecurityLevel") or checks.get("attestationSecurityLevel"),
        "keymasterSecurityLevel": parsed.get("keymasterSecurityLevel") or checks.get("keymasterSecurityLevel"),
        "deviceLocked": root_of_trust.get("deviceLocked", checks.get("deviceLocked")),
        "verifiedBootState": root_of_trust.get("verifiedBootState", checks.get("verifiedBootState")),
        "requestedChallenge": key_attestation.get("requested_challenge"),
        "attestationChallenge": parsed.get("attestationChallenge"),
    }


def root_checks(root_diff: dict[str, Any]) -> dict[str, Any]:
    comparison = root_diff.get("rootComparison", {})
    if not isinstance(comparison, dict):
        comparison = {}
    return {
        "exactGoogleRootMatch": comparison.get("exactGoogleRootMatch"),
        "spkiGoogleRootMatch": comparison.get("spkiGoogleRootMatch"),
    }


def verify(report: dict[str, Any], root_diff: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    checks = {
        **normalize_key_attestation(report),
        **root_checks(root_diff),
    }
    reasons: list[str] = []
    warnings: list[str] = []

    if not checks["chainPresent"]:
        reasons.append("attestation certificate chain is missing")
    if checks["chainLength"] < args.min_chain_length:
        reasons.append("attestation certificate chain is shorter than required")
    if args.expected_challenge:
        if checks.get("requestedChallenge") != args.expected_challenge and checks.get("attestationChallenge") != args.expected_challenge:
            reasons.append("attestation challenge mismatch")
    if args.expected_attestation_security_level and checks.get("attestationSecurityLevel") != args.expected_attestation_security_level:
        reasons.append("attestation security level mismatch")
    if args.expected_keymaster_security_level and checks.get("keymasterSecurityLevel") != args.expected_keymaster_security_level:
        reasons.append("keymaster security level mismatch")
    if args.require_device_locked and checks.get("deviceLocked") is not True:
        reasons.append("device is not locked")
    if args.expected_verified_boot_state and checks.get("verifiedBootState") != args.expected_verified_boot_state:
        reasons.append("verified boot state mismatch")
    if args.require_exact_google_root and checks.get("exactGoogleRootMatch") is not True:
        reasons.append("missing exact Google root certificate match")
    if args.require_spki_google_root and checks.get("spkiGoogleRootMatch") is not True:
        reasons.append("missing Google root SPKI match")
    if checks.get("exactGoogleRootMatch") is None:
        warnings.append("exact Google root comparison was not provided")
    if checks.get("spkiGoogleRootMatch") is None:
        warnings.append("SPKI Google root comparison was not provided")

    return {
        "checks": checks,
        "policy": {
            "backendStrict": {
                "passed": not reasons,
                "reasons": reasons,
                "warnings": warnings,
            }
        },
        "notes": [
            "key possession and backend trust are separate claims",
            "exact Google root match and SPKI match are reported separately",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify normalized Android attestation report evidence against explicit offline policy checks.")
    parser.add_argument("report", type=Path)
    parser.add_argument("--root-diff", type=Path)
    parser.add_argument("--expected-challenge")
    parser.add_argument("--expected-attestation-security-level")
    parser.add_argument("--expected-keymaster-security-level")
    parser.add_argument("--expected-verified-boot-state")
    parser.add_argument("--min-chain-length", type=int, default=1)
    parser.add_argument("--require-device-locked", action="store_true")
    parser.add_argument("--require-exact-google-root", action="store_true", default=True)
    parser.add_argument("--allow-missing-exact-google-root", dest="require_exact_google_root", action="store_false")
    parser.add_argument("--require-spki-google-root", action="store_true", default=True)
    parser.add_argument("--allow-missing-spki-google-root", dest="require_spki_google_root", action="store_false")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    output = verify(read_json(args.report), read_json(args.root_diff), args)
    text = json.dumps(output, indent=2, sort_keys=True) + "\n"
    print(text, end="")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
