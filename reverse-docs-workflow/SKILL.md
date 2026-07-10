---
name: reverse-docs-workflow
description: Organize reverse engineering documentation, findings, decisions, hypotheses, experiments, runbooks, and reports with stable IDs, frontmatter, statuses, evidence links, supersession tracking, indexes, and linting. Use when Codex needs to clean up messy docs folders, create numbered findings or decisions, mark outdated notes as superseded, produce docs indexes, enforce documentation schemas, or migrate ad hoc reversing notes from docs/, reports/, .tmp/, or agent-findings into a professional knowledge base.
---

# Reverse Documentation Workflow

Use this skill when the problem is documentation order, not raw artifact storage. Pair it with `reverse-investigation-workflow`: cases hold evidence and runs; this workflow holds durable knowledge derived from that evidence.

## Quick Start

Initialize documentation:

```bash
python3 reverse-docs-workflow/scripts/init-docs.py \
  --root . \
  --project "live protocol reconstruction"
```

Create a numbered finding:

```bash
python3 reverse-docs-workflow/scripts/new-finding.py docs \
  "udp bootstrap uses dominant session" \
  --target likee \
  --case-id 2026-07-10-likee-live \
  --evidence cases/2026-07-10-likee-live/runs/0001/observations.md
```

Create a numbered decision:

```bash
python3 reverse-docs-workflow/scripts/new-decision.py docs \
  "prefer case folders over tmp" \
  --rationale "Reports need stable evidence paths."
```

Mark stale docs superseded instead of deleting them:

```bash
python3 reverse-docs-workflow/scripts/mark-superseded.py \
  docs/findings/F-0001-old-route.md \
  --by F-0007 \
  --reason "Replaced by packet-level evidence."
```

Index and validate:

```bash
python3 reverse-docs-workflow/scripts/index-docs.py docs --json-out docs/docs-index.json
python3 reverse-docs-workflow/scripts/lint-docs.py docs
```

## Canonical Layout

Use this layout for durable documentation:

```text
docs/
  INDEX.md
  glossary.md
  timeline.md
  findings/
  hypotheses/
  experiments/
  decisions/
  runbooks/
  reports/final/
  reports/interim/
  archive/superseded/
```

Keep ad hoc notes out of `reports/` until reviewed. Use `findings/` for claims proven by evidence, `hypotheses/` for unproven theories, `experiments/` for what was tried, `decisions/` for workflow or tooling choices, and `runbooks/` for repeatable procedures.

## Document Rules

- Every durable doc needs frontmatter with `id`, `type`, `status`, `title`, and `created_at`.
- Prefer stable IDs over phase names alone: `F-0001`, `D-0001`, `R-0001`.
- Never delete stale findings by default. Mark them `superseded` and point to the replacement.
- A finding should cite evidence paths from a case, artifact index, run folder, log, PCAP, HAR, screenshot, or code reference.
- Keep secrets out of docs. Refer to redacted artifact paths, not raw credentials or tokens.

## Reference Routing

- Read `references/doc-taxonomy.md` when classifying existing docs.
- Read `references/frontmatter-schema.md` before editing schemas or lint rules.
- Read `references/templates.md` when drafting findings, decisions, experiments, runbooks, or reports.
- Read `references/migration-guide.md` when reorganizing existing `docs/`, `reports/`, `.tmp/`, or `agent-findings` material.
