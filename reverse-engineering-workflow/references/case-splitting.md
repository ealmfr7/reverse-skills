# Case Splitting

Use one case per coherent target and goal.

## Separate Cases

- Likee APK live protocol and Bigo APK live protocol should usually be separate cases.
- Different apps with different evidence stores should be separate cases.
- Different goals in the same app may be separate cases when artifacts, runs, and reports diverge heavily.

## Same Case

- Multiple versions of the same APK can stay in one case when the goal is version comparison.
- Android app plus web/API captures can stay in one case when the API belongs to the app flow under investigation.

## Comparison Case

Create a comparison case when the goal is explicitly cross-target:

```yaml
id: 2026-07-10-likee-bigo-live-comparison
target: likee+bigo
related_cases:
  - 2026-07-10-likee-live-protocol
  - 2026-07-10-bigo-live-protocol
```
