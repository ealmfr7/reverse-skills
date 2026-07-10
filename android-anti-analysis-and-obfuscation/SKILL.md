---
name: android-anti-analysis-and-obfuscation
description: Triage and document Android APK anti-analysis, anti-debug, anti-Frida, root/emulator detection, certificate pinning, Play Integrity/SafetyNet/key attestation, packed DEX/loaders, string encryption, Java/Kotlin obfuscation, native integrity checks, and tamper protections. Use when Codex needs to analyze why an APK behaves differently on VMOS/emulators/rooted devices, detect Snapchat-like attestation or integrity failures, classify protections from JADX/apktool/Ghidra/logcat/Frida evidence, plan comparison experiments, or produce an evidence-backed anti-analysis report.
---

# Android Anti-Analysis and Obfuscation

Use this skill after first-pass APK triage when the app appears to detect the lab, block instrumentation, fail attestation, hide code, or change behavior under Frida/root/emulator conditions.

## Quick Start

Scan a JADX/apktool/decompiled tree or extracted strings:

```bash
python3 android-anti-analysis-and-obfuscation/scripts/scan-anti-analysis.py \
  path/to/decompiled-or-extracted \
  --json-out anti-analysis.json \
  --markdown-out anti-analysis.md
```

For a full case, combine:

1. `reverse-investigation-workflow`: create case and add APK, logs, screenshots, and runs.
2. `android-reversing-workflow`: fingerprint APK/static/native surfaces.
3. This skill: classify anti-analysis signals and plan controlled experiments.
4. `android-device-attestation-lab`: collect/compare device trust, KeyStore attestation, root certificate, and backend-trust artifacts when attestation is in scope.
5. `reverse-probe-tooling-workflow`: standardize Frida/logcat/strace probes.
6. `reverse-docs-workflow`: publish findings with evidence paths.

## Triage Order

1. **Static signals**: scan manifest, resources, decompiled Java/Kotlin, native strings, and package names.
2. **Environment baseline**: compare real device, emulator, VMOS/rooted, no-Frida, and Frida-attached runs.
3. **Runtime evidence**: collect logcat, UI state, network failures, attestation results, Frida bridge availability, and native traces.
4. **Protection class**: root, emulator, Frida, debugger, pinning, attestation, packing, obfuscation, integrity, or native checks.
5. **Evidence report**: record what was observed, where, under which environment, and what remains unverified.

## Protection Map

| Protection | Static clues | Runtime clues |
|---|---|---|
| Root detection | `su`, Magisk, BusyBox, root paths, mount checks | root-only failure, logcat root flags |
| Emulator/VM detection | `generic`, `goldfish`, `ranchu`, `sdk_gphone`, build prop checks | emulator-only denial |
| Frida/instrumentation detection | `frida`, `gum-js-loop`, Xposed, Substrate, `/proc/self/maps` scans | crash/exit on attach, Gum threads |
| Debug/native anti-debug | `ptrace`, `TracerPid`, `prctl`, `seccomp`, `syscall` | debugger attach failure |
| Certificate pinning | `CertificatePinner`, `TrustManager`, pin hashes, network security config | proxy fails while direct works |
| Play Integrity/SafetyNet/key attestation | `IntegrityManager`, `SafetyNet`, KeyStore attestation, keymaster | VMOS/root fails attestation |
| Packed DEX/loaders | DexClassLoader, encrypted assets, Jiagu/Bangcle/Legu/Protect names | code appears only at runtime |
| String/control obfuscation | tiny class names, encrypted strings, reflection-heavy dispatch | static xrefs are sparse |
| App integrity/tamper checks | signature digest, installer/source checks, CRC/hash comparisons | patched build behaves differently |

## Rules

- Prefer classification and evidence before attempting modifications.
- Compare environments instead of assuming one failure cause.
- Mark every conclusion as observed, inferred, or unverified.
- Store raw logs and traces as artifacts; summarize sensitive values in reports.

## Reference Routing

- Read `references/static-signals.md` for scan categories and keywords.
- Read `references/runtime-experiments.md` to plan real-vs-emulator/root/Frida comparisons.
- Read `references/attestation-notes.md` for Play Integrity, SafetyNet, KeyStore, and keymaster evidence.
- Read `references/report-template.md` when writing findings or a final anti-analysis report.
