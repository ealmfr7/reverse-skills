# Migration Guide

Use this for workspaces with many loose Markdown files such as `docs/agent-findings`, `reports/`, and `.tmp` notes.

## Process

1. Inventory Markdown files with `find docs reports .tmp -name '*.md'`.
2. Classify each file as finding, hypothesis, experiment, decision, runbook, report, or archive.
3. Create new numbered docs for current knowledge. Do not preserve old filenames as canonical IDs.
4. Mark duplicated or stale documents as `superseded`, pointing to the new ID.
5. Keep raw evidence in case folders and cite paths from docs.
6. Generate `docs/docs-index.json` and `docs/INDEX.md`.
7. Run `lint-docs.py docs` before treating the documentation set as clean.

## Practical Migration Pattern

For a folder like `docs/agent-findings`:

- Start with the latest documents by phase or topic.
- Promote only still-valid claims into `docs/findings/`.
- Move unproven next-step notes into `docs/hypotheses/` or `docs/experiments/`.
- Keep obsolete documents in place until the new index covers them, then archive only with explicit approval.
