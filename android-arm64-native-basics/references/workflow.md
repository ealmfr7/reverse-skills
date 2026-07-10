# ARM64 Native Basics

## JNI Argument Mapping

Java:

```java
native int sign(byte[] data, String user);
```

Static JNI C-style:

```c
Java_pkg_Class_sign(JNIEnv *env, jobject thiz, jbyteArray data, jstring user)
```

ARM64 entry:

```text
x0 = JNIEnv *
x1 = jobject/jclass
x2 = data
x3 = user
```

## Offset Math

If Ghidra shows function offset `0x12340` in `libtarget.so`:

```javascript
const mod = Process.getModuleByName("libtarget.so");
const fn = mod.base.add(0x12340);
```

Confirm whether the tool displays file offset, image offset, or rebased virtual
address before using it in Frida.

Use the helper:

```bash
python3 android-arm64-native-basics/scripts/offset-math.py \
  --image-base 0x100000 \
  --entry 0x101234 \
  --module-base 0x7a00000000
```

## Reading Pseudocode

- `obj + 0x18` suggests a struct/class field.
- `(*env)->GetStringUTFChars` indicates JNI string conversion.
- `memcmp`, `strcmp`, `EVP_*`, `AES_*`, `SHA*` are useful semantic anchors.

## Focused References

- `arm64-calling-convention.md`: registers and instruction reading.
- `jni-argument-mapping.md`: Java native declarations to `x0`/`args[0]`.
- `offset-math.md`: static entry, image base, runtime module base.
- `frida-native-argument-decoding.md`: pointer/string/buffer logging.
