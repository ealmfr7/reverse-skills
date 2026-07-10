# Frida Native Argument Decoding

## Primitive Values

```javascript
console.log(args[0]);              // pointer
console.log(args[0].toInt32());    // int
console.log(args[0].toString());   // hex pointer string
```

## Strings and Buffers

```javascript
console.log(args[0].readCString());
console.log(args[0].readUtf8String());
console.log(hexdump(args[0], { length: 64, ansi: false }));
```

Only read memory when the pointer is valid and expected to reference readable
data.

## JNI Objects

Native `jstring`, `jbyteArray`, and object references are not raw C strings. Use
Java hooks when possible, or call JNI helper functions carefully if working in
native-only hooks.

Safer workflow:

1. Hook the Java native method declaration first.
2. Log Java-level arguments.
3. Hook the native function by offset/export.
4. Correlate Java logs with native `args[N]`.
