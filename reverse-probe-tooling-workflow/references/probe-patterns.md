# Probe Patterns

## Frida Helpers

Every serious Frida probe should define or import equivalents of:

- `emit(type, event, data)`.
- `status(event, data)`.
- `safeString(value)`.
- redaction for URLs, paths, tokens, cookies, signatures, secrets, authorization, and session fields.
- bounded counters for noisy hooks.

## Java Hooks

Use Java probes for:

- Activity/Intent flow.
- Retrofit/OkHttp/WebView observations.
- model object summaries.
- JNI proxy calls with Java signatures.

Prefer `overloads.forEach` when method signatures are unknown or unstable. Emit `hook.skipped` instead of failing the script when a class or method is absent.

## Native Hooks

Use native probes for:

- exported functions.
- offset-based hooks after module load.
- socket, crypto, compression, encoder/decoder, and packet builder boundaries.

Wait for modules if they are loaded late. Emit module name, base, offset, and absolute address.

## Limits

Every probe that emits payloads should have byte and event limits. For deep captures, add focus ranges so later runs can narrow output.
