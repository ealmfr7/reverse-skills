# Tooling Guide

Choose the least invasive tool that gives enough evidence.

## Web Fingerprint

Use `scripts/fingerprint-web.py` before dumping or scanning deeply.

Best for:

- Detecting framework signals such as Next.js, Nuxt, Angular, Vite, React, Vue, Svelte/SvelteKit, Remix, Astro, and webpack.
- Detecting platform/library signals such as Supabase, Firebase, Auth0, Clerk, Cognito, Stripe, Shopify, WordPress, Laravel, Rails, and Django.
- Detecting API style signals such as GraphQL, REST-like paths, RPC-style APIs, WebSocket/SSE, auth/session, and request signing.
- Detecting friction signals such as Cloudflare, Akamai, reCAPTCHA, and hCaptcha.
- Choosing whether to run static dump, browser dump, HAR analysis, or a focused framework runbook.

Example:

```bash
python3 scripts/fingerprint-web.py https://example.com --json-out fingerprint.json
```

Use the `recommended_commands` from the JSON when possible. Then read `references/runbooks.md` for the matching scenario.

## Structured Artifact Builders

Use these after a dump or HAR summary:

```bash
python3 scripts/extract-endpoints.py dumps/site --base-url https://example.com --json-out endpoints.json --markdown-out endpoints.md
python3 scripts/extract-sourcemaps.py dumps/site --out extracted-sources --json-out sourcemaps.json
python3 scripts/analyze-graphql.py dumps/site --json-out graphql.json --markdown-out graphql.md
python3 scripts/build-report.py --fingerprint fingerprint.json --endpoints endpoints.json --graphql graphql.json --out report.md
python3 scripts/generate-client-skeleton.py endpoints.json --lang python --out generated-client
```

Prefer these artifacts when building clients or reporting findings; they are easier to review than raw grep output.

Use `scripts/capture-playwright-flow.py <url> --out flow.har` when browser execution is required and Playwright is installed. It records a HAR that can be fed into `har-summary.py --json-out`.

## Browser DevTools

Use for first-pass analysis.

Best for:

- Network request inventory.
- Copying requests as cURL.
- Inspecting cookies, localStorage, sessionStorage, IndexedDB.
- Viewing request initiators and stack traces.
- Exporting HAR files.

Tips:

- Enable "Preserve log" for redirects and login flows.
- Disable cache while capturing.
- Filter by Fetch/XHR first, then review WebSocket and document requests.
- Export HAR only after sanitizing or controlling where secrets go.

Source: Chrome DevTools Network reference documents HAR import/export and request inspection: https://developer.chrome.com/docs/devtools/network/reference

Chrome DevTools Protocol's Network domain is the lower-level source for browser network events and bodies. Consider CDP-backed capture when HAR omits details needed for dynamic apps, service workers, redirects, or WebSocket/event timing: https://chromedevtools.github.io/devtools-protocol/tot/Network/

## Static Website JS Dump

Use `scripts/dump-website-js.py` when the user gives a URL and needs a local bundle dump before deeper analysis.

Best for:

- Unauthenticated public pages.
- Server-rendered pages that include script tags in initial HTML.
- Capturing JavaScript bundles and source maps for later `scan-js-bundle.py` analysis.

Example:

```bash
python3 scripts/dump-website-js.py https://example.com --out dumps/example
python3 scripts/scan-js-bundle.py dumps/example
```

Browser execution mode:

```bash
bash scripts/check-deps.sh
python3 scripts/dump-website-js.py https://example.com --out dumps/example --browser
```

Default behavior:

- Save `index.html`.
- Download same-origin external scripts.
- Skip cross-origin scripts but list them in `manifest.json`.
- Try to download source maps referenced by `sourceMappingURL`.
- Avoid executing JavaScript.

Use `--browser` when the target is a SPA that injects bundles after runtime execution or depends on browser state. The script requires the Python Playwright package; if missing, it prints `INSTALL_REQUIRED:playwright`. Install manually with:

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
```

If Playwright-managed Chromium is not installed, the script also tries system Chrome/Chromium channels. Use `--allow-cross-origin` only when collecting third-party or CDN-hosted scripts is in scope. For authenticated workflows, prefer HAR capture or a purpose-built Playwright script that logs in using authorized test credentials.

## Playwright

Use when flows require repeatable browser automation.

Best for:

- Capturing requests while performing deterministic UI steps.
- Waiting for specific API responses.
- Recording HAR for replay or mocking.
- Testing a reconstructed client against browser-observed behavior.

Typical pattern:

```ts
page.on('request', request => {
  console.log(request.method(), request.url());
});

page.on('response', response => {
  console.log(response.status(), response.url());
});
```

Source: Playwright documents monitoring and modifying HTTP/HTTPS traffic, including XHR/fetch and HAR usage: https://playwright.dev/docs/network

## mitmproxy

Use when a proxy capture is better than DevTools or when replay/interception is needed.

Best for:

- Capturing complete HTTP conversations.
- Intercepting and modifying requests in an authorized test.
- Replaying requests/responses.
- Scripted traffic analysis in Python.
- Inspecting non-browser clients or mobile/emulator traffic when configured correctly.

Watch for:

- TLS certificate setup.
- Certificate pinning in non-browser clients.
- Accidental capture of unrelated personal traffic.

Source: mitmproxy documents HTTP/HTTPS interception, replay, reverse proxy mode, and Python addons: https://docs.mitmproxy.org/stable/

## curl and HTTPie

Use to reduce a browser request to the minimum server-required protocol.

Best for:

- Verifying which headers are actually required.
- Saving reproducible examples.
- Debugging redirects, cookies, compression, and TLS.
- Producing examples that can be translated into code.

Tips:

- Keep one exact copied command and one simplified command.
- Use variables for host, token, tenant, and IDs.
- Add `--include` when response headers matter.
- Add `--cookie-jar` and `--cookie` for cookie flows.

Source: Everything curl is the primary open guide to curl and HTTP usage: https://everything.curl.dev/

## jq

Use for response exploration.

Best for:

- Extracting IDs from JSON.
- Comparing response shapes.
- Building endpoint inventories from HAR JSON.
- Redacting sensitive fields.

## JavaScript Bundle Inspection

Use after network analysis, not before.

Best for:

- Finding endpoint constants.
- Understanding request signing.
- Mapping GraphQL persisted query hashes.
- Locating feature flag names.

Tactics:

- Search for known path fragments, header names, error messages, operation names, and status labels.
- Prefer source maps when available.
- Beautify only relevant files or snippets.
- Track evidence back to observed traffic.

## GraphQL Tools

Use when requests target a GraphQL endpoint.

Best for:

- Identifying operation names and variables.
- Understanding fragments and persisted query hashes.
- Running introspection where authorized.
- Generating schemas/types from known operations.

Source: GraphQL documents introspection as a way to learn a schema's types and fields: https://graphql.org/learn/introspection/

GraphQL over HTTP can use POST bodies or GET query parameters. When analyzing HAR files, inspect both `postData.text` and URL query keys such as `query`, `operationName`, `variables`, and `extensions`: https://graphql.org/learn/serving-over-http/

## Source Maps

Use `scripts/extract-sourcemaps.py` when `.map` files are present.

Check:

- `sources`
- `sourcesContent`
- `sourceRoot`
- generated-to-original source names

Source maps can reconstruct original TypeScript/JSX modules when `sourcesContent` is embedded. The current script extracts embedded sources only; if content is missing, document source names but do not assume the original source is recoverable from the map alone.

Source: TC39 source map specification: https://tc39.es/source-map/

## HTTP Concepts to Check

Cookies:

- Check `Set-Cookie`, `HttpOnly`, `Secure`, `SameSite`, domain, path, and expiry.
- Browser storage may differ from server-side client requirements.

CORS:

- CORS is a browser enforcement mechanism, not a general HTTP client requirement.
- Server-side clients are not limited by browser preflight, but APIs may still validate `Origin` or CSRF tokens.

Source: MDN documents cookies and CORS behavior: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies and https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS

## Security Testing References

Use OWASP WSTG as a vocabulary and checklist source when the task touches auth, session management, or authorization boundaries.

Do not turn a client reconstruction task into vulnerability exploitation unless the user explicitly has authorization and asks for security testing within scope.

Source: https://owasp.org/www-project-web-security-testing-guide/

For API-specific risk framing, use OWASP API Security Top 10. This is useful when documenting client reconstruction limits around object authorization, broken authentication, unrestricted resource consumption, and unsafe consumption of APIs: https://owasp.org/API-Security/editions/2023/en/0x00-header/
