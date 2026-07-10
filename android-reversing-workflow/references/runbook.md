# Master Android Reversing Runbook

## Default Flow

1. Fingerprint APK: framework, manifest, permissions, native libs, packers.
2. Static analysis: JADX/apktool for Java/Kotlin/resources.
3. If packed: run app in lab and dump DEX.
4. If network goal: capture proxy traffic and correlate with code.
5. If runtime behavior matters: write Frida hooks.
6. If native `.so` matters: use Ghidra/IDA, then Frida native hooks.
7. If native algorithm is isolated but hard to run: emulate with Unicorn.
8. If a lab patch is needed: patch/rebuild/sign/install.

Use the local tooling for the first branch:

```bash
bash android-reversing-workflow/scripts/fingerprint-apk.sh app.apk > fingerprint.txt
python3 android-reversing-workflow/scripts/route-android-task.py --fingerprint fingerprint.txt
```

For a full decision tree, read `decision-tree.md`. For examples, read
`examples.md`.

## Common Branches

### Login/API analysis

`android-reverse-engineering` -> `android-traffic-analysis` ->
`android-frida-hooking` -> `web-api-reverse-engineering`

### Packed APK

`android-reverse-engineering` -> `rev-dex-dumper` ->
`android-reverse-engineering` on dumped DEX -> `android-frida-hooking`

### Native signing algorithm

`android-reverse-engineering` -> `android-arm64-native-basics` ->
`rev-ghidra` or `rev-idapython` -> `rev-symbol`/`rev-struct` ->
`android-frida-hooking` or `rev-unicorn-debug`

### UDP or custom datagram protocol

`udp-protocol-reverse-engineering` -> `android-frida-hooking` for
`sendto`/`recvfrom` or `DatagramSocket` correlation -> `rev-ghidra` /
`rev-idapython` if parser, crypto, or compression is native.

### Suspicious APK

`android-malware-triage` -> static IOC report -> isolated dynamic analysis only
if necessary and authorized.
