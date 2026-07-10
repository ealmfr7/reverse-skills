#!/usr/bin/env bash
set -euo pipefail

host="${1:-10.0.2.2}"
port="${2:-8080}"

adb shell settings put global http_proxy "$host:$port"
echo "PROXY_SET:$host:$port"
