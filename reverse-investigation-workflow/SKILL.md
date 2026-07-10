---
name: reverse-investigation-workflow
description: Create and maintain structured reverse engineering investigation cases. Use when Codex needs to organize messy reversing work into professional case folders, define scope and authorization, create case.yaml metadata, separate inputs/artifacts/runs/notes/reports/scripts, add and index evidence, track hypotheses/findings/unknowns, or migrate ad hoc APK, Frida, JADX, Ghidra, PCAP, HAR, screenshot, log, and script artifacts into a stable workflow.
---

# Reverse Investigation Workflow

Use this skill to impose a repeatable case structure before or during reverse engineering work. Keep the workflow evidence-oriented: define what is in scope, preserve original inputs, keep generated artifacts separate, record runs, and publish findings from indexed evidence.

## Quick Start

Create a case:

```bash
python3 reverse-investigation-workflow/scripts/init-case.py 2026-07-10-target-feature \
  --root . \
  --target target-name \
  --platform android \
  --country US \
  --authorization lab \
  --goal "Trace login and live-room bootstrap"
```

Add artifacts instead of dropping files directly into random folders:

```bash
python3 reverse-investigation-workflow/scripts/add-artifact.py \
  cases/2026-07-10-target-feature ./hook.js \
  --kind frida-script \
  --phase dynamic \
  --note "Hook for login token construction"
```

Create a numbered run folder for each meaningful experiment:

```bash
python3 reverse-investigation-workflow/scripts/new-run.py \
  cases/2026-07-10-target-feature dynamic-login-hook \
  --phase dynamic \
  --command "frida -U -f com.example.app -l artifacts/frida/hook.js"
```

Create standard Android attestation run folders:

```bash
python3 reverse-investigation-workflow/scripts/init-attestation-runs.py \
  cases/2026-07-10-target-feature
```

Build an evidence index before summarizing:

```bash
python3 reverse-investigation-workflow/scripts/index-artifacts.py \
  cases/2026-07-10-target-feature \
  --json-out cases/2026-07-10-target-feature/reports/evidence-index.json
```

## Workflow

1. **Intake**: create the case, write the goal, authorization, platform, country, and target in `case.yaml`.
2. **Scope**: keep original inputs under `inputs/`; do not mix them with decompiled or modified outputs.
3. **Analysis**: use `runs/` for repeatable experiments and `artifacts/` for generated evidence.
4. **Notes**: split thinking into `notes/hypotheses.md`, `notes/findings.md`, and `notes/unknowns.md`.
5. **Evidence**: use `add-artifact.py` for important files so hashes, phases, and notes are recorded.
6. **Reporting**: generate `reports/evidence-index.json` and write conclusions that cite artifact paths.

## Case Layout

Every case should live under `cases/<case-id>/` and contain:

```text
case.yaml
README.md
timeline.md
inputs/
artifacts/
runs/
notes/
reports/
scripts/
```

Read `references/folder-layout.md` when deciding where a new file belongs.

## Reference Routing

- Read `references/case-schema.md` when creating or editing `case.yaml`.
- Read `references/folder-layout.md` when reorganizing a workspace or deciding file placement.
- Read `references/artifact-policy.md` before handling tokens, accounts, captures, customer data, malware, or third-party app data.
- Read `references/migration-guide.md` when converting an existing messy workspace into `cases/`.
