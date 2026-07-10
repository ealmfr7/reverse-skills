# Reverse Skills

This repository collects reverse engineering skills for Codex-style agents.

## Skill Index

### Master Router

| Skill | Purpose |
|---|---|
| `reverse-engineering-workflow` | Parent router for Android, web/API, UDP/protocol, native, docs, evidence, and probe tooling workflows. |
| `android-reversing-workflow` | Routes Android reversing goals to the right local skills and runbooks. |

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
for d in */SKILL.md; do
  python3 /home/ubuntu/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$(dirname "$d")"
done
```

Third-party skill sources are tracked in `THIRD_PARTY_SKILLS.md`.
