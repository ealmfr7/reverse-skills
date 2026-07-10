# Router Matrix

Use this matrix to select child skills.

| Evidence or Goal | Primary Skill | Support Skills |
|---|---|---|
| APK, XAPK, AAB, DEX, JADX, package name | `android-reversing-workflow` | `reverse-investigation-workflow` |
| Runtime hooks, Java methods, native functions | `android-frida-hooking` | `rev-frida`, `reverse-probe-tooling-workflow` |
| URL, HAR, JS bundle, GraphQL, WebSocket | `web-api-reverse-engineering` | `reverse-docs-workflow` |
| UDP, PCAP, datagrams, custom protocol | `udp-protocol-reverse-engineering` | `reverse-probe-tooling-workflow` |
| `.so`, ARM64, JNI, offsets, symbols | `rev-ghidra` | `android-arm64-native-basics`, `rev-symbol`, `rev-struct` |
| Findings, decisions, reports, Markdown cleanup | `reverse-docs-workflow` | `reverse-investigation-workflow` |
| Frida scripts, analyzers, event JSONL, runs | `reverse-probe-tooling-workflow` | `android-frida-hooking` |

Always add `reverse-investigation-workflow` when artifacts need durable case structure.
