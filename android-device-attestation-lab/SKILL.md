---
name: android-device-attestation-lab
description: Use when Android reversing needs device environment baselines, real-vs-emulator or VMOS comparison, Play Integrity or KeyStore attestation lab runs, attestation certificate/root analysis, backend trust experiments, ADB preflight checks, or KeyStore/keymaster runtime probes.
---

# Android Device Attestation Lab

Use this skill when anti-analysis triage points to device trust, Play Integrity,
SafetyNet, Android Key Attestation, KeyStore/keymaster, VMOS/emulator
differences, or backend registration/signature flows.

Keep target-specific findings outside the skill. Package names, app screenshots,
case conclusions, and Snapchat/Likee-specific notes belong in a
`reverse-investigation-workflow` case. This skill only keeps reusable tools,
run layouts, and decision rules.

## Quick Start

Check that a device/app is ready for a dynamic run:

```bash
python3 android-device-attestation-lab/scripts/android-target-preflight.py \
  --package com.example.app \
  --fail-if-not-ready
```

Capture target-neutral Android environment signals:

```bash
python3 android-device-attestation-lab/scripts/android-env-capture.py \
  --package com.example.app \
  --raw-out cases/<case-id>/runs/0001-physical-attestation-baseline/raw \
  --json-out cases/<case-id>/runs/0001-physical-attestation-baseline/android-env.json
```

Summarize a run folder with attestation artifacts:

```bash
python3 android-device-attestation-lab/scripts/attestation-artifact-summary.py \
  cases/<case-id>/runs/0001-device-attestation \
  --json-out cases/<case-id>/runs/0001-device-attestation/attestation-summary.json
```

Compare two attestation runs:

```bash
python3 android-device-attestation-lab/scripts/compare-attestation-runs.py \
  cases/<case-id>/runs/0001-physical-attestation-baseline \
  cases/<case-id>/runs/0002-comparison-attestation \
  --left-label physical \
  --right-label comparison \
  --json-out cases/<case-id>/runs/0002-comparison-attestation/attestation-comparison.json
```

Parse and verify an offline attestation report:

```bash
python3 android-device-attestation-lab/scripts/parse-android-key-attestation.py \
  cases/<case-id>/runs/0001-physical-attestation-baseline/env-probe.json \
  --json-out cases/<case-id>/runs/0001-physical-attestation-baseline/parsed-attestation.json

python3 android-device-attestation-lab/scripts/verify-attestation-report.py \
  cases/<case-id>/runs/0001-physical-attestation-baseline/env-probe.json \
  --root-diff cases/<case-id>/runs/0001-physical-attestation-baseline/root-diff.json \
  --expected-attestation-security-level TrustedEnvironment \
  --expected-keymaster-security-level TrustedEnvironment \
  --require-device-locked \
  --json-out cases/<case-id>/runs/0001-physical-attestation-baseline/verification.json
```

Model backend registration/signature trust locally:

```bash
python3 android-device-attestation-lab/scripts/attestation-backend-lab.py issue-nonce \
  --state cases/<case-id>/backend-state.json \
  --device-id physical-1
```

Render a Markdown report:

```bash
python3 android-device-attestation-lab/scripts/attestation-report.py \
  --summary cases/<case-id>/runs/0002-comparison-attestation/attestation-summary.json \
  --verification cases/<case-id>/runs/0002-comparison-attestation/verification.json \
  --comparison cases/<case-id>/runs/0002-comparison-attestation/attestation-comparison.json \
  --out cases/<case-id>/reports/attestation-report.md
```

Search local dumps/images for root-source evidence:

```bash
python3 android-device-attestation-lab/scripts/attestation-root-source-probe.py \
  --root-diff cases/<case-id>/runs/0002-comparison-attestation/root-diff.json \
  --local-scan-dir cases/<case-id>/artifacts/device-image \
  --json-out cases/<case-id>/runs/0002-comparison-attestation/root-source.json
```

## Workflow

1. Create/select a case with `reverse-investigation-workflow`.
2. Capture a known-good physical-device baseline before VMOS/root/Frida runs.
3. Run target preflight: ADB device, package installed, foreground activity,
   process id, Frida server state, and residual Gum/Frida threads.
4. Collect public environment signals and app attestation output.
5. Verify attestation chain, root certificate, challenge, app binding, security
   levels, boot state, and revocation status.
6. Compare physical vs VMOS/emulator/rooted/Frida-attached runs.
7. Separate **key possession** from **backend trust**: a key can sign while
   backend policy still rejects the attestation environment.
8. Promote durable conclusions to numbered findings with exact artifact paths.

## Stable Tooling Boundary

Stable tools should be target-agnostic. Before promoting a script into this
skill, remove hardcoded package names, app-specific activities, private run
paths, case conclusions, and raw sensitive values.

Do promote:

- ADB/device readiness checks.
- environment capture and artifact indexing.
- attestation parsing and chain/root verification.
- backend nonce/register/signature lab flows.
- root certificate source analysis.
- bounded Frida/strace probes for KeyStore/keymaster observation.

Do not promote:

- Snapchat-only findings or screenshots.
- Likee-only media/protocol logic.
- package-specific bypasses.
- conclusions that depend on one APK build.

## Reference Routing

- Read `references/tool-map.md` when deciding which existing lab scripts are
  stable enough to include in this skill or need sanitization first.
- Read `references/run-layout.md` when creating attestation runs inside a case.
- Read `references/attestation-flow.md` when interpreting backend registration,
  nonce, signature, and root-certificate results.
