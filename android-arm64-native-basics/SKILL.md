---
name: android-arm64-native-basics
description: Explain and apply Android ARM64 native reversing basics. Use when Codex needs AArch64 calling conventions, registers, stack frames, JNI argument mapping, .so offsets, module base plus offset math, IDA/Ghidra pseudocode interpretation, Frida native hook argument decoding, pointer/memory basics, or bridging Java native declarations to native functions.
---

# Android ARM64 Native Basics

Use this skill as the conceptual bridge between JADX/Java, native `.so`
analysis, Ghidra/IDA, Frida native hooks, and Unicorn emulation.

## Quick Rules

- First eight integer/pointer args: `x0`-`x7`.
- Return value: `x0`.
- Link register: `x30` / `lr`.
- Stack pointer: `sp`.
- 32-bit view of `xN`: `wN`.
- Android native libraries are usually PIE; runtime address = module base +
  file/rebased offset.
- JNI native methods receive `JNIEnv *` and `jobject`/`jclass` before app args.

Read `references/workflow.md` for examples.

## Tooling

Calculate offsets and runtime addresses:

```bash
reverse-skill android-arm64-native-basics offset-math --image-base 0x100000 --entry 0x101234 --module-base 0x7a00000000
```

Read focused references as needed:

- `references/arm64-calling-convention.md`
- `references/jni-argument-mapping.md`
- `references/offset-math.md`
- `references/frida-native-argument-decoding.md`

## Source Anchors

- Arm A64 instruction set docs: https://developer.arm.com/documentation
- Android NDK concepts: https://developer.android.com/ndk
- Frida JavaScript API: https://frida.re/docs/javascript-api/
