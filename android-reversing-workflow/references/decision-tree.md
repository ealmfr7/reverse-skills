# Android Reversing Decision Tree

## Start With Evidence

If the user provides an APK, run:

```bash
bash android-reversing-workflow/scripts/fingerprint-apk.sh app.apk > fingerprint.txt
python3 android-reversing-workflow/scripts/route-android-task.py --fingerprint fingerprint.txt
```

If the user provides only a goal, route the text:

```bash
python3 android-reversing-workflow/scripts/route-android-task.py "analyze login API and token signing"
```

## Decision Tree

1. Is the scope authorized?
   - No or unclear: ask for scope.
   - Yes: continue.

2. Is the APK suspicious/malware-focused?
   - Yes: use `android-malware-triage` first.
   - No: continue.

3. Is the app cross-platform?
   - Flutter/RN/Cordova/Xamarin/Unity markers: use
     `android-cross-platform-reversing`.
   - No or unclear: continue.

4. Does JADX show only stubs/loaders or dynamic DEX markers?
   - Yes: use `rev-dex-dumper` in an isolated lab.
   - No: continue.

5. Is the goal network/API behavior?
   - Yes: use `android-traffic-analysis` and `web-api-reverse-engineering`.
   - If traffic is hidden/encrypted before HTTP: add `android-frida-hooking`.

6. Is the goal runtime behavior?
   - Java/Kotlin: use `android-frida-hooking`.
   - quick exploration: use `android-objection`.
   - native function: add `android-arm64-native-basics` and `rev-ghidra` or
     `rev-idapython`.

7. Is a lab APK modification required?
   - Yes: use `android-apk-patching`.

8. Is native analysis unclear?
   - names unclear: `rev-symbol`
   - fields/structs unclear: `rev-struct`
   - isolated algorithm execution: `rev-unicorn-debug`

## Validation Signal

Every route should name a concrete validation signal:

- static route: specific class, manifest component, string, native lib, or asset
- traffic route: captured request/response or explained TLS failure
- hook route: hook installed and fired on the target action
- patch route: rebuilt APK installs and target behavior/log changes
- native route: function offset/name, xref, pseudocode, or emulation output
