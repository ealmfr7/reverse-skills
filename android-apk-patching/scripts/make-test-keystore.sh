#!/usr/bin/env bash
set -euo pipefail

out="${1:-test.keystore}"
alias_name="${2:-androiddebugkey}"
password="${3:-android}"

keytool -genkeypair \
    -keystore "$out" \
    -storepass "$password" \
    -keypass "$password" \
    -alias "$alias_name" \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -dname "CN=Android Test,O=Lab,C=US"

echo "KEYSTORE:$out"
echo "ALIAS:$alias_name"
