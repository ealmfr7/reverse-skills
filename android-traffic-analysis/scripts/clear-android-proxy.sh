#!/usr/bin/env bash
set -euo pipefail

adb shell settings delete global http_proxy >/dev/null 2>&1 || true
adb shell settings put global http_proxy :0 >/dev/null 2>&1 || true
echo "PROXY_CLEARED"
