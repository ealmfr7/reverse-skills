# Run Layout

Use this layout inside a `reverse-investigation-workflow` case:

```text
cases/<case-id>/
  runs/
    0001-physical-attestation-baseline/
      meta.json
      stdout.log
      stderr.log
      android-preflight.json
      android-env.json
      env-probe.json
      parsed-attestation.json
      verification.json
      attestation-summary.json
      raw/
      analysis/
    0002-vmos-attestation-compare/
      meta.json
      android-preflight.json
      android-env.json
      env-probe.json
      parsed-attestation.json
      verification.json
      flow-result.json
      attestation-summary.json
      attestation-comparison.json
  reports/
    attestation-report.md
```

Minimum metadata:

- target package and version.
- ADB serial or stable lab label.
- physical/emulator/VMOS/root/Frida state.
- installed APK hash when available.
- commands used.
- exact artifact paths consumed by each finding.

Do not store large APKs, decompiled trees, or full device images in the skill.
Keep them in case artifact storage and reference them by path and hash.
