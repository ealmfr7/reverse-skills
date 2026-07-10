#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected JSON object")
    return data


def sha256_base64(value: bytes) -> str:
    return base64.b64encode(hashlib.sha256(value).digest()).decode("ascii")


def cert_fingerprint(certificate: dict[str, Any]) -> dict[str, Any]:
    encoded = certificate.get("encoded_der_base64") or certificate.get("encodedDerBase64")
    result = {
        "subject": certificate.get("subject"),
        "issuer": certificate.get("issuer"),
        "serial": certificate.get("serial_number") or certificate.get("serialHex") or certificate.get("serial"),
        "attestationExtensionPresent": certificate.get("attestation_extension_present"),
    }
    if isinstance(encoded, str) and encoded:
        try:
            der = base64.b64decode(encoded, validate=True)
            result["derSha256Base64"] = sha256_base64(der)
            result["derLength"] = len(der)
        except Exception:
            result["derDecodeError"] = "invalid base64 DER"
    return {key: value for key, value in result.items() if value is not None}


def parse_report(report: dict[str, Any], source: Path) -> dict[str, Any]:
    key_attestation = report.get("key_attestation", {})
    if not isinstance(key_attestation, dict):
        key_attestation = {}
    certificates = key_attestation.get("certificates") or []
    if not isinstance(certificates, list):
        certificates = []

    parsed = key_attestation.get("parsed") or report.get("parsed_attestation") or {}
    if not isinstance(parsed, dict):
        parsed = {}
    checks = report.get("checks", {})
    if not isinstance(checks, dict):
        checks = {}

    chain_present = bool(
        key_attestation.get("chain_present")
        or key_attestation.get("chainPresent")
        or certificates
    )
    chain_length = key_attestation.get("chain_length", key_attestation.get("chainLength"))
    if not isinstance(chain_length, int):
        chain_length = len(certificates) if certificates else (1 if chain_present else 0)

    signals: list[str] = []
    if chain_present:
        signals.append("chain-present")
    if chain_length:
        signals.append(f"chain-length:{chain_length}")
    if key_attestation.get("requested_challenge") or parsed.get("attestationChallenge"):
        signals.append("challenge-present")
    if parsed.get("attestationSecurityLevel") or checks.get("attestationSecurityLevel"):
        signals.append("attestation-security-level-present")
    if parsed.get("keymasterSecurityLevel") or checks.get("keymasterSecurityLevel"):
        signals.append("keymaster-security-level-present")

    return {
        "source": str(source),
        "chainPresent": chain_present,
        "chainLength": chain_length,
        "requestedChallenge": key_attestation.get("requested_challenge"),
        "attestationChallenge": parsed.get("attestationChallenge"),
        "attestationSecurityLevel": parsed.get("attestationSecurityLevel") or checks.get("attestationSecurityLevel"),
        "keymasterSecurityLevel": parsed.get("keymasterSecurityLevel") or checks.get("keymasterSecurityLevel"),
        "rootOfTrust": parsed.get("rootOfTrust") or checks,
        "certificates": [
            cert_fingerprint(item)
            for item in certificates
            if isinstance(item, dict)
        ],
        "signals": signals,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse normalized Android Key Attestation fields from an offline report JSON.")
    parser.add_argument("report", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    output = parse_report(read_json(args.report), args.report)
    text = json.dumps(output, indent=2, sort_keys=True) + "\n"
    print(text, end="")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
