# React Native and Hermes

## Signals

- `assets/index.android.bundle`
- `*.hbc`
- `libhermes.so`
- `libreactnativejni.so`

## Approach

If a plain JS bundle exists, extract and analyze it with
`web-api-reverse-engineering`. If Hermes bytecode exists, preserve the `.hbc`
file and use Hermes-specific tooling where available. Use Frida/OkHttp hooks to
observe native requests when bundle analysis is incomplete.
