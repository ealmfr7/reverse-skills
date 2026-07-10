---
name: android-apk-patching
description: Patch, rebuild, align, sign, install, and verify Android APKs. Use when Codex needs apktool, smali/baksmali, AndroidManifest or resource edits, debug flag changes in lab builds, network security config edits, zipalign, apksigner, adb install, or troubleshooting APK rebuild/signature/install failures.
---

# Android APK Patching

## Workflow

1. Clarify goal: resource/manifest edit, smali edit, Frida Gadget lab build,
   debug/test config, certificate trust test, or reproducible patch.
2. Run dependency triage:
   ```bash
   reverse-skill android-apk-patching check-apk-patching-deps
   ```
3. Decode:
   ```bash
   reverse-skill android-apk-patching decode-apk app.apk work/app
   ```
4. Patch the smallest surface: manifest/resource XML first, smali only when
   required and understood.
   For CA/proxy testing:
   ```bash
   reverse-skill android-apk-patching add-network-security-config work/app --trust-user-certs
   ```
5. Rebuild:
   ```bash
   reverse-skill android-apk-patching make-test-keystore test.keystore
   reverse-skill android-apk-patching rebuild-sign-apk work/app build test.keystore androiddebugkey android
   ```
6. Install and capture logs:
   ```bash
   reverse-skill android-apk-patching install-and-logcat build/app-signed.apk com.example
   ```

For details and troubleshooting, read `references/workflow.md`.

## Tool Outputs

- `reverse-skill android-apk-patching check-apk-patching-deps`: reports required tools.
- `reverse-skill android-apk-patching decode-apk <apk> <out-dir>`: decodes with apktool and prints
  `DECODED:<out-dir>`.
- `reverse-skill android-apk-patching add-network-security-config <decoded-project>`: creates
  `res/xml/network_security_config.xml` and updates the manifest application
  attribute.
- `reverse-skill android-apk-patching make-test-keystore [keystore] [alias] [password]`: creates a lab
  signing key.
- `reverse-skill android-apk-patching rebuild-sign-apk <decoded-project> [out-dir] [keystore] [alias] [password]`:
  rebuilds, zipaligns, signs, verifies, and prints `SIGNED:<apk>`.
- `reverse-skill android-apk-patching install-and-logcat <signed-apk> [filter]`: installs and starts
  logcat.

## Source Anchors

- Apktool documentation: https://apktool.org/
- Android `zipalign`: https://developer.android.com/tools/zipalign
- Android `apksigner`: https://developer.android.com/tools/apksigner
- Android Network Security Config: https://developer.android.com/privacy-and-security/security-config
