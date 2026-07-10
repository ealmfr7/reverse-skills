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

## Candidate Tools To Add Later

| Candidate | Role | Acceptance rule |
|---|---|---|
| `attestation-backend-lab.py` | Local nonce/register/signature backend model. | Must use synthetic local state only. |
| `attestation-root-diff.py` | Compare local attestation root against trusted root material. | Must preserve source timestamps and match type. |
| `attestation-root-source-probe.py` | Search device/local images for root certificate material. | Must bound pulls/scans and default to metadata/hashes. |
| `attestation-runtime-trace-summary.py` | Summarize strace/logcat/Frida runtime evidence. | Must consume offline input files and redact sensitive values. |
| `attestation-native-static-probe.py` | Scan native files for keymaster/attestation strings and symbols. | Must be static-only and path-bounded. |
| `frida-keystore-trace.js` / `frida-keymaster-trace.js` | Observational runtime probes for KeyStore/keymaster/X.509 flows. | Must emit bounded JSONL events and avoid policy modification. |

## Promotion Order

1. `android-target-preflight.py`: generic ADB/device readiness.
2. `android-env-capture.py`: generic environment capture.
3. `attestation-artifact-summary.py`: offline run summary.
4. `compare-attestation-runs.py`: fixture-tested run comparison.
5. `parse-android-key-attestation.py`: normalized parser.
6. `verify-attestation-report.py`: explicit offline policy verification.
7. backend nonce/register/signature lab model.
8. root diff/source probes.
9. KeyStore/keymaster Frida probes using the probe tooling event schema.
