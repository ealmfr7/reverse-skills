# Ghidra Workflow

## Android Native Triage

1. Locate `lib/<abi>/*.so` in the APK.
2. Prefer `arm64-v8a` when present.
3. Search strings for URLs, keys, algorithm names, JNI class names, and error
   messages.
4. Inspect exports for `Java_...` JNI names.
5. If JNI is dynamic, correlate with Frida `RegisterNatives` logs.

## Headless Pattern

```bash
analyzeHeadless /tmp/ghidra-projects ProjectName \
  -import libtarget.so \
  -postScript script.py \
  -deleteProject
```

Use the wrapper:

```bash
bash rev-ghidra/scripts/ghidra-run-headless.sh \
  libtarget.so /tmp/ghidra-projects TargetProject \
  rev-ghidra/scripts/ghidra/export_functions.py
```

Ghidra post scripts can receive arguments after the script name. For function
export:

```bash
analyzeHeadless /tmp/ghidra-projects TargetProject \
  -import libtarget.so \
  -postScript export_functions.py /tmp/functions.json libtarget.so \
  -deleteProject
```

Then generate Frida hooks:

```bash
python3 rev-ghidra/scripts/make-frida-offset-hooks.py /tmp/functions.json --out hook-offsets.js
```

## Minimal Script Ideas

- list functions and entry points
- export strings and xrefs
- find calls to imports like `strcmp`, `AES_*`, `EVP_*`, `JNIEnv`
- rename functions based on string references
- export JSON for Frida offset hooks

## Offset Notes

For PIE Android `.so` files, runtime addresses change. Frida hooks should use:

```javascript
const mod = Process.getModuleByName("libtarget.so");
const fn = mod.base.add(0x1234);
```

Confirm whether the offset comes from Ghidra image base arithmetic, file offset,
or a rebased virtual address before using it.
