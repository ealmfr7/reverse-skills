# Binary Protocol Patterns

## Common Fields

| Field | Clues |
|---|---|
| magic | constant prefix across packet family |
| version | small integer near start |
| type/opcode | one byte/word that changes with action |
| length | equals payload length or body length |
| sequence | increments per packet or per direction |
| timestamp | monotonic 32/64-bit integer |
| flags | bitmasks tested with `&`, `tbz`, `tbnz` |
| checksum/MAC | trailing bytes change with payload |
| nonce | unique random-looking bytes per packet |

## Endianness

Try interpreting stable 2/4/8 byte fields as both little-endian and big-endian.
Network protocols often use big-endian, but custom app protocols may use host
endianness.

## Automated First Pass

After `udp-json-summary.py`, run:

```bash
python3 udp-protocol-reverse-engineering/scripts/udp-field-candidates.py udp-summary.json --json-out udp-fields.json
```

Review:

- `constant_bytes`: likely magic/version/reserved fields
- `byte_entropy`: low entropy positions often encode type/flags
- `monotonic_counters`: sequence/timestamp candidates

Treat this as a hypothesis generator, not proof. Re-run it on a single payload
cluster or direction for better signal.

## Encryption and Compression Clues

- compressed: recognizable headers, entropy high after a small stable prefix,
  decompression API in code
- encrypted: random-looking payload, IV/nonce fields, crypto API calls near
  send path, MAC/tag length at tail
- protobuf/flatbuffers/msgpack: structured binary with repeated field-like
  patterns and libraries in app
