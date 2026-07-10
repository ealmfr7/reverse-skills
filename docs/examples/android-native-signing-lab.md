# Android Native Signing Lab Workflow

Use this workflow when a lab APK computes a request signature or token in a
native `.so`.

## Goal

Map Java native declarations to native functions, observe runtime arguments, and
produce stable Frida hooks.

## Flow

1. Static APK triage:
   ```text
   Use android-reverse-engineering to find native declarations and System.loadLibrary calls.
   ```
2. ARM64/JNI mapping:
   ```bash
   python3 android-arm64-native-basics/scripts/offset-math.py --image-base 0x100000 --entry 0x101234 --module-base 0x7a00000000
   ```
3. Native analysis:
   ```bash
   bash rev-ghidra/scripts/ghidra-run-headless.sh libsign.so /tmp/ghidra SignProject
   ```
4. Export functions from Ghidra and generate hook stubs:
   ```bash
   python3 rev-ghidra/scripts/make-frida-offset-hooks.py functions.json --out sign-offset-hooks.js
   ```
5. Runtime correlation:
   ```bash
   python3 android-frida-hooking/scripts/make-native-hook.py libsign.so --offset 0x1234 --wait-load --out sign-hook.js
   frida -U com.example.lab -l sign-hook.js
   ```

## Validation

- Java native method and native address are correlated.
- Hook logs arguments/return for the target app action.
- Offset is module-relative, not a stale runtime address.
