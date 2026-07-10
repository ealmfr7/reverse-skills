# Flutter

## Signals

- `lib/<abi>/libflutter.so`
- `lib/<abi>/libapp.so`
- `assets/flutter_assets/`

## Approach

JADX mostly shows Android shell and plugin bridge code. Treat app logic as
Dart/native assets. Use Java/Frida hooks for platform channel boundaries,
network stack calls, and native library loading. Use native tooling if the goal
is inside `libapp.so`.
