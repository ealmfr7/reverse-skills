---
name: reverse-engineering-workflow
description: Parent router for authorized reverse engineering work across Android APKs, web/API targets, UDP/protocol captures, native binaries, Frida probes, documentation, evidence, and reporting. Use when Codex needs to choose which reverse engineering skills to apply, plan an end-to-end workflow, decide whether work belongs in Android, web, protocol, investigation, docs, or probe tooling skills, or coordinate multiple skills for apps such as Likee, Bigo, web clients, PCAP/HAR captures, scripts, findings, and reports.
---

# Reverse Engineering Workflow

Use this as the top-level router before selecting specialized skills. It should answer: what is the target, what artifacts exist, what workflow layer is needed, and which child skills should be loaded next.

## Quick Route

Run the deterministic router when the goal or artifacts are available:

```bash
python3 reverse-engineering-workflow/scripts/route-reversing-task.py \
  "analyze APK, hook Frida login, inspect UDP media traffic, write findings" \
  --artifact app.apk \
  --artifact capture.pcap
```

Use `--json` when another script or report needs structured output.

## Skill Map

| Situation | Use |
|---|---|
| Any serious investigation with artifacts/runs/evidence | `reverse-investigation-workflow` |
| Android APK/XAPK/AAB/JAR/AAR, mobile app static/dynamic analysis | `android-reversing-workflow` |
| Root/emulator/Frida detection, pinning, attestation, packing, obfuscation | `android-anti-analysis-and-obfuscation` |
| Frida hooks, runtime observation, Java/native methods | `android-frida-hooking`, `rev-frida`, `reverse-probe-tooling-workflow` |
| Web URL, HAR, JS bundle, GraphQL, WebSocket, browser API flow | `web-api-reverse-engineering` |
| UDP, PCAP, datagrams, QUIC/DTLS/custom binary protocol | `udp-protocol-reverse-engineering` |
| Native `.so`, ARM64, symbols, structs, emulation | `rev-ghidra`, `android-arm64-native-basics`, `rev-symbol`, `rev-struct`, `rev-unicorn-debug` |
| Findings, hypotheses, decisions, reports, migration of docs | `reverse-docs-workflow` |
| Probe/analyzer scaffolding, event schema, run output format | `reverse-probe-tooling-workflow` |
| Suspicious APK defensive triage | `android-malware-triage` |

## Default Workflow

1. Confirm authorization and scope.
2. Create or select a case with `reverse-investigation-workflow`.
3. Route the technical domain: Android, web/API, UDP/protocol, native, or mixed.
4. Standardize scripts/probes with `reverse-probe-tooling-workflow` when dynamic tooling is created.
5. Store outputs as run artifacts and generate evidence indexes.
6. Promote durable claims into `reverse-docs-workflow`.
7. Produce a report that cites evidence paths, run indexes, and findings.

## Routing Rules

- If the user mentions an APK, package, Frida, JADX, DEX, `lib*.so`, or Android device, include `android-reversing-workflow`.
- If the user mentions root/emulator/Frida detection, pinning, attestation, integrity, anti-debug, packing, or obfuscation, include `android-anti-analysis-and-obfuscation`.
- If the user mentions URL, HAR, JavaScript bundle, GraphQL, WebSocket, DevTools, browser, curl, or API client, include `web-api-reverse-engineering`.
- If the user mentions UDP, PCAP, datagrams, packets, QUIC, DTLS, `sendto`, `recvfrom`, or protocol reconstruction, include `udp-protocol-reverse-engineering`.
- If the user mentions scripts, probes, Frida script cleanup, analyzer, event schema, JSONL, run output, or reusable tooling, include `reverse-probe-tooling-workflow`.
- If the user mentions docs, findings, report, decision, hypothesis, index, or messy Markdown, include `reverse-docs-workflow`.
- For mixed mobile app API work, use both Android and web/API skills.

## Reference Routing

- Read `references/router-matrix.md` for detailed artifact-to-skill mapping.
- Read `references/end-to-end-flows.md` for combined Android, web, UDP, docs, and probe workflows.
- Read `references/case-splitting.md` when deciding whether Likee, Bigo, versions, or comparisons need separate cases.
