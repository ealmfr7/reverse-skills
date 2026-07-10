---
name: android-reversing-workflow
description: Master runbook for routing authorized Android reversing tasks to the right local skills. Use when Codex needs to choose between APK decompilation, packed DEX dumping, Frida hooking, traffic capture, APK patching, cross-platform triage, malware triage, native .so analysis, IDA/Ghidra, symbol/struct recovery, Unicorn emulation, or web/API reverse engineering.
---

# Android Reversing Workflow

Use this as the parent skill when the user has an Android APK/reversing goal but
the right technique is not obvious. Work only on authorized apps, labs, CTFs,
owned systems, or defensive samples.

## Router

| User goal / evidence | Use |
|---|---|
| First-pass APK structure, endpoints, manifest, Java/Kotlin | `android-reverse-engineering` |
| Need full Android workflow decision tree | this skill + `references/runbook.md` |
| APK is packed or JADX shows only stub/loader | `rev-dex-dumper` |
| Root/emulator/Frida detection, pinning, attestation, obfuscation | `android-anti-analysis-and-obfuscation` |
| Play Integrity/SafetyNet/KeyStore attestation, VMOS comparison, root certificate source, backend trust lab | `android-device-attestation-lab`, `android-anti-analysis-and-obfuscation` |
| Runtime method/function observation | `android-frida-hooking`, `rev-frida` |
| Quick interactive Frida exploration | `android-objection` |
| Capture HTTP/TLS traffic | `android-traffic-analysis`, `web-api-reverse-engineering` |
| Modify/rebuild/sign APK in lab | `android-apk-patching` |
| Flutter/RN/Cordova/Xamarin/Unity | `android-cross-platform-reversing` |
| Suspicious APK / malware IOC report | `android-malware-triage` |
| Native `.so` analysis with free tooling | `rev-ghidra` |
| Native `.so` analysis with IDA | `rev-idapython` |
| Native function names unknown | `rev-symbol` |
| Native data structures unclear | `rev-struct` |
| Need ARM64/JNI/offset explanation | `android-arm64-native-basics` |
| Emulate native function outside app | `rev-unicorn-debug` |
| UDP traffic, custom datagrams, QUIC/DTLS, sendto/recvfrom | `udp-protocol-reverse-engineering`, `android-frida-hooking`, `rev-ghidra` |

Read `references/runbook.md` for end-to-end flows.

## Tooling

When an APK is available, fingerprint it before choosing a route:

```bash
bash scripts/fingerprint-apk.sh app.apk > fingerprint.txt
python3 scripts/route-android-task.py --fingerprint fingerprint.txt
```

When only a text goal is available, route the description:

```bash
python3 scripts/route-android-task.py "hook login and inspect OkHttp traffic"
```

For more detailed routing logic, read `references/decision-tree.md`. For
concrete examples, read `references/examples.md`.

## Expected Output

Produce a short plan naming:

1. current evidence
2. selected skill(s)
3. first command/artifact to collect
4. validation signal
5. next branch if the first attempt fails
