---
name: rev-ghidra
description: Analyze native binaries with Ghidra and automate Ghidra workflows. Use when Codex needs Ghidra project setup, ELF/Mach-O/PE/.so analysis, Android native library review, JNI mapping, symbol/string/xref analysis, decompiler guidance, Java or Jython Ghidra scripts, headless analyzeHeadless automation, or exports for Frida/IDA/Ghidra workflows.
---

# Ghidra Reverse Engineering

Use Ghidra for native binaries such as Android `.so` files, firmware, ELF, PE,
and Mach-O. For Java/Kotlin APK logic, prefer JADX first.

## Workflow

1. Identify binary type, architecture, base address assumptions, and goal.
2. Import into Ghidra, run auto-analysis, then inspect strings, exports, imports,
   JNI names, and cross-references.
3. Rename functions and labels as evidence accumulates.
4. For batch work, use `analyzeHeadless` and scripts.
5. Export offsets/function names for Frida hooks or reports.

Run dependency triage:

```bash
  reverse-skill rev-ghidra check-ghidra-deps
```

Read `references/workflow.md` for commands and script patterns.

## Tooling

Run Ghidra headless:

```bash
bash scripts/ghidra-run-headless.sh libtarget.so /tmp/ghidra-projects TargetProject scripts/ghidra/export_functions.py
```

Generate Frida offset hooks from a function export:

```bash
python3 scripts/make-frida-offset-hooks.py functions.json --out hook-offsets.js
```

Bundled Ghidra scripts:

- `scripts/ghidra/export_functions.py`: exports function names, entries,
  offsets, sizes, and thunk/source info.
- `scripts/ghidra/export_strings.py`: exports defined strings.
- `scripts/ghidra/export_imports.py`: exports external symbols and references.

Local helper:

- `scripts/make-frida-offset-hooks.py`: turns a Ghidra function JSON export into
  a Frida native hook template using `module.base.add(offset)`.

## Source Anchors

- Ghidra project: https://github.com/NationalSecurityAgency/ghidra
- HeadlessScript API: https://ghidra.re/ghidra_docs/api/ghidra/app/util/headless/HeadlessScript.html
- Ghidra headless analyzer documentation: https://www.ghidradocs.com/10.2_PUBLIC/docs/GhidraClass/Intermediate/HeadlessAnalyzer_withNotes.html
