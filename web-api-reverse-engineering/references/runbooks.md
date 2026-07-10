# Scenario Runbooks

Use these runbooks after `scripts/fingerprint-web.py` or after strong evidence from HAR/JS scans. Keep the scope authorized and prefer read-only actions until the user approves mutations.

## Universal First Pass

Run:

```bash
bash scripts/check-deps.sh
python3 scripts/fingerprint-web.py <url> --json-out fingerprint.json
```

Then choose the narrowest matching runbook. Preserve these artifacts:

- `fingerprint.json`
- `manifest.json` from `dump-website-js.py`
- downloaded scripts/source maps
- HAR file when auth or runtime user actions matter
- notes on account, role, tenant, and timestamp

Recommended artifact pipeline:

```bash
python3 scripts/extract-endpoints.py dumps/site --base-url <url> --json-out endpoints.json --markdown-out endpoints.md
python3 scripts/extract-sourcemaps.py dumps/site --out extracted-sources --json-out sourcemaps.json
python3 scripts/analyze-graphql.py dumps/site --json-out graphql.json --markdown-out graphql.md
python3 scripts/build-report.py --fingerprint fingerprint.json --endpoints endpoints.json --graphql graphql.json --out report.md
python3 scripts/generate-client-skeleton.py endpoints.json --lang python --out generated-client
```

## Next.js

Evidence:

- `__NEXT_DATA__`
- `/_next/static/`
- `/_next/data/*.json`
- Next.js chunks or route data

Run:

```bash
python3 scripts/dump-website-js.py <url> --out dumps/site --browser
python3 scripts/scan-js-bundle.py dumps/site
python3 scripts/extract-endpoints.py dumps/site --base-url <url> --json-out endpoints.json --markdown-out endpoints.md
```

Focus:

- Parse `__NEXT_DATA__` for route props, build ID, public runtime config, and data paths.
- Probe `/_next/data/<build-id>/<route>.json` only for routes observed in the app.
- Separate Next internals from backend API calls.
- Look for API routes under `/api/*`, GraphQL clients, and server action/fetch wrappers.

Output:

- Build ID and route data inventory.
- API endpoints called by page transitions.
- Distinction between static props, route data, and backend APIs.

## GraphQL

Evidence:

- `/graphql`
- `query`, `mutation`, `subscription`
- `__typename`
- Apollo, Relay, urql, persisted query hashes

Run:

```bash
python3 scripts/dump-website-js.py <url> --out dumps/site --browser
python3 scripts/scan-js-bundle.py dumps/site
python3 scripts/analyze-graphql.py dumps/site --base-url <url> --json-out graphql.json --markdown-out graphql.md
```

If user provides HAR:

```bash
python3 scripts/har-summary.py capture.har
```

Focus:

- Endpoint URL and auth headers.
- POST bodies and GET query parameters: `query`, `operationName`, `variables`, `extensions`.
- Operation names.
- Variables and response shape.
- Persisted query hashes and how they map to operations.
- Batching format.
- Subscription transport for WebSocket GraphQL.

Output:

- Operation inventory grouped by query/mutation/subscription.
- Variables and response model examples.
- Reproducible curl for one low-risk query.
- Notes on introspection only if authorized.

## Static-Only or Mostly Static Site

Evidence:

- Few or no XHR/fetch/API signals.
- Mostly HTML, CSS, static JS, CDN assets.
- No login/session indicators.

Run:

```bash
python3 scripts/dump-website-js.py <url> --out dumps/site
python3 scripts/scan-js-bundle.py dumps/site
python3 scripts/extract-endpoints.py dumps/site --base-url <url> --json-out endpoints.json --markdown-out endpoints.md
```

Focus:

- Confirm whether there is any API surface.
- Record forms, search endpoints, RSS/sitemap, static JSON, or embedded data files.
- Avoid overfitting framework guesses when no runtime API exists.

Output:

- Static asset inventory.
- Any discovered JSON/data endpoints.
- Statement that no API behavior was observed, if true.

## SPA Runtime App

Evidence:

- Vite/React/Vue/Angular/Svelte/Remix/Astro bundles.
- Initial HTML has minimal content.
- Runtime-injected scripts or route chunks.
- API calls happen only after route navigation.

Run:

```bash
bash scripts/check-deps.sh
python3 scripts/dump-website-js.py <url> --out dumps/site --browser
python3 scripts/scan-js-bundle.py dumps/site
python3 scripts/extract-endpoints.py dumps/site --base-url <url> --json-out endpoints.json --markdown-out endpoints.md
```

If specific UI interactions are required, capture a HAR instead of guessing:

```bash
python3 scripts/capture-playwright-flow.py <url> --out flow.har
python3 scripts/har-summary.py capture.har
```

Focus:

- Route chunks and lazy-loaded modules.
- Fetch/axios/request wrappers.
- Environment variables embedded at build time.
- Feature flags and API base URL construction.

Output:

- API base URL candidates.
- Request wrapper location.
- Route-to-endpoint map for observed flows.

## RPC-Style APIs: tRPC or gRPC-Web

Evidence:

- `/trpc/`
- `@trpc/client`
- `grpc-web`
- `application/grpc-web`

Run:

```bash
python3 scripts/dump-website-js.py <url> --out dumps/site --browser
python3 scripts/extract-endpoints.py dumps/site --base-url <url> --json-out endpoints.json --markdown-out endpoints.md
```

Focus:

- Procedure names rather than REST resources.
- Batching format.
- Input serialization.
- Auth/session wrapper.
- Whether the browser client uses generated types or runtime schemas.

Output:

- Procedure inventory.
- Request/response envelope examples.
- Minimal safe client sketch only after auth and serialization are understood.

## Hosted Backend/Auth Providers

Evidence:

- Supabase or Firebase SDKs.
- Auth0, Clerk, Cognito, OAuth/OIDC/PKCE terms.
- Stripe hosted checkout or payment SDKs.

Focus:

- Prefer official SDKs and documented APIs when available.
- Separate provider SDK calls from first-party backend calls.
- Do not reconstruct payment or auth flows by copying private tokens.

Output:

- Provider inventory.
- Official SDK/API recommendation.
- First-party endpoints that wrap provider operations.

## Auth-Heavy App

Evidence:

- Login redirects.
- OIDC/OAuth/SAML/PKCE terms.
- CSRF headers/cookies.
- Session refresh endpoints.
- Most API calls fail without browser state.

Run:

```bash
python3 scripts/capture-playwright-flow.py <url> --out authorized-flow.har
python3 scripts/har-summary.py authorized-flow.har
python3 scripts/har-summary.py authorized-flow.har --json-out har.json --markdown-out har.md
```

Focus:

- Use an authorized test account.
- Map login, token issuance, refresh, CSRF, and logout.
- Do not extract long-lived personal tokens from a browser profile.
- Reproduce only the smallest safe request outside the browser.

Output:

- Auth/session lifecycle.
- Required cookies/headers by endpoint.
- Token refresh behavior.
- Safe client-auth strategy.

## WebSocket or SSE

Evidence:

- `WebSocket(`
- `EventSource(`
- `ws://` or `wss://`
- GraphQL subscriptions

Run:

```bash
python3 scripts/dump-website-js.py <url> --out dumps/site --browser
python3 scripts/scan-js-bundle.py dumps/site
```

Prefer HAR/DevTools capture for real interaction flows.

Focus:

- Handshake URL.
- Auth carrier: cookie, header, query token, or first message.
- HAR `_webSocketMessages` or browser DevTools message frames when available.
- Subscribe/unsubscribe message formats.
- Heartbeat and reconnect behavior.
- Event envelope and event names.

Output:

- Connection lifecycle.
- Message schema examples.
- Minimal read-only client sketch if authorized.

## Protection or Bot-Friction Signals

Evidence:

- Cloudflare/Akamai cookies or headers.
- reCAPTCHA/hCaptcha scripts.
- Bot manager scripts.
- Browser-only failures in curl.

Run:

```bash
python3 scripts/fingerprint-web.py <url> --json-out fingerprint.json
```

Focus:

- Do not bypass protections.
- Prefer browser DevTools or HAR from an authorized session.
- Document that a server-side client may require official API access, partner credentials, or a supported SDK.

Output:

- Friction signals observed.
- Safe analysis path.
- Explicit limitations for client reconstruction.
