# Cross-Platform APK Triage

## File Markers

| Framework | Markers |
|---|---|
| Flutter | `libflutter.so`, `libapp.so`, `flutter_assets/` |
| React Native | `assets/index.android.bundle`, `*.hbc`, `libhermes.so` |
| Cordova/Capacitor | `assets/www/`, `cordova.js`, `capacitor.config.*` |
| Xamarin | `assemblies/`, `libmonodroid.so`, `.dll` assemblies |
| Unity | `libil2cpp.so`, `global-metadata.dat`, `UnityPlayerActivity` |

## Routing

- Flutter: Java code is mostly shell/plugin bridge; focus on Dart/native assets.
- React Native: inspect JS/Hermes before native code.
- Cordova: web reversing workflow applies to `assets/www`.
- Unity: run IL2CPP metadata workflow.
- Xamarin: inspect managed assemblies when available.

## Commands

```bash
python3 android-cross-platform-reversing/scripts/fingerprint-framework.py app.apk --json-out framework.json
python3 android-cross-platform-reversing/scripts/extract-framework-assets.py app.apk --out extracted-framework
```

## Follow-up Skills

| Framework | Follow-up |
|---|---|
| Flutter | `android-frida-hooking`, `rev-ghidra` for native assets |
| React Native | `web-api-reverse-engineering`, `android-frida-hooking` |
| Cordova/Capacitor | `web-api-reverse-engineering`, `android-frida-hooking` WebView templates |
| Xamarin | managed assembly tooling, `rev-ghidra` for native glue |
| Unity IL2CPP | `rev-u3d-dump`, then `rev-ghidra` or `rev-idapython` |
