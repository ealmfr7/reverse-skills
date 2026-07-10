# Android Traffic Workflow

## Proxy Commands

Emulator:

```bash
bash android-traffic-analysis/scripts/set-android-proxy.sh 10.0.2.2 8080
bash android-traffic-analysis/scripts/clear-android-proxy.sh
```

Physical device: use Wi-Fi proxy settings or a test network where the proxy host
is reachable.

## Capture Notes

- Record package name, app version, account role, timestamp, and action.
- Export mitmproxy flows or HAR before analysis.
- Summarize exported traffic:
  ```bash
  python3 android-traffic-analysis/scripts/summarize-traffic.py capture.har --json-out traffic-summary.json
  ```
- Treat missing traffic as evidence: the app may use native sockets, gRPC,
  WebSocket, certificate pinning, QUIC, or pre-HTTP encryption.

## Summary Output

`summarize-traffic.py` supports HAR and simple mitmproxy JSON exports. It stores:

- HTTP endpoints by method, scheme, host, path, status, and count.
- GraphQL operation names from JSON request bodies.
- WebSocket endpoints by host/path.

It removes query strings and does not copy request headers or body values into
the summary.

## Troubleshooting

- Browser works but app fails: app trust config or certificate pinning differs.
- No traffic appears: proxy not configured, app bypasses proxy, VPN active, or
  native stack ignores system proxy.
- CONNECT failures: inspect TLS trust and SNI/hostname mismatch.
- Response body unreadable: compression, protobuf, custom crypto, or binary API.
