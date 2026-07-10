# Analyzer Patterns

Python analyzers should be deterministic and offline-first.

## CLI Shape

Prefer:

```bash
python3 analyzer.py <run-dir> --out <run-dir>/analysis/<name> --json
```

## Code Shape

- Put core logic in importable functions.
- Keep CLI parsing in `main`.
- Read JSONL with a small helper.
- Write machine output as JSON/JSONL.
- Write human output as Markdown only after machine output exists.
- Avoid network/device calls in analyzers unless the script is explicitly a runner.

## Tests

Add fixture tests for:

- missing index files.
- malformed JSONL.
- representative events or blob slices.
- redaction of sensitive strings.
