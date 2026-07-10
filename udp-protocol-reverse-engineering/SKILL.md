---
name: udp-protocol-reverse-engineering
description: Analyze UDP protocols from PCAPs, Android apps, native binaries, Frida hooks, and lab replays. Use when Codex needs UDP packet capture, tshark/Wireshark filters, UDP flow extraction, payload clustering, binary protocol inference, sendto/recvfrom or DatagramSocket hooks, QUIC/DTLS/custom UDP triage, replay behavior, Scapy/socket replay, or correlation between UDP payloads and app code.
---

# UDP Protocol Reverse Engineering

Use this skill for UDP protocol analysis from captures, app code, and controlled
replay experiments.

## Workflow

1. Confirm target context: target app/system, capture source, IPs/ports,
   account/test environment, and replay plan.
2. Capture or receive a PCAP:
   ```bash
   reverse-skill udp-protocol-reverse-engineering capture-udp-tcpdump any udp-capture.pcapng "udp"
   ```
3. Convert PCAP to UDP JSON:
   ```bash
   reverse-skill udp-protocol-reverse-engineering pcap-to-udp-json udp-capture.pcapng udp-packets.json "udp"
   ```
4. Summarize flows and payload prefixes:
   ```bash
   reverse-skill udp-protocol-reverse-engineering udp-json-summary udp-packets.json --json-out udp-summary.json
   reverse-skill udp-protocol-reverse-engineering udp-payload-cluster udp-summary.json --prefix-bytes 4 --json-out udp-clusters.json
   reverse-skill udp-protocol-reverse-engineering udp-field-candidates udp-summary.json --json-out udp-fields.json
   ```
5. Correlate with runtime behavior:
   ```bash
   reverse-skill udp-protocol-reverse-engineering make-frida-udp-hooks --mode both --out udp-hooks.js
   frida -U com.example.app -l udp-hooks.js
   ```
6. If payloads are custom binary, inspect lengths, magic bytes, counters,
   timestamps, endianness, compression, encryption, and checksums before replay.
7. Replay against the selected test endpoint:
   ```bash
   reverse-skill udp-protocol-reverse-engineering replay-udp 127.0.0.1 9000 --hex 01020304
   ```

## Reference Routing

- PCAP/tshark capture and display filters: `references/wireshark-tshark.md`
- UDP analysis process: `references/udp-protocol-workflow.md`
- Binary payload patterns: `references/binary-protocol-patterns.md`
- Frida socket hooks: `references/frida-udp-hooks.md`
- QUIC/DTLS/custom encrypted UDP: `references/quic-dtls-notes.md`
- Replay process: `references/replay-safety.md`

## Script Outputs

- `check-udp-deps.sh`: reports optional tooling.
- `pcap-to-udp-json.sh`: writes tshark JSON with UDP fields.
- `udp-json-summary.py`: summarizes UDP flows, payload lengths, prefixes, and
  exports payloads for clustering.
- `udp-payload-cluster.py`: clusters payloads by length and prefix.
- `udp-field-candidates.py`: identifies constant byte offsets, byte entropy, and
  simple monotonic counter candidates in aligned payload samples.
- `tshark-udp-stats.sh`: prints tshark UDP conversations, IP endpoints, and
  protocol hierarchy stats.
- `make-frida-udp-hooks.py`: generates native `sendto`/`recvfrom` and Java
  `DatagramSocket` hooks.
- `replay-udp.py`: sends one payload to a selected endpoint.

## Source Anchors

- TShark manual: https://www.wireshark.org/docs/man-pages/tshark.html
- Wireshark display filters: https://www.wireshark.org/docs/man-pages/wireshark-filter.html
- Wireshark Display Filter Reference: https://www.wireshark.org/docs/dfref/
- tcpdump capture guidance: https://www.wireshark.org/docs/wsug_html_chunked/AppToolstcpdump.html
- Scapy usage: https://scapy.readthedocs.io/en/latest/usage.html
- Frida JavaScript API: https://frida.re/docs/javascript-api/
- QUIC transport RFC 9000: https://datatracker.ietf.org/doc/rfc9000/
- QUIC DATAGRAM RFC 9221: https://datatracker.ietf.org/doc/html/rfc9221
