# Setup

## Host Tools

Install:

- Android platform tools: `adb`
- Python package: `frida-tools`
- Matching `frida-server` binary for the device ABI

Check:

```bash
adb devices
frida --version
adb shell getprop ro.product.cpu.abi
```

## Device Setup

Rooted emulator/device workflow:

```bash
adb push frida-server /data/local/tmp/frida-server
adb shell chmod 755 /data/local/tmp/frida-server
adb shell su -c /data/local/tmp/frida-server
frida-ps -U
```

If `su` is unavailable, use a rooted emulator image or consider Frida Gadget for
authorized test builds.

## Version Matching

Keep `frida-tools` and `frida-server` compatible. If attach fails with protocol
or handshake errors, install a matching server release.

## Spawn vs Attach

Use spawn when early initialization matters:

```bash
frida -U -f com.example.app -l hook.js
```

Use attach when the target behavior happens after the app is already running:

```bash
frida -U com.example.app -l hook.js
```

## Useful ADB Commands

```bash
adb shell pidof com.example.app
adb shell ps -A | grep example
adb logcat | grep -i frida
adb shell run-as com.example.app ls
```

`run-as` only works for debuggable apps.
