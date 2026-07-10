# UDP Protocol Workflow

## Why UDP Is Different

UDP does not provide sessions, ordering, retransmission, request/response
semantics, or application framing. The protocol may define all of that itself,
or may intentionally avoid it for realtime behavior.

## Analysis Steps

1. Group packets by 4-tuple: source IP/port and destination IP/port.
2. Split directions: client to server and server to client.
3. List payload lengths and first bytes.
4. Look for stable headers: magic bytes, version, type, flags, sequence numbers.
   Use:
   ```bash
   python3 udp-protocol-reverse-engineering/scripts/udp-field-candidates.py udp-summary.json --json-out udp-fields.json
   ```
5. Compare repeated actions in the app with packet bursts.
6. Check whether the payload looks encrypted/compressed:
   - high entropy
   - no stable prefixes
   - lengths aligned to block boundaries
   - nonce-like fields
7. Correlate with app code:
   - Java: `DatagramSocket`, `DatagramPacket`, `DatagramChannel`
   - Native: `sendto`, `recvfrom`, `sendmsg`, `recvmsg`, `connect`
8. Build a parser only after packet families are separated.

## Evidence To Preserve

- PCAP file hash
- capture command and interface
- device/app version
- account/test state
- action timeline
- flow summary JSON
- Frida logs matching packet timestamps

## Advanced Heuristics

- Compare client-to-server and server-to-client separately; field layouts often
  differ by direction.
- Cluster before inferring fields. Mixed packet types make counters and constants
  look noisy.
- Re-run field inference per cluster, not only over all payloads.
- If first bytes are stable but the rest is high entropy, suspect header +
  encrypted/compressed body.
- If lengths are stable and only a few byte offsets change, suspect opcode,
  counter, timestamp, flags, or checksum.
