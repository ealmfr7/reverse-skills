# Native and JNI Hooks

## When To Use Native Hooks

Use native hooks when:

- The app calls `System.loadLibrary`.
- JADX shows native method declarations.
- Important logic lives in `.so` files.
- Java hooks only show opaque byte arrays or wrapper calls.
- The app registers native methods dynamically.

## Module Timing

Do not assume a `.so` is loaded at script start. Use `dlopen`/`android_dlopen_ext`
timing from `scripts/templates/dlopen-hook.js`.

## Export Hooks

If the function is exported:

```javascript
const mod = Process.getModuleByName("libtarget.so");
const fn = mod.getExportByName("target_export");
Interceptor.attach(fn, {
    onEnter(args) {
        console.log("arg0:", args[0]);
    },
    onLeave(retval) {
        console.log("ret:", retval);
    }
});
```

Use `scripts/templates/native-export-hook.js`.

Generate a concrete native hook with:

```bash
python3 scripts/make-native-hook.py libtarget.so --export target_export --wait-load --out hook.js
python3 scripts/make-native-hook.py libtarget.so --offset 0x1234 --wait-load --out hook-offset.js
```

## JNI Names

Static JNI exports often look like:

```text
Java_com_example_NativeLib_methodName
```

Dynamic JNI registration uses `RegisterNatives`; use
`scripts/templates/register-natives-hook.js` to log Java method names,
signatures, and native function pointers.

## Pointers and Buffers

Read only when pointer validity and expected size are known:

```javascript
console.log(hexdump(args[0], { length: 64, ansi: false }));
```

Avoid large dumps by default. Keep output narrow and reproducible.

## Initialization Hooks

Avoid blind hooks on `.init`, `.init_array`, constructors, or `JNI_OnLoad`.
Prefer:

1. Hook a stable exported function after module load.
2. Hook `RegisterNatives` to map Java names to native addresses.
3. Hook `dlsym` if symbol lookup behavior is the target.
4. Hook `JNI_OnLoad` only with evidence that native registration or checks occur
   there.
