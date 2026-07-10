# Run Layout

Each run should be self-contained and reproducible.

```text
runs/0001-name/
  meta.json
  events.jsonl
  stdout.log
  stderr.log
  blobs/
  analysis/
  run-index.json
```

## meta.json

Recommended fields:

```json
{
  "schema": 1,
  "name": "dynamic-bootstrap",
  "caseId": "2026-07-10-likee-live",
  "probe": "probes/frida/likee-bootstrap.js",
  "command": "frida -U -f video.like -l probes/frida/likee-bootstrap.js",
  "createdAt": "2026-07-10T00:00:00+00:00"
}
```

## Blob Policy

Use `blobs/` for binary streams. Reference blob slices from JSONL with `stream`, `offset`, and `length`. Keep large payloads out of Markdown reports; summarize and cite paths.
