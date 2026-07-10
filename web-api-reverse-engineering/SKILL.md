---
name: web-api-reverse-engineering
description: Analyze authorized web applications to understand browser behavior, network traffic, JavaScript clients, authentication, API endpoints, GraphQL/WebSocket protocols, request signing, and undocumented data flows. Use when Codex needs to document how a web app works, reproduce browser requests, inspect HAR/network captures, review frontend bundles, or build a compatible API client in Python, Node.js, Go, or another language.
---

# Web API Reverse Engineering

## Safety Boundary

Work only on systems the user owns, operates, is contracted to test, or is otherwise authorized to analyze. Do not help bypass access controls, steal secrets, evade rate limits, or abuse private APIs. When authorization is unclear, ask for scope before proceeding.

## Quick Start

1. Clarify the goal: documentation, endpoint inventory, auth analysis, minimal client, test suite, or migration plan.
2. Ask for available artifacts: URL, HAR file, DevTools export, curl command, browser session notes, JS bundle, API examples, or existing client code.
3. Run the dependency checker when local analysis is needed:
   ```bash
   bash scripts/check-deps.sh
   ```
4. Fingerprint the target before choosing the scan path:
   ```bash
   python3 scripts/fingerprint-web.py https://example.com --json-out fingerprint.json
   ```
5. Dump client-side assets when the user provides a website URL:
   ```bash
   python3 scripts/dump-website-js.py https://example.com --out dumps/example
   python3 scripts/scan-js-bundle.py dumps/example
   ```
   For SPAs, runtime-injected scripts, or pages that need browser execution:
   ```bash
   bash scripts/check-deps.sh
   python3 scripts/dump-website-js.py https://example.com --out dumps/example --browser
   ```
6. Run fast triage before manual analysis:
   ```bash
   python3 scripts/har-summary.py capture.har
   python3 scripts/scan-js-bundle.py path/to/bundle-or-dir
   ```
7. Produce structured artifacts:
   ```bash
   python3 scripts/extract-endpoints.py dumps/example --base-url https://example.com --json-out endpoints.json --markdown-out endpoints.md
   python3 scripts/extract-sourcemaps.py dumps/example --out extracted-sources --json-out sourcemaps.json
   python3 scripts/analyze-graphql.py dumps/example --json-out graphql.json --markdown-out graphql.md
   python3 scripts/build-report.py --fingerprint fingerprint.json --endpoints endpoints.json --graphql graphql.json --out report.md
   ```
8. Preserve evidence before modifying behavior: capture baseline traffic and note account state, user role, timestamps, and environment.
9. Build a request inventory: method, URL, headers, cookies, body, response schema, status codes, initiator, and feature that triggered it.
10. Reproduce the smallest useful request outside the browser with `curl`, HTTPie, Python, or Node.js.
11. Generalize into a client only after auth, CSRF, pagination, retries, and error responses are understood.
12. Document unknowns and avoid guessing. Mark each conclusion as observed, inferred, or unverified.

## Workflow Selection

- For first-pass analysis of a website or HAR, read `references/workflow.md`.
- For choosing tooling, capture strategy, or proxy setup, read `references/tools.md`.
- For implementing a compatible client, read `references/client-patterns.md`.
- For scenario-specific paths after fingerprinting, read `references/runbooks.md`.
- For deterministic triage, use `scripts/fingerprint-web.py` on URLs, `scripts/dump-website-js.py` on public/static pages, `scripts/har-summary.py` on HAR files, and `scripts/scan-js-bundle.py` on JavaScript bundles or source directories.

## Expected Outputs

Prefer concrete artifacts over loose notes:

- Endpoint inventory with examples.
- Auth/session flow summary.
- Data model and response schema notes.
- Reproducible curl commands.
- Minimal typed client or request wrapper.
- Tests using recorded fixtures where possible.
- Risk notes covering authorization, secrets in captures, rate limits, and fragility.

## Script Outputs

The scripts are intentionally read-only and avoid printing secret values.

- `scripts/check-deps.sh`: reports required and optional local tools with `INSTALL_OPTIONAL:<tool>` lines for missing optional tools. It reports whether Playwright Python is available for `--browser` mode.
- `scripts/fingerprint-web.py <url>`: detects framework/platform/API/protection signals and recommends a targeted next command path before dumping or scanning deeply.
- `scripts/dump-website-js.py <url> --out <dir>`: saves the initial HTML, same-origin JavaScript bundles, available source maps, and a `manifest.json` for later analysis. Add `--browser` to execute the page with Playwright and capture runtime-loaded scripts. Use `--allow-cross-origin` only when cross-origin script collection is in scope.
- `scripts/capture-playwright-flow.py <url> --out <har>`: captures browser-loaded traffic to HAR when runtime interactions matter and Playwright is available.
- `scripts/har-summary.py <capture.har>`: prints hosts, methods/statuses, auth/header signals, likely API endpoints, GraphQL/WebSocket hints, and noisy third-party hosts.
- `scripts/scan-js-bundle.py <file-or-dir>`: scans JavaScript/TypeScript/HTML assets for URL/path literals, fetch/axios calls, GraphQL operations, WebSocket usage, auth header names, and common framework hints.
- `scripts/extract-endpoints.py <dump>`: writes structured endpoint inventory JSON/Markdown from dumped assets.
- `scripts/extract-sourcemaps.py <dump> --out <dir>`: extracts embedded original sources from `.map` files.
- `scripts/analyze-graphql.py <dump>`: consolidates GraphQL endpoints, operation names, subscriptions, and persisted-query signals from dumps and HAR JSON.
- `scripts/build-report.py`: creates a Markdown report from fingerprint, endpoint, HAR, and GraphQL artifacts.
- `scripts/generate-client-skeleton.py <endpoints.json>`: creates a conservative Python client skeleton from observed endpoints; review auth, CSRF, pagination, and request bodies before use.

## Practical Heuristics

- Start from browser Network traffic before reading minified JavaScript.
- Fingerprint first. Use the detected framework/API style to narrow the scan instead of treating every site the same.
- Treat headers and cookies as hypotheses: remove one at a time to find which are required.
- Separate browser constraints from server requirements. CORS affects browser clients, not server-side clients.
- Prefer stable API surfaces over copying internal frontend implementation details.
- Use Playwright when user interactions are hard to reproduce manually or require multi-step state.
- Use `dump-website-js.py` for unauthenticated/static first-pass collection; add `--browser` when scripts are injected only after browser execution. Use a HAR capture when login or manual user interaction is required.
- Use mitmproxy/Burp/HTTP Toolkit when a proxy capture is more useful than DevTools alone.
- Inspect JavaScript bundles only when traffic does not explain request construction, signatures, feature flags, or persisted GraphQL queries.

## Source Anchors

The bundled references are informed by official or primary documentation:

- Chrome DevTools Network panel and HAR export: https://developer.chrome.com/docs/devtools/network/reference
- Chrome DevTools Protocol Network domain: https://chromedevtools.github.io/devtools-protocol/tot/Network/
- HAR 1.2 format: https://www.softwareishard.com/blog/har-12-spec/
- Playwright network interception and HAR support: https://playwright.dev/docs/network
- mitmproxy interception and replay workflows: https://docs.mitmproxy.org/stable/
- curl usage and HTTP fundamentals: https://everything.curl.dev/
- MDN HTTP cookies and CORS behavior: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies
- GraphQL introspection concepts: https://graphql.org/learn/introspection/
- GraphQL over HTTP guidance: https://graphql.org/learn/serving-over-http/
- Source map specification: https://tc39.es/source-map/
- OWASP API Security Top 10: https://owasp.org/API-Security/editions/2023/en/0x00-header/
- OWASP Web Security Testing Guide: https://owasp.org/www-project-web-security-testing-guide/
