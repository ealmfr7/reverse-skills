#!/usr/bin/env bash
set -u
missing=0
for tool in apktool zipalign apksigner adb keytool; do
    if command -v "$tool" >/dev/null 2>&1; then
        printf 'OK:%s:%s\n' "$tool" "$(command -v "$tool")"
    else
        printf 'INSTALL_REQUIRED:%s\n' "$tool"
        missing=1
    fi
done
exit "$missing"
