#!/usr/bin/env bash
set -u
missing=0
for tool in adb mitmproxy mitmdump curl; do
    if command -v "$tool" >/dev/null 2>&1; then
        printf 'OK:%s:%s\n' "$tool" "$(command -v "$tool")"
    else
        printf 'INSTALL_OPTIONAL:%s\n' "$tool"
    fi
done
exit "$missing"
