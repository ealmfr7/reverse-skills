# Migration Guide

Use this to standardize existing one-off scripts without losing useful target-specific logic.

## Process

1. Inventory scripts with `find scripts .tmp/frida -name '*.js' -o -name '*.py'`.
2. Classify each file as Frida Java probe, Frida native probe, runner, offline analyzer, downloader, or fixture helper.
3. Keep target-specific hook bodies intact at first.
4. Replace ad hoc logging with the standard event schema.
5. Add redaction and capture limits.
6. Move outputs into a run folder with `meta.json`, `events.jsonl`, `blobs/`, and `analysis/`.
7. Add a small test for analyzers or event parsing.
8. Index the run and cite it from documentation findings.

Do not rewrite working hooks aggressively. Normalize the shell around them first: metadata, outputs, and validation.
