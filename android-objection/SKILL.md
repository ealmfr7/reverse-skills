---
name: android-objection
description: Use Objection for authorized Android runtime exploration powered by Frida. Use when Codex needs interactive mobile app exploration, quick Frida-backed Android checks, package storage inspection, activity/service exploration, heap/class inspection, method watching, SSL pinning assessment in labs, or deciding when Objection is faster than writing custom Frida scripts.
---

# Android Objection

Use Objection for fast interactive exploration on apps in scope. For precise or
repeatable hooks, convert findings into `android-frida-hooking` scripts.

## Workflow

1. Confirm Frida works with the target device and package.
2. Start Objection:
   ```bash
   objection -g com.example.app explore
   ```
3. Use it for reconnaissance: package files, activities, loaded classes, heap
   objects, and quick method watches.
4. Save commands and observations. Convert stable findings into scripts.
5. Avoid relying on one-click bypasses without documenting what changed.

Read `references/workflow.md` for practical command categories.

## Source Anchors

- Objection repository: https://github.com/sensepost/objection
- Objection usage wiki: https://github.com/sensepost/objection/wiki/Using-objection
- OWASP MASTG Objection: https://mas.owasp.org/MASTG/tools/android/MASTG-TOOL-0029/
