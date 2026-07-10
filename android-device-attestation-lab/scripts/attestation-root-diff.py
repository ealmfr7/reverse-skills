#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_spki(value: str) -> tuple[str, str]:
    if ":" not in value:
        raise argparse.ArgumentTypeError("expected label:spki-sha256")
    return tuple(value.split(":", 1))  # type: ignore[return-value]


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare an attestation root against trusted root bytes and optional SPKI digests.")
    parser.add_argument("--local-root", type=Path, required=True)
    parser.add_argument("--trusted-root", type=Path, action="append", required=True)
    parser.add_argument("--local-spki-sha256")
    parser.add_argument("--trusted-spki-sha256", action="append", type=parse_spki, default=[])
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    local_sha = sha256_hex(args.local_root)
    trusted_roots = [
        {"label": path.stem, "path": str(path), "sha256": sha256_hex(path)}
        for path in args.trusted_root
    ]
    trusted_spki = dict(args.trusted_spki_sha256)
    exact_matches = [item for item in trusted_roots if item["sha256"] == local_sha]
    spki_matches = [
        {"label": label, "spkiSha256": digest}
        for label, digest in trusted_spki.items()
        if args.local_spki_sha256 and digest == args.local_spki_sha256
    ]
    output = {
        "localRoot": {
            "path": str(args.local_root),
            "sha256": local_sha,
            "spkiSha256": args.local_spki_sha256,
        },
        "rootComparison": {
            "exactGoogleRootMatch": bool(exact_matches),
            "exactMatches": exact_matches,
            "spkiGoogleRootMatch": bool(spki_matches),
            "spkiMatches": spki_matches,
        },
        "trustedRoots": trusted_roots,
        "trustedSpki": trusted_spki,
    }
    text = json.dumps(output, indent=2, sort_keys=True) + "\n"
    print(text, end="")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
