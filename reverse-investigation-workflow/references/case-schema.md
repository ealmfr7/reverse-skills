# Case Schema

Use `case.yaml` as the canonical metadata file for each investigation.

## Required Fields

- `id`: stable case id, preferably `YYYY-MM-DD-target-topic`.
- `target`: app, binary, service, protocol, or feature under investigation.
- `platform`: one of `android`, `ios`, `web`, `backend`, `native`, `mixed`.
- `country`: ISO-like country marker or `unknown` when not relevant.
- `status`: one of `planned`, `active`, `blocked`, `paused`, `complete`, `archived`.
- `authorization`: one of `owned`, `lab`, `ctf`, `contracted`, `defensive`, `unknown`.
- `goal`: concrete investigation objective.
- `created_at`: UTC timestamp.
- `skills_used`: list of reverse engineering skills used in the case.
- `artifact_policy`: handling rules for sensitive material.

## Recommended Extra Fields

- `scope`: concise list of allowed targets, accounts, devices, domains, and binaries.
- `out_of_scope`: systems or actions that must not be touched.
- `environment`: emulator/device, OS version, proxy, rooted/jailbroken state, tooling versions.
- `open_questions`: short list of unresolved technical questions.
- `final_report`: path under `reports/` once complete.

Keep `authorization: unknown` only during triage. Before active testing or dynamic analysis, clarify authorization in notes or update the field.
