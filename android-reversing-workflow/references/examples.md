# Routing Examples

## Packed APK

Evidence:

```text
JADX shows StubApp, ShellApplication, DexClassLoader.
```

Route:

```text
android-reverse-engineering -> rev-dex-dumper -> android-reverse-engineering on dumped DEX -> android-frida-hooking
```

First validation:

```text
Dumped DEX contains app package classes absent from original JADX output.
```

## Login API With Token Signing

Evidence:

```text
OkHttp strings, Retrofit interfaces, native lib named libsign.so.
```

Route:

```text
android-traffic-analysis -> android-frida-hooking -> android-arm64-native-basics -> rev-ghidra
```

First validation:

```text
Captured login request plus Frida log showing token/signature inputs.
```

## Flutter APK

Evidence:

```text
libflutter.so, libapp.so, flutter_assets/.
```

Route:

```text
android-cross-platform-reversing -> android-frida-hooking for Java/native boundary
```

First validation:

```text
Fingerprint identifies Flutter; JADX Java code is treated as wrapper/plugin code.
```

## Unity Game

Evidence:

```text
libil2cpp.so and global-metadata.dat.
```

Route:

```text
android-cross-platform-reversing -> rev-u3d-dump -> rev-ghidra or rev-idapython
```

First validation:

```text
Recovered IL2CPP method/address mapping.
```

## Suspicious APK

Evidence:

```text
AccessibilityService, BOOT_COMPLETED receiver, SMS permissions, hardcoded domains.
```

Route:

```text
android-malware-triage
```

First validation:

```text
IOC report with SHA-256, package, permissions, components, domains, and confidence notes.
```

## Native Algorithm

Evidence:

```text
Java declares native byte[] decrypt(byte[]), libnative.so has JNI_OnLoad and no clear exports.
```

Route:

```text
android-arm64-native-basics -> rev-ghidra -> android-frida-hooking -> rev-unicorn-debug
```

First validation:

```text
RegisterNatives log maps Java method to native pointer, then Frida captures inputs/outputs.
```
