# Frontmatter Schema

Every durable document should start with YAML frontmatter.

## Required

```yaml
id: F-0001
type: finding
status: active
title: short precise title
created_at: 2026-07-10
```

## Recommended

```yaml
target: likee
case_id: 2026-07-10-likee-live
phase: dynamic
supersedes: []
superseded_by: null
evidence:
  - cases/2026-07-10-likee-live/reports/evidence-index.json
```

## Rules

- Use `case_id` to connect durable docs to the investigation case.
- Use `evidence` to cite stable paths, not pasted secrets.
- Use `supersedes` when a new document replaces old documents.
- Use `superseded_by` on old documents when they are replaced.
- Keep titles short enough to scan in tables.
