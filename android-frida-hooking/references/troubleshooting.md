# Troubleshooting

## `Java.use()` Cannot Find Class

Check:

- package/process name is correct
- app action that loads the feature has already happened
- class name matches JADX, including `$` for inner classes
- target process is not a secondary process
- ClassLoader workflow is needed

Read `references/classloaders-packers.md`.

## Overload Error

Print overloads:

```javascript
Target.method.overloads.forEach(function (ov) {
    console.log(ov.argumentTypes.map(t => t.className).join(", "));
});
```

Then hook the exact signature.

## App Crashes After Hook

Reduce the hook:

1. Remove return modification.
2. Remove argument modification.
3. Remove heavy stack traces.
4. Wrap logging in `try/catch`.
5. Confirm the original method is called with the original arguments.

## Native Function Not Found

Check:

```javascript
Process.enumerateModules().forEach(m => console.log(m.name));
```

Then wait for module load using the dlopen template. If the symbol is not
exported, use JNI registration logs, string xrefs in a disassembler, or
offset-based attachment only after verifying the module base and version.

## Frida Cannot Attach

Check:

- `adb devices`
- `frida-ps -U`
- matching Frida server/client versions
- rooted device/emulator or Gadget setup
- correct architecture server binary
- app not running under a different Android user/profile

## No Hook Output

Confirm the user action reaches the target. Add a broader hook one layer above
or below the suspected function. Example: if a repository hook does not fire,
hook OkHttp to confirm the network path, or hook the UI click handler to confirm
the action path.
