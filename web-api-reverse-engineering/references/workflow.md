# Web/API Reverse Engineering Workflow

Use this workflow for authorized analysis of a web application whose browser client talks to undocumented or partially documented APIs.

## 1. Scope and Goal

Record:

- Target application and environment.
- Authorized account or test tenant.
- User role and feature area.
- Desired output: docs, endpoint list, client library, migration plan, or tests.
- Explicit exclusions such as production mutation endpoints, payment flows, admin actions, or third-party domains.

If the user cannot confirm authorization, stop and ask for scope.

## 2. Capture Baseline Traffic

Use Chrome/Edge DevTools Network first unless the task requires a proxy.

Capture:

- Page load with cache disabled.
- Login/session establishment when in scope.
- One clean interaction per target feature.
- Error cases when safe: invalid input, empty result, expired session, permission denied.
- HAR export when the user can safely share it.

Sanitize captures before sharing or committing:

- Cookies, bearer tokens, API keys, CSRF tokens, session IDs.
- Personal data and tenant identifiers.
- Internal hostnames when sensitive.

## 3. Build the Request Inventory

For each relevant request, record:

- Feature or UI action that triggered it.
- Initiator: document, fetch/XHR, script file, WebSocket, worker.
- Method, path, query string, and host.
- Required headers and optional headers.
- Cookies or Authorization scheme.
- Request body and content type.
- Response schema, status codes, and pagination fields.
- Ordering dependencies on previous calls.
- Cache behavior and ETags if relevant.

Group noise separately:

- Static assets.
- Telemetry/analytics.
- Feature flag polling.
- Ads, CDNs, fonts, and third-party SDKs.

## 4. Reproduce Outside the Browser

Start with the browser's "Copy as cURL" output, then simplify.

Simplification loop:

1. Run the copied request exactly.
2. Remove one header at a time.
3. Replace volatile values with named variables.
4. Confirm the response still matches.
5. Note which values are required, optional, inferred, or unknown.

Common required values:

- `Authorization` bearer token.
- Session cookies.
- CSRF token header or form field.
- `Content-Type` and `Accept`.
- Tenant, organization, locale, or feature headers.
- Request signature, timestamp, nonce, or device identifier.

Do not assume browser-only headers are required. `Origin`, `Referer`, `Sec-Fetch-*`, and CORS-related behavior may be enforced by some servers, but many APIs do not require them outside a browser.

## 5. Understand Authentication and Session Renewal

Map:

- Login endpoint and redirect flow.
- Cookie attributes and token storage location.
- CSRF token source and refresh behavior.
- Access token expiry and refresh token flow.
- Logout and session invalidation.
- MFA/2FA boundaries if present.

For OAuth/OIDC/SAML flows, prefer using documented provider flows and official SDKs when available. Do not extract or hard-code long-lived tokens from a browser profile.

## 6. Investigate Frontend Code Only When Needed

Read JavaScript bundles when traffic alone cannot explain:

- Dynamic endpoint construction.
- Request signing or hashing.
- Persisted GraphQL operation IDs.
- Client-side encryption/compression.
- Feature flags and hidden routes.
- WebSocket message formats.

Use source maps when publicly available. Otherwise beautify only the relevant bundle section and search for endpoint paths, GraphQL operation names, header names, or error strings observed in traffic.

## 7. Handle API Styles

REST/JSON:

- Identify resource paths, verbs, filters, pagination, sorting, and idempotency.
- Capture create/update/delete carefully in a safe test tenant.

GraphQL:

- Identify endpoint, operation names, variables, persisted query hashes, and batching.
- Try introspection only when authorized and appropriate.
- Map query/mutation names to UI features.

WebSocket/SSE:

- Capture handshake URL, auth headers or query params, subscription messages, heartbeat behavior, and reconnect rules.
- Record message envelopes and event types.

Multipart/file APIs:

- Record boundaries conceptually, file field names, metadata fields, content type, upload session creation, and completion calls.

## 8. Build the Client

Start with a minimal wrapper:

- Base URL and environment config.
- Session/auth provider.
- Request function with headers, cookies, timeout, retries, and error handling.
- One endpoint per proven workflow.
- Fixture-based tests from sanitized responses.

Avoid copying entire browser clients. Implement the protocol surface you need, with clear notes where behavior is inferred.

## 9. Deliverables Checklist

Include:

- Scope and authorization notes.
- Endpoint inventory.
- Auth/session lifecycle.
- Reproduction commands.
- Client code or pseudocode.
- Test fixtures or examples.
- Known unknowns.
- Operational constraints: rate limits, ToS, data sensitivity, brittle internals.
