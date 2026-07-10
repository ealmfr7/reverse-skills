# Network Hooks

## Goal

Use network hooks to observe request construction inside the app. Prefer proxy
captures for ordinary HTTP analysis; use Frida when traffic is encrypted before
HTTP, proxying is blocked, or request construction must be understood in code.

## OkHttp

OkHttp is a high-value hook point for many Android apps. Hook:

- `okhttp3.Request$Builder.url`
- `okhttp3.Request$Builder.header`
- `okhttp3.OkHttpClient.newCall`
- `okhttp3.ResponseBody.string` when safe

Use `scripts/templates/okhttp-hook.js`.

Do not consume a response body with `.string()` unless the hook rebuilds or the
test can tolerate changing app behavior. Reading a body stream can affect the
app.

## Retrofit

Retrofit methods are often interfaces. If the interface is clear in JADX, hook
the generated call path indirectly through OkHttp or hook repository methods
that call the Retrofit service.

## WebView

Use WebView hooks when the app is hybrid or exposes a JavaScript bridge:

- `WebView.loadUrl`
- `WebView.postUrl`
- `WebView.evaluateJavascript`
- `WebView.addJavascriptInterface`

Use `scripts/templates/webview-hook.js`.

## Headers and Secrets

Log headers carefully. If output may include tokens, redact before sharing.
Document whether a value is observed, inferred, or user-provided.

## TLS and Pinning

This skill can help observe TLS-related code in authorized labs. Do not provide
instructions to abuse third-party services. Prefer documenting which trust
manager, certificate pinner, or network security config is used before changing
runtime behavior.
