# Frida UDP Hooks

## Java Layer

Hook Java UDP APIs when the app uses Java networking:

- `java.net.DatagramSocket.send`
- `java.net.DatagramSocket.receive`
- `java.net.DatagramPacket`
- `java.nio.channels.DatagramChannel`

Generate template:

```bash
python3 udp-protocol-reverse-engineering/scripts/make-frida-udp-hooks.py --mode java --out udp-java.js
```

## Native Layer

Hook native socket APIs when Java hooks do not fire or the app uses native code:

- `sendto`
- `recvfrom`
- `sendmsg`
- `recvmsg`
- `connect`

Generate template:

```bash
python3 udp-protocol-reverse-engineering/scripts/make-frida-udp-hooks.py --mode native --out udp-native.js
```

## Correlation

Use both PCAP and Frida:

- PCAP shows real network bytes and timing.
- Frida shows pre-send buffers, post-recv buffers, call stacks, and code path.

If PCAP payload differs from Frida buffer, encryption/compression/framing may
occur below or above the hook point.
