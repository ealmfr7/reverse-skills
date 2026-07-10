# Document Taxonomy

Use a document type based on the claim's lifecycle.

## Types

- `finding`: proven technical claim supported by evidence.
- `hypothesis`: plausible but unproven explanation or route.
- `experiment`: a documented attempt, test plan, or run summary.
- `decision`: technical or workflow choice that affects future work.
- `runbook`: repeatable procedure.
- `report`: synthesized output for a reader.

## IDs

- `F-0001`: finding.
- `H-0001`: hypothesis.
- `R-0001`: experiment.
- `D-0001`: decision.
- `RB-0001`: runbook.
- `REP-0001`: report.

Do not encode all meaning into the filename. The filename should be readable, but frontmatter is canonical.

## Statuses

- `draft`: not reviewed or incomplete.
- `active`: currently valid.
- `superseded`: replaced by a newer document.
- `rejected`: tested and found false.
- `final`: approved final output.
