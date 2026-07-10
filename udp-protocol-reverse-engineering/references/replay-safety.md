# Replay Safety

Replay only against systems the user owns or is explicitly authorized to test.
Do not replay packets to public services or third-party infrastructure.

## Preconditions

- isolated lab endpoint or local emulator
- explicit permission to send test packets
- rate limit agreed
- packet payload contains no third-party secrets
- replay command and timestamp logged

## Replay Limitations

UDP protocols often include:

- sequence numbers
- timestamps
- nonces
- session IDs
- checksums
- authentication tags

Raw replay may fail or produce misleading results if these fields are stale.

## Safer First Step

Before replay, build a parser and compare packet families. Then replay one small
non-destructive packet to a local test endpoint.
