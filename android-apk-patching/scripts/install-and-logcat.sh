#!/usr/bin/env bash
set -euo pipefail

apk="${1:-}"
filter="${2:-}"
if [ -z "$apk" ]; then
    echo "Usage: $0 app-signed.apk [logcat-filter]" >&2
    exit 2
fi

adb install -r "$apk"
echo "INSTALLED:$apk"
echo "Starting logcat. Press Ctrl-C to stop."
if [ -n "$filter" ]; then
    adb logcat | grep --line-buffered -i "$filter"
else
    adb logcat
fi
