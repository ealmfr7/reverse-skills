---
name: android-traffic-analysis
description: Capture, inspect, and document Android app network traffic. Use when Codex needs mitmproxy, Burp, HTTP Toolkit, adb proxy configuration, emulator proxy setup, user/system CA trust, Android Network Security Config, HAR/flow review, OkHttp correlation, TLS troubleshooting, or traffic-to-client reproduction.
---

# Android Traffic Analysis

## Workflow

1. Clarify capture goal: endpoint inventory, auth flow, request signing, WebView,
   GraphQL, WebSocket, TLS failure, or client reproduction.
2. Run:
   ```bash
   bash scripts/check-traffic-deps.sh
   ```
3. Pick capture method:
   - Browser/WebView or normal HTTP: proxy with mitmproxy/Burp/HTTP Toolkit.
   - App rejects proxy cert: inspect Network Security Config and TLS behavior.
   - Data encrypted before HTTP: use `android-frida-hooking` or app-layer hooks.
4. Configure emulator/device proxy and install the test CA for the test device.
   ```bash
   bash scripts/set-android-proxy.sh 10.0.2.2 8080
   ```
5. Capture baseline action once, save flow/HAR, and document app state.
6. Summarize capture:
   ```bash
   python3 scripts/summarize-traffic.py capture.har --json-out traffic-summary.json
   ```
7. Correlate traffic with code using JADX or Frida hooks when needed.
8. Clear proxy after the test:
   ```bash
   bash scripts/clear-android-proxy.sh
   ```

Read `references/workflow.md` for setup and troubleshooting.

## Script Outputs

- `scripts/check-traffic-deps.sh`: reports available capture tools.
- `scripts/set-android-proxy.sh [host] [port]`: sets Android global HTTP proxy.
- `scripts/clear-android-proxy.sh`: clears Android global HTTP proxy.
- `scripts/summarize-traffic.py <capture.har|mitm.json>`: emits endpoint,
  GraphQL, and WebSocket counts without secret values.

## Source Anchors

- mitmproxy certificates: https://docs.mitmproxy.org/stable/concepts/certificates/
- mitmproxy Android system CA: https://docs.mitmproxy.org/stable/howto/install-system-trusted-ca-android/
- Android Network Security Config: https://developer.android.com/privacy-and-security/security-config
- Android TLS guidance: https://developer.android.com/privacy-and-security/security-ssl
