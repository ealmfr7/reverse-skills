---
name: reverse-probe-tooling-workflow
description: Standardize reverse engineering probes, Frida scripts, Python analyzers, run directories, JSONL event schemas, blob indexes, redaction rules, and probe linting. Use when Codex needs to create or refactor target-specific Frida hooks, build reusable analyzer scripts, normalize events from dynamic instrumentation, create run folders for probe output, validate probe JSONL, or turn messy one-off reversing scripts into professional tooling without removing target-specific logic.
---

# Reverse Probe Tooling Workflow

Use this skill for the tooling layer between investigation cases and technical hooks. Do not force every reverse engineering script to become generic. Keep target-specific hooks specific, but standardize scaffolding, output schemas, redaction, run folders, analyzers, and validation.

## Quick Start

Create a Frida Java probe scaffold:

```bash
python3 reverse-probe-tooling-workflow/scripts/new-probe.py frida java likee-bootstrap \
  --out probes \
  --source frida.likee.bootstrap
```

Create a Frida native probe scaffold:

```bash
python3 reverse-probe-tooling-workflow/scripts/new-probe.py frida native mediasdk-offsets \
  --out probes \
  --source frida.likee.mediasdk
```

Create a Python analyzer scaffold:

```bash
python3 reverse-probe-tooling-workflow/scripts/new-analyzer.py udp-summary --out probes/python
```

Create a run folder:

```bash
python3 reverse-probe-tooling-workflow/scripts/init-run.py runs dynamic-bootstrap \
  --case-id 2026-07-10-likee-live \
  --probe probes/frida/likee-bootstrap.js \
  --command "frida -U -f video.like -l probes/frida/likee-bootstrap.js"
```

Validate and index run output:

```bash
python3 reverse-probe-tooling-workflow/scripts/lint-events.py runs/0001-dynamic-bootstrap/events.jsonl
python3 reverse-probe-tooling-workflow/scripts/index-run.py runs/0001-dynamic-bootstrap
```

## Standard Layout

Use this layout inside a repo, case, or workspace:

```text
probes/
  frida/
  python/
  schemas/
runs/
  0001-name/
    meta.json
    events.jsonl
    stdout.log
    stderr.log
    blobs/
    analysis/
    run-index.json
```

Inside a `reverse-investigation-workflow` case, place case-specific probes under `cases/<case-id>/scripts/` or `cases/<case-id>/artifacts/frida/`, and place run outputs under `cases/<case-id>/runs/`.

## Event Contract

Every probe event should be a JSON object with:

```json
{
  "schema": 1,
  "type": "event",
  "event": "probe.start",
  "ts": 1.0,
  "source": "frida.target.profile",
  "data": {}
}
```

Allowed `type` values are `event`, `status`, `blob`, and `error`. Use `blob` only when binary data is stored separately or sent through Frida's binary message channel.

## Probe Rules

- Keep hooks target-specific when classes, offsets, signatures, or packet formats are target-specific.
- Standardize `emit`, timestamps, `source`, redaction, limits, and output folders.
- Redact URLs, filesystem paths, tokens, cookies, signatures, secrets, authorization headers, and session-like values by default.
- Bound captures with max event counts, max bytes, or focus ranges.
- Prefer analyzers that operate offline over local run folders.
- Every analyzer should support `<run> --out <dir> --json` where practical.
- Add a small fixture test for reusable analyzers.

## Reference Routing

- Read `references/event-schema.md` before changing event formats or linting.
- Read `references/run-layout.md` when creating run folders or indexes.
- Read `references/probe-patterns.md` when refactoring Frida scripts.
- Read `references/analyzer-patterns.md` when creating Python analyzers.
- Read `references/migration-guide.md` when standardizing existing scripts from `scripts/` or `.tmp/frida/`.
