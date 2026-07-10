# UDP Protocol Lab Workflow

Use this workflow for an authorized app or service that speaks a custom UDP
protocol.

## Goal

Group UDP flows, infer packet families, correlate packets with app code, and
replay only against a lab endpoint.

## Flow

1. Capture:
   ```bash
   bash udp-protocol-reverse-engineering/scripts/capture-udp-tcpdump.sh any udp-capture.pcapng "udp"
   ```
2. Extract and summarize:
   ```bash
   bash udp-protocol-reverse-engineering/scripts/pcap-to-udp-json.sh udp-capture.pcapng udp-packets.json "udp"
   python3 udp-protocol-reverse-engineering/scripts/udp-json-summary.py udp-packets.json --json-out udp-summary.json
   python3 udp-protocol-reverse-engineering/scripts/udp-payload-cluster.py udp-summary.json --prefix-bytes 4 --json-out udp-clusters.json
   python3 udp-protocol-reverse-engineering/scripts/udp-field-candidates.py udp-summary.json --json-out udp-fields.json
   ```
3. Runtime correlation:
   ```bash
   python3 udp-protocol-reverse-engineering/scripts/make-frida-udp-hooks.py --mode both --out udp-hooks.js
   frida -U com.example.lab -l udp-hooks.js
   ```
4. If native parser or crypto appears:
   ```text
   Use rev-ghidra, android-arm64-native-basics, and android-frida-hooking.
   ```
5. Replay only in lab:
   ```bash
   python3 udp-protocol-reverse-engineering/scripts/replay-udp.py 127.0.0.1 9000 --hex 01020304
   ```

## Validation

- Flow summary identifies dominant 4-tuples and payload families.
- Frida logs correlate app actions to UDP payloads.
- Replay target is explicitly authorized and isolated.
