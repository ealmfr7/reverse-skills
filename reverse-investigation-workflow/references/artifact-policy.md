# Artifact Policy

Treat artifacts as evidence. Preserve enough context to reproduce findings without spreading secrets.

## Handling Rules

- Keep original inputs unchanged under `inputs/`.
- Store generated or derived material under `artifacts/`.
- Record the phase and note for meaningful artifacts with `add-artifact.py`.
- Redact secrets before committing: passwords, raw session tokens, cookies, private keys, access tokens, and personal account data.
- Prefer synthetic lab accounts. If real accounts are unavoidable, store only account labels and setup notes.
- Do not commit raw malware payloads, live credentials, private customer data, or captured third-party private data unless the repository is explicitly authorized to hold them.
- For PCAP/HAR/log files, review for tokens, cookies, phone numbers, emails, device identifiers, and precise locations before commit.
- Keep `artifact_policy.raw_tokens_allowed: false` unless an explicitly authorized private evidence store requires otherwise.

## Evidence Quality

Each finding should cite at least one stable artifact path. Good evidence includes a hash, tool/version, command/run folder, timestamp, and short explanation of why the artifact proves the claim.
