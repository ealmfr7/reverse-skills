# QUIC, DTLS, and Encrypted UDP

## QUIC

QUIC runs over UDP and is normally encrypted. Wireshark/tshark can identify QUIC
traffic, but application payload inspection requires keys or app-layer hooks.
For Android apps, correlate QUIC libraries or Cronet/HTTP3 usage with Frida and
native analysis.

QUIC is standardized in RFC 9000. QUIC DATAGRAM frames are standardized in RFC
9221 and provide unreliable datagrams inside an encrypted QUIC connection. If a
capture shows QUIC, do not assume the visible UDP datagram payload is the
application payload.

Useful routes:

- Identify QUIC with Wireshark/tshark display filter `quic`.
- If the app/runtime can export TLS secrets, configure Wireshark with an
  SSLKEYLOGFILE-style key log.
- If key logs are unavailable, hook app-layer plaintext before QUIC encryption
  or after QUIC decryption.
- For implementations that support qlog, collect qlog event traces and correlate
  them with PCAP timing.

## DTLS

DTLS is TLS-like security over datagrams. Treat it as encrypted unless keys or
app-layer plaintext hooks are available.

## Custom Encrypted UDP

Look for:

- crypto APIs before send path
- nonce/counter fields in packet headers
- fixed-size authentication tags
- key exchange or session setup packets

Prefer observing plaintext at app-layer function boundaries instead of trying to
break cryptography.

## Practical Android Signals

Look for Cronet, HTTP/3, QUIC, or native networking libraries in:

- Java package/class names
- native library names
- strings in `.so` files
- Frida `System.loadLibrary` logs
- `sendto`/`recvfrom` hooks showing UDP traffic from native code
