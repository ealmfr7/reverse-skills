# Android Frida Hooking Workflow

## Triage

Collect these facts before writing hooks:

- Package name: `adb shell pm list packages | grep <name>`
- Launch activity: `adb shell cmd package resolve-activity --brief <package>`
- Android version and ABI: `adb shell getprop ro.build.version.release`,
  `adb shell getprop ro.product.cpu.abi`
- Frida versions: `frida --version` and `frida-server --version`
- Static hints from JADX: class names, method signatures, Retrofit/OkHttp usage,
  `System.loadLibrary`, native library names, and string anchors.

## Hook Selection

Choose a hook layer by evidence:

| Evidence | Prefer |
|---|---|
| Clear Java/Kotlin class and method | Java method hook |
| Method has many overloads | overload enumerator |
| `Java.use()` cannot find class | ClassLoader workflow |
| OkHttp in dependencies or stack traces | OkHttp hook |
| WebView app or JS bridge names | WebView hook |
| Crypto/storage behavior | Cipher/Base64/SharedPreferences hooks |
| `System.loadLibrary` or `.so` files | dlopen/native export hooks |
| JNI names not exported | RegisterNatives logging |

## Baseline Before Modification

1. Run a logging-only script.
2. Trigger the target action once.
3. Save the exact command, app state, timestamp, and observed logs.
4. Add stack traces only when the call origin is unclear.
5. Modify behavior only after the original data path is visible.

## Validation

For each hook, verify:

- The script loaded without exceptions.
- The target hook installed exactly once.
- The user action produced hook output.
- The output matches the expected layer. Example: an OkHttp hook should show
  HTTP methods/URLs, not only generic app lifecycle calls.
- The app still runs unless the goal is to diagnose a crash.

## Escalation Path

If no output appears:

1. Confirm spawn vs attach timing.
2. Confirm package/process name.
3. Confirm class/module is loaded.
4. Try overload enumeration or ClassLoader discovery.
5. For native targets, wait for `dlopen`.
6. For protected/packed apps, observe class loading and DEX loading before
   trying app-specific classes.
