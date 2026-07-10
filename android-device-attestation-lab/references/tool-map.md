# Tool Map

This map separates reusable device/attestation tooling from target-specific
case scripts.

## Stable Tools In This Skill

| Tool | Role | Notes |
|---|---|---|
| `android-target-preflight.py` | Checks ADB device selection, package install state, foreground activity, process id, Frida server state, and residual Gum/Frida threads. | Target-neutral; package and foreground regex are caller-provided. |
| `android-env-capture.py` | Captures public Android props, settings, package inventory, network, sensor, and selected package state. | Target-neutral; `--package` may be repeated. |
| `attestation-artifact-summary.py` | Summarizes run artifacts and recommends missing next evidence. | Offline only. |
| `compare-attestation-runs.py` | Compares two run folders for chain, security level, boot state, root match, backend policy, and signature differences. | Offline only; fixture-tested. |
| `parse-android-key-attestation.py` | Parses normalized Android Key Attestation fields, chain metadata, root-of-trust fields, and certificate fingerprints from report JSON. | Offline only; fixture-tested. |
| `verify-attestation-report.py` | Verifies explicit policy checks for challenge, chain, security level, boot state, exact root, and SPKI root evidence. | Keeps key possession and backend trust separate. |
| `attestation-backend-lab.py` | Models nonce, registration, challenge, synthetic signing, and signature verification against backend trust state. | Local synthetic state only. |
| `attestation-root-diff.py` | Compares local root bytes and optional SPKI digests against trusted roots. | Keeps exact root and SPKI match separate. |
| `attestation-report.py` | Renders Markdown from summary, verification, and comparison JSON artifacts. | Report generator only; no new claims. |
| `attestation-root-source-probe.py` | Searches bounded local dumps/images for attestation root source markers. | Metadata-only output; does not copy matched file contents. |
| `frida-keystore-trace.js` | Observational Java KeyStore availability/instance trace template. | Bounded JSON events; no method overwrites. |
| `frida-keymaster-trace.js` | Observational native keymaster/keymint export trace template. | Bounded JSON events; attach-only native observation. |

## Candidate Tools To Add Later

| Candidate | Role | Acceptance rule |
|---|---|---|
| `attestation-runtime-trace-summary.py` | Summarize strace/logcat/Frida runtime evidence. | Must consume offline input files and redact sensitive values. |
| `attestation-native-static-probe.py` | Scan native files for keymaster/attestation strings and symbols. | Must be static-only and path-bounded. |

## Promotion Order

1. `android-target-preflight.py`: generic ADB/device readiness.
2. `android-env-capture.py`: generic environment capture.
3. `attestation-artifact-summary.py`: offline run summary.
4. `compare-attestation-runs.py`: fixture-tested run comparison.
5. `parse-android-key-attestation.py`: normalized parser.
6. `verify-attestation-report.py`: explicit offline policy verification.
7. `attestation-backend-lab.py`: backend nonce/register/signature lab model.
8. `attestation-root-diff.py`: exact root and SPKI comparison.
9. `attestation-report.py`: Markdown reporting.
10. `attestation-root-source-probe.py`: bounded root source scans.
11. Frida KeyStore/keymaster traces using bounded JSON events.
