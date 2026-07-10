# Reverse Skills

This repository collects reverse engineering skills for Codex-style agents.

## Included skills

- `android-reversing-workflow`: master runbook that routes Android reversing tasks to the right skills.
- `web-api-reverse-engineering`: local skill for web API reverse engineering workflows.
- `rev-frida`: imported Frida instrumentation skill for runtime hooking and dynamic analysis.
- `rev-dex-dumper`: imported Android DEX memory dumping skill for packed or dynamically loaded apps.
- `rev-idapython`: imported IDAPython and IDALib reference skill for IDA automation.
- `rev-symbol`: imported symbol recovery skill for reverse engineering workflows.
- `rev-struct`: imported structure recovery skill for native reverse engineering.
- `rev-unicorn-debug`: imported Unicorn emulation skill for targeted binary debugging.
- `android-frida-hooking`: local skill for authorized Android Frida setup, Java/Kotlin hooks, native/JNI hooks, network hooks, crypto/storage hooks, and troubleshooting.
- `android-apk-patching`: local skill for authorized APK patch, rebuild, align, sign, install, and verification workflows.
- `android-traffic-analysis`: local skill for authorized Android proxy capture, TLS troubleshooting, and traffic documentation.
- `rev-ghidra`: local skill for Ghidra native binary analysis and headless automation.
- `android-objection`: local skill for Objection-based Android runtime exploration.
- `android-cross-platform-reversing`: local skill for Flutter, React Native, Cordova, Xamarin, and Unity APK triage.
- `android-malware-triage`: local defensive skill for suspicious APK triage and IOC extraction.
- `android-arm64-native-basics`: local skill for ARM64, JNI, offsets, pointers, and native hook interpretation.
- `udp-protocol-reverse-engineering`: local skill for authorized UDP PCAP analysis, payload clustering, Frida socket hooks, binary protocol inference, and lab replay.

Third-party skill sources are tracked in `THIRD_PARTY_SKILLS.md`.
