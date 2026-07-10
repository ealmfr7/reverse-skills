# End-to-End Flows

## Android App To Report

1. `reverse-investigation-workflow`: create case and add APK.
2. `android-reversing-workflow`: fingerprint and choose static/dynamic/native paths.
3. `android-frida-hooking` or `rev-ghidra`: collect runtime/native evidence.
4. `reverse-probe-tooling-workflow`: standardize probes and run outputs.
5. `reverse-docs-workflow`: create findings and report.

## Web API To Client

1. `reverse-investigation-workflow`: create case and add URL/HAR/JS artifacts.
2. `web-api-reverse-engineering`: fingerprint, summarize HAR, extract endpoints.
3. `reverse-docs-workflow`: document endpoint inventory and decisions.

## UDP Protocol Reconstruction

1. `reverse-investigation-workflow`: create case and add PCAP/run artifacts.
2. `udp-protocol-reverse-engineering`: summarize traffic and infer fields.
3. `reverse-probe-tooling-workflow`: standardize packet capture hooks/analyzers.
4. `reverse-docs-workflow`: publish findings and limitations.

## Mixed Android Web/API

Use Android skills to find request construction and web/API skills to document the protocol. Keep both under the same case when the target app and goal are the same.
