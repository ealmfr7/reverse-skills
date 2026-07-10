# Artifact Policy

Treat artifacts as evidence. Preserve enough context to reproduce findings and
apply the repository-level use policy in `README.md`.

## Handling Rules

- Keep original inputs unchanged under `inputs/`.
- Store generated or derived material under `artifacts/`.
- Record the phase and note for meaningful artifacts with `add-artifact.py`.

## Evidence Quality

Each finding should cite at least one stable artifact path. Good evidence includes a hash, tool/version, command/run folder, timestamp, and short explanation of why the artifact proves the claim.
