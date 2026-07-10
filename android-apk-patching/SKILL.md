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
   bash scripts/check-apk-patching-deps.sh
   ```
3. Decode:
   ```bash
   bash scripts/decode-apk.sh app.apk work/app
   ```
4. Patch the smallest surface: manifest/resource XML first, smali only when
   required and understood.
   For CA/proxy testing:
   ```bash
   python3 scripts/add-network-security-config.py work/app --trust-user-certs
   ```
5. Rebuild:
   ```bash
   bash scripts/make-test-keystore.sh test.keystore
   bash scripts/rebuild-sign-apk.sh work/app build test.keystore androiddebugkey android
   ```
6. Install and capture logs:
   ```bash
   bash scripts/install-and-logcat.sh build/app-signed.apk com.example
   ```

For details and troubleshooting, read `references/workflow.md`.

## Script Outputs

- `scripts/check-apk-patching-deps.sh`: reports required tools.
- `scripts/decode-apk.sh <apk> <out-dir>`: decodes with apktool and prints
  `DECODED:<out-dir>`.
- `scripts/add-network-security-config.py <decoded-project>`: creates
  `res/xml/network_security_config.xml` and updates the manifest application
  attribute.
- `scripts/make-test-keystore.sh [keystore] [alias] [password]`: creates a lab
  signing key.
- `scripts/rebuild-sign-apk.sh <decoded-project> [out-dir] [keystore] [alias] [password]`:
  rebuilds, zipaligns, signs, verifies, and prints `SIGNED:<apk>`.
- `scripts/install-and-logcat.sh <signed-apk> [filter]`: installs and starts
  logcat.

## Source Anchors

- Apktool documentation: https://apktool.org/
- Android `zipalign`: https://developer.android.com/tools/zipalign
- Android `apksigner`: https://developer.android.com/tools/apksigner
- Android Network Security Config: https://developer.android.com/privacy-and-security/security-config
