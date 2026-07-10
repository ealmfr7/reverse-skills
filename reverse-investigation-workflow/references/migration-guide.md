# Migration Guide

Use this when an existing reverse engineering workspace contains loose APKs, dumps, scripts, captures, screenshots, and notes.

## Process

1. Inventory the workspace with `find` or `rg --files`; group files by target and investigation goal.
2. Create one case per coherent target or question, not one case per file.
3. Copy original inputs into `inputs/`; do not edit them in place.
4. Copy generated outputs into `artifacts/` by kind.
5. Use `add-artifact.py` for important files so hashes and notes are recorded.
6. Create `runs/` entries for experiments that should be reproducible.
7. Move loose notes into `notes/hypotheses.md`, `notes/findings.md`, or `notes/unknowns.md`.
8. Generate `reports/evidence-index.json` and check it before writing summaries.

## Non-Destructive Rule

During migration, copy or link first. Do not delete the old workspace until the case has an evidence index, important artifacts are accounted for, and the user explicitly agrees cleanup is safe.
