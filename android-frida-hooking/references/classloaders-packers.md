# ClassLoaders and Packed Apps

## Symptoms

Use this workflow when:

- `Java.use("com.example.Class")` throws `ClassNotFoundException`.
- JADX shows a class but Frida cannot see it at attach time.
- The app loads DEX dynamically.
- The app uses plugin frameworks, packers, or multiple processes.

## Enumerate Loaded Classes

```javascript
Java.perform(function () {
    Java.enumerateLoadedClasses({
        onMatch(name) {
            if (name.indexOf("com.example") !== -1) {
                console.log(name);
            }
        },
        onComplete() {
            console.log("done");
        }
    });
});
```

## Enumerate ClassLoaders

Use `scripts/templates/classloader-hook.js` to find loaders that can resolve the
target class. Once found, set `Java.classFactory.loader` before `Java.use()`.

## Hook Dynamic DEX Loading

Watch `dalvik.system.DexClassLoader`, `PathClassLoader`, or app-specific loader
wrappers when classes appear after login or feature navigation.

## Multi-Process Apps

Check process names:

```bash
adb shell ps -A | grep com.example
```

Attach to the process that owns the target behavior. Push notification, WebView,
and sandboxed service code may run outside the main process.

## Packer Strategy

Do not guess class names in packed apps. First observe:

- DEX file loading paths
- ClassLoader instances
- native library loads
- calls to `loadClass`
- late-loaded app package names

Then install the specific hook after the target class resolves.
