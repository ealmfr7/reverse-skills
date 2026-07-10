---
name: android-frida-hooking
description: Create, adapt, and troubleshoot Frida scripts for Android dynamic analysis. Use when Codex needs to hook Android APKs at runtime, inspect Java/Kotlin methods, handle overloads, constructors, ClassLoaders, OkHttp/WebView/network behavior, crypto/storage APIs, native .so exports, JNI, RegisterNatives, dlopen timing, or Frida spawn/attach setup on rooted devices and emulators.
---

# Android Frida Hooking

Use this skill to guide Android runtime instrumentation with Frida.

## Quick Workflow

1. Confirm target context: app package, device/emulator, Android version, ABI,
   and target behavior.
2. If setup is unknown, run:
   ```bash
   reverse-skill android-frida-hooking check-frida-android
   ```
   Then read `references/setup.md`.
3. Use static analysis first when possible: JADX/class names/logcat/errors give
   better targets than blind hooks.
4. Choose the narrowest hook layer:
   - Java/Kotlin app logic: read `references/java-kotlin-hooks.md`.
   - ClassLoader/packed apps: read `references/classloaders-packers.md`.
   - OkHttp/WebView/network observation: read `references/network-hooks.md`.
   - Crypto/storage observation: read `references/crypto-storage-hooks.md`.
   - Native/JNI/.so hooks: read `references/native-jni-hooks.md`.
   - Failures/crashes: read `references/troubleshooting.md`.
5. Start with logging-only hooks. Modify arguments or return values only after
   baseline behavior is understood and the user has a legitimate test reason.
6. Prefer stable, specific hooks over broad hooks. Avoid constructor/init hooks
   unless evidence shows the target behavior only exists during initialization.

## Command Patterns

Modern Frida CLI does not need `--no-pause`.

```bash
# Spawn the app and load the script from process start
frida -U -f com.example.app -l hook.js

# Attach to a running app
frida -U com.example.app -l hook.js

# Attach by PID
frida -U -p 1234 -l hook.js
```

## Template Selection

Generate common hooks:

```bash
reverse-skill android-frida-hooking make-java-hook com.example.AuthManager login --overload java.lang.String,java.lang.String --stacktrace --out login-hook.js
reverse-skill android-frida-hooking make-native-hook libsign.so --export sign_payload --wait-load --out sign-hook.js
reverse-skill android-frida-hooking make-native-hook libsign.so --offset 0x1234 --wait-load --out offset-hook.js
```

Copy or adapt templates from `scripts/templates/`:

- `java-method-hook.js`: one known Java/Kotlin method.
- `java-overloads-hook.js`: log all overloads for a method.
- `constructor-hook.js`: Java constructor hooks.
- `classloader-hook.js`: find/use non-default ClassLoaders.
- `stacktrace-hook.js`: print a Java stack trace at the current hook point.
- `system-loadlibrary-hook.js`: observe `System.loadLibrary` and `System.load`.
- `dexclassloader-hook.js`: observe dynamic DEX class loader creation.
- `okhttp-hook.js`: observe OkHttp requests and responses.
- `webview-hook.js`: observe WebView URL and JavaScript bridge behavior.
- `sharedprefs-hook.js`: observe SharedPreferences reads/writes.
- `crypto-hook.js`: observe common Java crypto inputs/outputs.
- `base64-hook.js`: observe Android Base64 encode/decode calls.
- `file-io-hook.js`: observe basic Java file input/output constructors.
- `native-export-hook.js`: hook a native export in a loaded `.so`.
- `dlopen-hook.js`: wait for native library load before hooking.
- `register-natives-hook.js`: log JNI native method registration.

## Expected Outputs

Prefer concrete artifacts:

- A Frida script with package name, target class/module, and hook intent.
- Run command for spawn or attach.
- Baseline observations: arguments, return values, stack traces, request URLs,
  buffers, module names, or JNI registration logs.
- Clear notes distinguishing observed behavior from inferred behavior.
- Failure notes with next debugging step when a hook cannot be installed.

## Source Anchors

This skill is informed by:

- Frida Android documentation: https://frida.re/docs/android/
- Frida JavaScript API: https://frida.re/docs/javascript-api/
- OWASP MASTG Frida for Android: https://mas.owasp.org/MASTG/tools/android/MASTG-TOOL-0001/
- Local third-party reference: `../rev-frida/SKILL.md`
