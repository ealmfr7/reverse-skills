---
name: android-cross-platform-reversing
description: Triage and analyze Android APKs built with Flutter, React Native, Hermes, Cordova, Capacitor, Xamarin, Unity, or other cross-platform stacks. Use when normal Java/Kotlin decompilation is low-signal, when APK assets contain JS bundles or Dart/Flutter/native markers, or when Codex needs to choose framework-specific reverse engineering tools before JADX/Frida work.
---

# Android Cross-Platform Reversing

Use this skill before deep Java/Kotlin analysis when the APK may be Flutter,
React Native, Cordova/Capacitor, Xamarin, Unity, or another framework.

## Workflow

1. Fingerprint the APK by files, assets, native libs, package names, and strings:
   ```bash
   reverse-skill android-cross-platform-reversing fingerprint-framework app.apk --json-out framework.json
   ```
2. Extract framework assets when the fingerprint finds useful artifacts:
   ```bash
   reverse-skill android-cross-platform-reversing extract-framework-assets app.apk --out extracted-framework
   ```
3. Route by framework:
   - Flutter: inspect `libflutter.so`, `libapp.so`, assets, Dart snapshots.
   - React Native: inspect JS bundle or Hermes bytecode.
   - Cordova/Capacitor: inspect `assets/www`.
   - Xamarin: inspect assemblies and managed metadata.
   - Unity: use `rev-u3d-dump` for IL2CPP.
4. Only use JADX for the Android wrapper and bridge code when the real logic
   lives elsewhere.

Read `references/workflow.md`. For framework-specific notes, read:
`references/flutter.md`, `references/react-native-hermes.md`,
`references/cordova-capacitor.md`, or `references/xamarin.md`.

## Tool Outputs

- `reverse-skill android-cross-platform-reversing fingerprint-framework`: prints `FRAMEWORKS:<names>` and can write
  JSON evidence with recommended next steps.
- `reverse-skill android-cross-platform-reversing extract-framework-assets`: extracts JS bundles, Hermes bytecode,
  Cordova assets, Flutter assets/libs, and Unity IL2CPP metadata/libraries.

## Source Anchors

- React Native Hermes docs: https://reactnative.dev/docs/hermes
- Expo Hermes guide: https://docs.expo.dev/guides/using-hermes/
- Unity IL2CPP workflow: local `rev-u3d-dump`
