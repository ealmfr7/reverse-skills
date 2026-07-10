#!/usr/bin/env bash
set -euo pipefail

iface="${1:-any}"
out="${2:-udp-capture.pcapng}"
expr="${3:-udp}"

echo "CAPTURE:$iface -> $out filter=$expr"
tcpdump -i "$iface" -s 0 -w "$out" "$expr"
