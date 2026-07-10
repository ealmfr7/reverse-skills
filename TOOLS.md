# Reverse Skill Tool Index

Generated from local skill `scripts/` directories. Run:

```bash
python3 scripts/generate-tools-index.py --out TOOLS.md
```

## android-anti-analysis-and-obfuscation

| Tool | Command |
|---|---|
| `scan-anti-analysis` | `reverse-skill android-anti-analysis-and-obfuscation scan-anti-analysis` |

## android-apk-patching

| Tool | Command |
|---|---|
| `add-network-security-config` | `reverse-skill android-apk-patching add-network-security-config` |
| `check-apk-patching-deps` | `reverse-skill android-apk-patching check-apk-patching-deps` |
| `decode-apk` | `reverse-skill android-apk-patching decode-apk` |
| `install-and-logcat` | `reverse-skill android-apk-patching install-and-logcat` |
| `make-test-keystore` | `reverse-skill android-apk-patching make-test-keystore` |
| `rebuild-sign-apk` | `reverse-skill android-apk-patching rebuild-sign-apk` |

## android-arm64-native-basics

| Tool | Command |
|---|---|
| `offset-math` | `reverse-skill android-arm64-native-basics offset-math` |

## android-cross-platform-reversing

| Tool | Command |
|---|---|
| `extract-framework-assets` | `reverse-skill android-cross-platform-reversing extract-framework-assets` |
| `fingerprint-framework` | `reverse-skill android-cross-platform-reversing fingerprint-framework` |

## android-device-attestation-lab

| Tool | Command |
|---|---|
| `android-env-capture` | `reverse-skill android-device-attestation-lab android-env-capture` |
| `android-target-preflight` | `reverse-skill android-device-attestation-lab android-target-preflight` |
| `attestation-artifact-summary` | `reverse-skill android-device-attestation-lab attestation-artifact-summary` |
| `attestation-backend-lab` | `reverse-skill android-device-attestation-lab attestation-backend-lab` |
| `attestation-report` | `reverse-skill android-device-attestation-lab attestation-report` |
| `attestation-root-diff` | `reverse-skill android-device-attestation-lab attestation-root-diff` |
| `attestation-root-source-probe` | `reverse-skill android-device-attestation-lab attestation-root-source-probe` |
| `compare-attestation-runs` | `reverse-skill android-device-attestation-lab compare-attestation-runs` |
| `parse-android-key-attestation` | `reverse-skill android-device-attestation-lab parse-android-key-attestation` |
| `templates/frida-keymaster-trace` | `reverse-skill android-device-attestation-lab templates/frida-keymaster-trace` |
| `templates/frida-keystore-trace` | `reverse-skill android-device-attestation-lab templates/frida-keystore-trace` |
| `verify-attestation-report` | `reverse-skill android-device-attestation-lab verify-attestation-report` |

## android-frida-hooking

| Tool | Command |
|---|---|
| `check-frida-android` | `reverse-skill android-frida-hooking check-frida-android` |
| `make-java-hook` | `reverse-skill android-frida-hooking make-java-hook` |
| `make-native-hook` | `reverse-skill android-frida-hooking make-native-hook` |
| `templates/base64-hook` | `reverse-skill android-frida-hooking templates/base64-hook` |
| `templates/classloader-hook` | `reverse-skill android-frida-hooking templates/classloader-hook` |
| `templates/constructor-hook` | `reverse-skill android-frida-hooking templates/constructor-hook` |
| `templates/crypto-hook` | `reverse-skill android-frida-hooking templates/crypto-hook` |
| `templates/dexclassloader-hook` | `reverse-skill android-frida-hooking templates/dexclassloader-hook` |
| `templates/dlopen-hook` | `reverse-skill android-frida-hooking templates/dlopen-hook` |
| `templates/file-io-hook` | `reverse-skill android-frida-hooking templates/file-io-hook` |
| `templates/java-method-hook` | `reverse-skill android-frida-hooking templates/java-method-hook` |
| `templates/java-overloads-hook` | `reverse-skill android-frida-hooking templates/java-overloads-hook` |
| `templates/native-export-hook` | `reverse-skill android-frida-hooking templates/native-export-hook` |
| `templates/okhttp-hook` | `reverse-skill android-frida-hooking templates/okhttp-hook` |
| `templates/register-natives-hook` | `reverse-skill android-frida-hooking templates/register-natives-hook` |
| `templates/sharedprefs-hook` | `reverse-skill android-frida-hooking templates/sharedprefs-hook` |
| `templates/stacktrace-hook` | `reverse-skill android-frida-hooking templates/stacktrace-hook` |
| `templates/system-loadlibrary-hook` | `reverse-skill android-frida-hooking templates/system-loadlibrary-hook` |
| `templates/webview-hook` | `reverse-skill android-frida-hooking templates/webview-hook` |

## android-malware-triage

| Tool | Command |
|---|---|
| `apk-ioc-scan` | `reverse-skill android-malware-triage apk-ioc-scan` |

## android-reversing-workflow

| Tool | Command |
|---|---|
| `fingerprint-apk` | `reverse-skill android-reversing-workflow fingerprint-apk` |
| `route-android-task` | `reverse-skill android-reversing-workflow route-android-task` |

## android-traffic-analysis

| Tool | Command |
|---|---|
| `check-traffic-deps` | `reverse-skill android-traffic-analysis check-traffic-deps` |
| `clear-android-proxy` | `reverse-skill android-traffic-analysis clear-android-proxy` |
| `set-android-proxy` | `reverse-skill android-traffic-analysis set-android-proxy` |
| `summarize-traffic` | `reverse-skill android-traffic-analysis summarize-traffic` |

## rev-ghidra

| Tool | Command |
|---|---|
| `check-ghidra-deps` | `reverse-skill rev-ghidra check-ghidra-deps` |
| `ghidra/export_functions` | `reverse-skill rev-ghidra ghidra/export_functions` |
| `ghidra/export_imports` | `reverse-skill rev-ghidra ghidra/export_imports` |
| `ghidra/export_strings` | `reverse-skill rev-ghidra ghidra/export_strings` |
| `ghidra-run-headless` | `reverse-skill rev-ghidra ghidra-run-headless` |
| `make-frida-offset-hooks` | `reverse-skill rev-ghidra make-frida-offset-hooks` |

## reverse-docs-workflow

| Tool | Command |
|---|---|
| `index-docs` | `reverse-skill reverse-docs-workflow index-docs` |
| `init-docs` | `reverse-skill reverse-docs-workflow init-docs` |
| `lint-docs` | `reverse-skill reverse-docs-workflow lint-docs` |
| `mark-superseded` | `reverse-skill reverse-docs-workflow mark-superseded` |
| `new-decision` | `reverse-skill reverse-docs-workflow new-decision` |
| `new-finding` | `reverse-skill reverse-docs-workflow new-finding` |

## reverse-engineering-workflow

| Tool | Command |
|---|---|
| `route-reversing-task` | `reverse-skill reverse-engineering-workflow route-reversing-task` |

## reverse-investigation-workflow

| Tool | Command |
|---|---|
| `add-artifact` | `reverse-skill reverse-investigation-workflow add-artifact` |
| `index-artifacts` | `reverse-skill reverse-investigation-workflow index-artifacts` |
| `init-attestation-runs` | `reverse-skill reverse-investigation-workflow init-attestation-runs` |
| `init-case` | `reverse-skill reverse-investigation-workflow init-case` |
| `new-run` | `reverse-skill reverse-investigation-workflow new-run` |

## reverse-probe-tooling-workflow

| Tool | Command |
|---|---|
| `index-run` | `reverse-skill reverse-probe-tooling-workflow index-run` |
| `init-run` | `reverse-skill reverse-probe-tooling-workflow init-run` |
| `lint-events` | `reverse-skill reverse-probe-tooling-workflow lint-events` |
| `new-analyzer` | `reverse-skill reverse-probe-tooling-workflow new-analyzer` |
| `new-probe` | `reverse-skill reverse-probe-tooling-workflow new-probe` |

## udp-protocol-reverse-engineering

| Tool | Command |
|---|---|
| `capture-udp-tcpdump` | `reverse-skill udp-protocol-reverse-engineering capture-udp-tcpdump` |
| `check-udp-deps` | `reverse-skill udp-protocol-reverse-engineering check-udp-deps` |
| `make-frida-udp-hooks` | `reverse-skill udp-protocol-reverse-engineering make-frida-udp-hooks` |
| `pcap-to-udp-json` | `reverse-skill udp-protocol-reverse-engineering pcap-to-udp-json` |
| `replay-udp` | `reverse-skill udp-protocol-reverse-engineering replay-udp` |
| `tshark-udp-stats` | `reverse-skill udp-protocol-reverse-engineering tshark-udp-stats` |
| `udp-field-candidates` | `reverse-skill udp-protocol-reverse-engineering udp-field-candidates` |
| `udp-json-summary` | `reverse-skill udp-protocol-reverse-engineering udp-json-summary` |
| `udp-payload-cluster` | `reverse-skill udp-protocol-reverse-engineering udp-payload-cluster` |

## web-api-reverse-engineering

| Tool | Command |
|---|---|
| `analyze-graphql` | `reverse-skill web-api-reverse-engineering analyze-graphql` |
| `build-report` | `reverse-skill web-api-reverse-engineering build-report` |
| `capture-playwright-flow` | `reverse-skill web-api-reverse-engineering capture-playwright-flow` |
| `check-deps` | `reverse-skill web-api-reverse-engineering check-deps` |
| `dump-website-js` | `reverse-skill web-api-reverse-engineering dump-website-js` |
| `extract-endpoints` | `reverse-skill web-api-reverse-engineering extract-endpoints` |
| `extract-sourcemaps` | `reverse-skill web-api-reverse-engineering extract-sourcemaps` |
| `fingerprint-web` | `reverse-skill web-api-reverse-engineering fingerprint-web` |
| `generate-client-skeleton` | `reverse-skill web-api-reverse-engineering generate-client-skeleton` |
| `har-summary` | `reverse-skill web-api-reverse-engineering har-summary` |
| `scan-js-bundle` | `reverse-skill web-api-reverse-engineering scan-js-bundle` |
