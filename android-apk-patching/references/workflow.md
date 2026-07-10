# APK Patching Workflow

## Common Tasks

| Goal | Preferred edit |
|---|---|
| Change app label/icon/resource | `res/` XML or assets |
| Add test network config for owned app | `res/xml/network_security_config.xml` + manifest attribute |
| Add debug logging in lab | narrow smali method edit |
| Inject Frida Gadget into authorized test build | native lib + manifest/library loader edits |
| Fix install failure | inspect signature scheme, minSdk, ABI, manifest |

## Smali Safety

- Keep register counts consistent.
- Prefer adding logs around existing branches instead of rewriting control flow.
- Rebuild after each small edit.
- If a method is complex, use Frida first to prove the behavior before patching.

## Signing Notes

Use `zipalign` before `apksigner`. Any change after signing invalidates the APK
signature. Use a test keystore for lab builds and document that the package will
not update over a build signed with a different cert unless the original is
uninstalled or the cert lineage allows it.

## Operable Lab Flow

```bash
bash android-apk-patching/scripts/check-apk-patching-deps.sh
bash android-apk-patching/scripts/decode-apk.sh app.apk work/app
python3 android-apk-patching/scripts/add-network-security-config.py work/app --trust-user-certs
bash android-apk-patching/scripts/make-test-keystore.sh test.keystore
bash android-apk-patching/scripts/rebuild-sign-apk.sh work/app build test.keystore androiddebugkey android
bash android-apk-patching/scripts/install-and-logcat.sh build/app-signed.apk com.example
```

Use `--cleartext` only for local lab targets where cleartext traffic is part of
the test. For ordinary proxy testing, prefer `--trust-user-certs`.

## Generated Network Security Config

The helper writes:

- `res/xml/network_security_config.xml`
- `android:networkSecurityConfig="@xml/network_security_config"` on
  `<application>`

It is idempotent: running it again rewrites the same config instead of adding
duplicate manifest attributes.

## Troubleshooting

- `INSTALL_FAILED_UPDATE_INCOMPATIBLE`: uninstall old app or use same signing key.
- `INSTALL_PARSE_FAILED_NO_CERTIFICATES`: sign with `apksigner`.
- `INSTALL_FAILED_NO_MATCHING_ABIS`: the patched APK lacks native libraries for
  the device ABI.
- Runtime crash after smali patch: compare logcat stack trace with edited method.
- Resource build errors: inspect `apktool.yml`, framework files, and invalid XML.
- Network config has no effect: verify the app process is using the patched APK,
  inspect `AndroidManifest.xml`, and confirm the target Android trust behavior.
