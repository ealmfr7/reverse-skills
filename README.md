# Reverse Skills

This repository collects reverse engineering skills for Codex-style agents.

## Repository Use Policy

Use these skills only for work that is in scope for the case: owned systems,
contracted testing, lab devices, CTFs, defensive research, incident response, or
other explicitly authorized analysis.

Do not use this repository to steal credentials or tokens, abuse third-party
services, bypass payment or account restrictions, evade rate limits, deploy or
improve malware, exfiltrate private data, or replay traffic against systems
outside scope.

Treat artifacts as evidence. Preserve original inputs, keep generated outputs
separate, cite stable artifact paths for findings, and redact secrets before
committing or sharing logs, HAR/PCAP files, screenshots, device identifiers,
private keys, cookies, session tokens, personal data, or customer data.

## Skill Index

### Master Router

| Skill | Purpose |
|---|---|
| `reverse-engineering-workflow` | Parent router for Android, web/API, UDP/protocol, native, docs, evidence, and probe tooling workflows. |
| `android-reversing-workflow` | Routes Android reversing goals to the right local skills and runbooks. |

## Stable CLI

Use `reverse-skill` to run bundled skill tools without long plugin cache paths:

```bash
reverse-skill list
reverse-skill list android-device-attestation-lab
reverse-skill path android-device-attestation-lab verify-attestation-report
reverse-skill android-device-attestation-lab verify-attestation-report report.json --root-diff root-diff.json
```

Install or refresh the CLI symlink:

```bash
bash scripts/install-reverse-skill.sh
```

Rebuild and reinstall the local plugin bundle:

```bash
bash scripts/build-local-plugin.sh
```

### Investigation Operations

| Skill | Purpose |
|---|---|
| `reverse-investigation-workflow` | Creates structured case folders, metadata, artifact indexes, run logs, and migration rules for professional reversing investigations. |
| `reverse-docs-workflow` | Organizes findings, hypotheses, decisions, experiments, runbooks, and reports with stable IDs, frontmatter, statuses, and indexes. |
| `reverse-probe-tooling-workflow` | Standardizes Frida probes, Python analyzers, JSONL event schemas, run folders, redaction, and probe output indexes. |

### Android Static and Dynamic Analysis

| Skill | Purpose |
|---|---|
| `android-frida-hooking` | Frida setup, Java/Kotlin hooks, native hooks, ClassLoaders, OkHttp/WebView, crypto/storage templates. |
| `rev-frida` | Third-party Frida reference for Java, ObjC, native hooks, memory, and module load timing. |
| `rev-dex-dumper` | DEX memory dumping for packed or dynamically loaded Android apps. |
| `android-anti-analysis-and-obfuscation` | Triage root/emulator/Frida detection, pinning, attestation, packing, obfuscation, and integrity checks. |
| `android-device-attestation-lab` | Device preflight, real-vs-VMOS comparison, KeyStore/keymaster attestation artifacts, root certificate checks, and backend trust lab flows. |
| `android-apk-patching` | APK decode, patch, rebuild, zipalign, sign, install, and logcat workflows. |
| `android-traffic-analysis` | Authorized Android HTTP/TLS proxy capture and traffic summaries. |
| `android-objection` | Objection-based interactive runtime exploration. |

### Cross-Platform APKs

| Skill | Purpose |
|---|---|
| `android-cross-platform-reversing` | Flutter, React Native/Hermes, Cordova/Capacitor, Xamarin, and Unity APK triage. |

### Native Reversing

| Skill | Purpose |
|---|---|
| `android-arm64-native-basics` | ARM64 registers, JNI mapping, offset math, and Frida native argument decoding. |
| `rev-ghidra` | Ghidra native analysis, headless scripts, function/string/import export, Frida offset hooks. |
| `rev-idapython` | Third-party IDAPython/IDALib reference for IDA automation. |
| `rev-symbol` | Function symbol/name recovery from patterns, strings, constants, and xrefs. |
| `rev-struct` | Native structure reconstruction from memory access patterns. |
| `rev-unicorn-debug` | Unicorn-based function emulation and native algorithm debugging. |

### Protocols and APIs

| Skill | Purpose |
|---|---|
| `web-api-reverse-engineering` | Browser/API reverse engineering: HAR, JS bundles, GraphQL, WebSocket, source maps, clients. |
| `udp-protocol-reverse-engineering` | UDP PCAP analysis, payload clustering, field inference, Frida socket hooks, QUIC/DTLS notes, lab replay. |

### Defensive Triage

| Skill | Purpose |
|---|---|
| `android-malware-triage` | Defensive suspicious APK triage and IOC extraction. |

## Examples

End-to-end lab workflows are documented in `docs/examples/`:

- `docs/examples/android-api-lab.md`
- `docs/examples/android-native-signing-lab.md`
- `docs/examples/udp-protocol-lab.md`

## Validation

Run the local test suite:

```bash
python3 -m unittest discover -s tests -v
```

Validate skill metadata:

```bash
reverse-skill list
```

Third-party skill sources are tracked in `THIRD_PARTY_SKILLS.md`.
