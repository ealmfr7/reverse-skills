#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_state(path: Path) -> dict[str, Any]:
    state = read_json(path)
    state.setdefault("nonces", {})
    state.setdefault("devices", {})
    state.setdefault("challenges", {})
    return state


def backend_strict_passed(verification: dict[str, Any]) -> bool:
    return bool(verification.get("policy", {}).get("backendStrict", {}).get("passed"))


def synthetic_signature(challenge: str, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), challenge.encode("utf-8"), hashlib.sha256).hexdigest()


def cmd_issue_nonce(args: argparse.Namespace) -> dict[str, Any]:
    state = load_state(args.state)
    nonce = secrets.token_urlsafe(24)
    state["nonces"][args.device_id] = {"issuedAt": now(), "nonce": nonce}
    write_json(args.state, state)
    return {"deviceId": args.device_id, "nonce": nonce}


def cmd_register(args: argparse.Namespace) -> dict[str, Any]:
    state = load_state(args.state)
    verification = read_json(args.verification)
    trusted = backend_strict_passed(verification)
    reasons = verification.get("policy", {}).get("backendStrict", {}).get("reasons", [])
    state["devices"][args.device_id] = {
        "backendReasons": reasons,
        "backendTrusted": trusted,
        "keyId": args.key_id,
        "registeredAt": now(),
        "secret": args.secret,
    }
    state["nonces"].pop(args.device_id, None)
    write_json(args.state, state)
    return {
        "backendTrusted": trusted,
        "deviceId": args.device_id,
        "reasons": reasons,
        "registered": trusted,
    }


def cmd_issue_challenge(args: argparse.Namespace) -> dict[str, Any]:
    state = load_state(args.state)
    if args.device_id not in state["devices"]:
        raise SystemExit(f"device is not registered: {args.device_id}")
    challenge = secrets.token_urlsafe(24)
    state["challenges"][args.device_id] = {"challenge": challenge, "issuedAt": now()}
    write_json(args.state, state)
    return {"challenge": challenge, "deviceId": args.device_id}


def cmd_sign(args: argparse.Namespace) -> dict[str, Any]:
    return {"challenge": args.challenge, "signature": synthetic_signature(args.challenge, args.secret)}


def cmd_verify_signature(args: argparse.Namespace) -> dict[str, Any]:
    state = load_state(args.state)
    device = state["devices"].get(args.device_id)
    challenge = state["challenges"].get(args.device_id)
    if not device:
        raise SystemExit(f"device is not registered: {args.device_id}")
    if not challenge:
        raise SystemExit(f"no pending challenge for device: {args.device_id}")
    expected = synthetic_signature(challenge["challenge"], device["secret"])
    signature_valid = hmac.compare_digest(expected, args.signature)
    backend_trusted = bool(device.get("backendTrusted"))
    return {
        "accepted": signature_valid and backend_trusted,
        "backendTrusted": backend_trusted,
        "deviceId": args.device_id,
        "notes": ["key possession and backend trust are separate claims"],
        "signatureValid": signature_valid,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Synthetic local backend lab for Android attestation trust experiments.")
    sub = parser.add_subparsers(dest="command", required=True)

    issue_nonce = sub.add_parser("issue-nonce")
    issue_nonce.add_argument("--state", type=Path, required=True)
    issue_nonce.add_argument("--device-id", required=True)

    register = sub.add_parser("register")
    register.add_argument("--state", type=Path, required=True)
    register.add_argument("--device-id", required=True)
    register.add_argument("--verification", type=Path, required=True)
    register.add_argument("--key-id", required=True)
    register.add_argument("--secret", required=True)

    issue_challenge = sub.add_parser("issue-challenge")
    issue_challenge.add_argument("--state", type=Path, required=True)
    issue_challenge.add_argument("--device-id", required=True)

    sign = sub.add_parser("sign")
    sign.add_argument("--challenge", required=True)
    sign.add_argument("--secret", required=True)

    verify = sub.add_parser("verify-signature")
    verify.add_argument("--state", type=Path, required=True)
    verify.add_argument("--device-id", required=True)
    verify.add_argument("--signature", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    handlers = {
        "issue-challenge": cmd_issue_challenge,
        "issue-nonce": cmd_issue_nonce,
        "register": cmd_register,
        "sign": cmd_sign,
        "verify-signature": cmd_verify_signature,
    }
    print(json.dumps(handlers[args.command](args), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
