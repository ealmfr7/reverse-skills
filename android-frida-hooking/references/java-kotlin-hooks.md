# Java and Kotlin Hooks

## Core Pattern

Use `Java.perform()` so hooks run after the VM is ready.

```javascript
Java.perform(function () {
    const Target = Java.use("com.example.Target");
    Target.method.implementation = function (arg) {
        console.log("arg:", arg);
        const ret = this.method(arg);
        console.log("ret:", ret);
        return ret;
    };
});
```

## Overloads

If a method has overloads, select the exact signature:

```javascript
Target.method.overload("java.lang.String", "int").implementation = function (s, i) {
    console.log("s:", s, "i:", i);
    return this.method(s, i);
};
```

Use `scripts/templates/java-overloads-hook.js` to print all overload signatures.

Generate a concrete overload hook with:

```bash
python3 scripts/make-java-hook.py com.example.Target method \
  --overload java.lang.String,int \
  --stacktrace \
  --out hook.js
```

## Static Methods

Static methods are hooked the same way, but call through the class wrapper:

```javascript
Target.staticMethod.implementation = function (value) {
    const ret = Target.staticMethod(value);
    console.log("static ret:", ret);
    return ret;
};
```

## Constructors

Constructors use `$init`:

```javascript
Target.$init.overload("java.lang.String").implementation = function (s) {
    console.log("new Target:", s);
    return this.$init(s);
};
```

## Kotlin Notes

- Kotlin top-level functions often compile into `FileNameKt` classes.
- Companion object methods may live under `ClassName$Companion`.
- Suspend functions may include a `kotlin.coroutines.Continuation` parameter.
- Default arguments can generate `$default` helper methods.
- Backtick or special names may need bracket access: `Target["method-name"]`.

## Type Handling

Common conversions:

```javascript
String(obj)
Java.cast(obj, Java.use("java.lang.String"))
Java.array("byte", [0x41, 0x42])
```

Byte arrays:

```javascript
function bytesToHex(arr) {
    const out = [];
    for (let i = 0; i < arr.length; i++) {
        out.push(("0" + (arr[i] & 0xff).toString(16)).slice(-2));
    }
    return out.join("");
}
```

## Stack Traces

Use stack traces sparingly when call origin is unclear:

```javascript
const Exception = Java.use("java.lang.Exception");
const Log = Java.use("android.util.Log");
console.log(Log.getStackTraceString(Exception.$new()));
```

Use `scripts/templates/system-loadlibrary-hook.js` when native library loading is
part of the call flow. Use `scripts/templates/dexclassloader-hook.js` when JADX
misses classes that appear only after runtime loading.
