#!/usr/bin/env bash
set -euo pipefail

apk="${1:-}"
out="${2:-}"
if [ -z "$apk" ] || [ -z "$out" ]; then
    echo "Usage: $0 app.apk work/app" >&2
    exit 2
fi

apktool d "$apk" -o "$out" -f
echo "DECODED:$out"
