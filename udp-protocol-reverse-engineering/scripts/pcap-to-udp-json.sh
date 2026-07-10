#!/usr/bin/env bash
set -euo pipefail

pcap="${1:-}"
out="${2:-udp-packets.json}"
filter="${3:-udp}"

if [ -z "$pcap" ]; then
    echo "Usage: $0 capture.pcapng [out.json] [display-filter]" >&2
    exit 2
fi

tshark -r "$pcap" -Y "$filter" -T json \
    -e frame.time_epoch \
    -e frame.len \
    -e ip.src \
    -e ip.dst \
    -e ipv6.src \
    -e ipv6.dst \
    -e udp.srcport \
    -e udp.dstport \
    -e udp.length \
    -e udp.payload \
    > "$out"

echo "WROTE:$out"
