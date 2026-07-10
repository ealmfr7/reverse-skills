# JNI Argument Mapping

## Instance Native Method

Java:

```java
native byte[] sign(byte[] body, String user);
```

Native prototype:

```c
jbyteArray sign(JNIEnv *env, jobject thiz, jbyteArray body, jstring user);
```

ARM64 at entry:

```text
x0 = JNIEnv *
x1 = jobject thiz
x2 = jbyteArray body
x3 = jstring user
```

## Static Native Method

Static methods receive `jclass` instead of `jobject`:

```text
x0 = JNIEnv *
x1 = jclass clazz
x2 = first Java argument
```

## Frida Native Hook View

In `Interceptor.attach`, `args[0]` maps to `x0`, `args[1]` to `x1`, etc.

For JNI methods, app-level Java arguments usually start at:

- `args[2]` for instance methods
- `args[2]` for static methods

The difference is whether `args[1]` is an object instance or class reference.
