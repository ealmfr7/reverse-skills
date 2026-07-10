#!/usr/bin/env bash
set -euo pipefail

project="${1:-}"
out_dir="${2:-build}"
keystore="${3:-test.keystore}"
alias_name="${4:-androiddebugkey}"
password="${5:-android}"

if [ -z "$project" ]; then
    echo "Usage: $0 decoded-project [out-dir] [keystore] [alias] [password]" >&2
    exit 2
fi

mkdir -p "$out_dir"
unsigned="$out_dir/app-unsigned.apk"
aligned="$out_dir/app-aligned.apk"
signed="$out_dir/app-signed.apk"

apktool b "$project" -o "$unsigned"
zipalign -p -f 4 "$unsigned" "$aligned"
apksigner sign \
    --ks "$keystore" \
    --ks-key-alias "$alias_name" \
    --ks-pass "pass:$password" \
    --key-pass "pass:$password" \
    --out "$signed" \
    "$aligned"
apksigner verify --verbose "$signed"

echo "SIGNED:$signed"
