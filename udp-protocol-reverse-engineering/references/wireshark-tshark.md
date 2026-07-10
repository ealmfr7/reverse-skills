# Wireshark and TShark

## Capture

Use tcpdump for capture when GUI access is not available:

```bash
tcpdump -i any -s 0 -w udp-capture.pcapng udp
```

Use narrow filters when scope is known:

```bash
tcpdump -i any -s 0 -w app-udp.pcapng 'udp and host 10.0.0.5 and port 9000'
```

## Extract UDP Fields

```bash
tshark -r udp-capture.pcapng -Y 'udp' -T json \
  -e frame.time_epoch \
  -e frame.len \
  -e ip.src \
  -e ip.dst \
  -e udp.srcport \
  -e udp.dstport \
  -e udp.length \
  -e udp.payload \
  > udp-packets.json
```

Use the wrapper:

```bash
bash udp-protocol-reverse-engineering/scripts/pcap-to-udp-json.sh capture.pcapng udp-packets.json 'udp'
```

## Useful Display Filters

```text
udp
udp.port == 9000
ip.addr == 10.0.0.5 && udp
udp.length > 100
quic
dtls
```

## Statistics

```bash
bash udp-protocol-reverse-engineering/scripts/tshark-udp-stats.sh capture.pcapng 'udp'
```

This wraps:

```bash
tshark -r capture.pcapng -Y 'udp' -q -z conv,udp
tshark -r capture.pcapng -Y 'udp' -q -z endpoints,ip
tshark -r capture.pcapng -Y 'udp' -q -z io,phs
```

Use stats before packet-level work to identify dominant endpoints, bursts, and
protocol dissector hints.
