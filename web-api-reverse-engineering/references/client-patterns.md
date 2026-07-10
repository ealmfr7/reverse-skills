# Client Construction Patterns

Build the smallest maintainable client that reproduces observed, authorized workflows.

## Client Shape

Use this structure unless the target codebase already has a stronger convention:

- `Config`: base URL, tenant/org, timeouts, user agent, environment.
- `AuthProvider`: login, token/session storage, refresh, logout.
- `Transport`: request wrapper, retries, headers, cookies, JSON handling.
- `Resources`: endpoint-specific methods.
- `Models`: typed request/response shapes when the language supports them.
- `Tests`: fixture-based tests and at least one live smoke test when safe.

## Request Wrapper Responsibilities

Centralize:

- Base URL joining.
- Default headers.
- Cookie jar or bearer token injection.
- CSRF token injection.
- JSON serialization/deserialization.
- Timeout and retry policy.
- Error normalization.
- Rate-limit handling.
- Request/response logging with secret redaction.

Keep endpoint methods boring. They should mostly pass typed parameters to the wrapper.

## Python Sketch

```python
from dataclasses import dataclass
import httpx

@dataclass
class ApiConfig:
    base_url: str
    timeout: float = 20.0

class ApiClient:
    def __init__(self, config: ApiConfig, token: str | None = None):
        self.config = config
        self.client = httpx.Client(
            base_url=config.base_url,
            timeout=config.timeout,
            headers={"Accept": "application/json"},
        )
        if token:
            self.client.headers["Authorization"] = f"Bearer {token}"

    def request(self, method: str, path: str, **kwargs):
        response = self.client.request(method, path, **kwargs)
        if response.status_code >= 400:
            raise ApiError(response.status_code, response.text)
        return response.json() if response.content else None

class ApiError(RuntimeError):
    def __init__(self, status_code: int, body: str):
        super().__init__(f"API request failed: {status_code}")
        self.status_code = status_code
        self.body = body
```

Use `httpx.Client` or `requests.Session` for cookie/session reuse. Prefer `httpx` when async support may be needed.

## Node.js Sketch

```ts
type ApiConfig = {
  baseUrl: string;
  token?: string;
};

export class ApiClient {
  constructor(private config: ApiConfig) {}

  async request<T>(method: string, path: string, body?: unknown): Promise<T> {
    const res = await fetch(new URL(path, this.config.baseUrl), {
      method,
      headers: {
        Accept: "application/json",
        ...(body ? { "Content-Type": "application/json" } : {}),
        ...(this.config.token ? { Authorization: `Bearer ${this.config.token}` } : {}),
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!res.ok) {
      throw new ApiError(res.status, await res.text());
    }

    return (await res.json()) as T;
  }
}

export class ApiError extends Error {
  constructor(readonly status: number, readonly body: string) {
    super(`API request failed: ${status}`);
  }
}
```

Use `undici`/native `fetch` for simple clients. Use a cookie jar library when the target API requires browser-like cookie behavior.

## Auth Patterns

Bearer token:

- Store token outside source control.
- Refresh before expiry when refresh flow is known.
- Retry once after refresh on `401`, then fail.

Cookie session:

- Preserve a cookie jar.
- Capture CSRF token source.
- Keep login separate from normal endpoint methods.

CSRF:

- Identify token source: cookie, meta tag, bootstrap JSON, or preflight endpoint.
- Send token only to the intended origin.
- Refresh it when the server rotates it.

Request signing:

- Do not guess. Locate exact input fields, canonicalization order, timestamp/nonce rules, encoding, and hash/HMAC algorithm.
- Prefer using a documented SDK if available.
- Mark the implementation brittle when derived from frontend internals.

## Pagination and Lists

Document:

- Page number, cursor, offset, or token style.
- Default and maximum page size.
- Sort field names.
- Empty page behavior.
- Consistency guarantees if records change while paging.

Expose iteration helpers after the raw list endpoint is proven.

## Error Handling

Normalize:

- HTTP status.
- API error code.
- Human message.
- Validation field errors.
- Retry-after/rate-limit metadata.
- Request ID or trace ID.

Do not hide response bodies during development. Redact secrets in logs.

## Tests

Use layers:

- Unit tests for request construction.
- Fixture tests from sanitized HAR/JSON responses.
- Contract smoke tests against a safe test account when authorized.
- Negative tests for expired auth, invalid input, and pagination end.

Avoid tests that mutate production data unless the user explicitly authorizes a safe test environment.

## Documentation Template

For each endpoint:

```md
### `GET /api/example`

Purpose: observed when opening the Example page.

Auth: bearer token and `x-csrf-token`.

Query:
- `limit`: number, default 25.
- `cursor`: opaque pagination token.

Response:
- `items[]`
- `nextCursor`

Notes:
- Observed in HAR `example-page.har`.
- `Origin` was not required outside browser in curl reproduction.
- Rate limit behavior unverified.
```
