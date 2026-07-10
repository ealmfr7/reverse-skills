#!/usr/bin/env bash
set -euo pipefail

pcap="${1:-}"
filter="${2:-udp}"

if [ -z "$pcap" ]; then
    echo "Usage: $0 capture.pcapng [display-filter]" >&2
    exit 2
fi

echo "== UDP conversations =="
tshark -r "$pcap" -Y "$filter" -q -z conv,udp || true
echo
echo "== IP endpoints =="
tshark -r "$pcap" -Y "$filter" -q -z endpoints,ip || true
echo
echo "== Protocol hierarchy =="
tshark -r "$pcap" -Y "$filter" -q -z io,phs || true
