# Event Schema

All probes should emit JSONL-compatible objects.

## Required Fields

```json
{
  "schema": 1,
  "type": "event",
  "event": "name",
  "ts": 1.0,
  "source": "frida.target.profile",
  "data": {}
}
```

## Optional Fields

- `monoMs`: milliseconds since probe start.
- `pid`: process id.
- `tid`: thread id.
- `seq`: monotonically increasing event sequence.
- `stream`: blob stream name.
- `offset`: blob offset when data is written to a sidecar file.
- `length`: blob length.

## Event Types

- `status`: lifecycle, hook installed/skipped, warnings.
- `event`: observed runtime behavior.
- `blob`: binary payload metadata or Frida binary message.
- `error`: script or analyzer errors.

Do not put raw secrets in `data`. Redact before emission.
