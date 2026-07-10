#!/usr/bin/env python3
"""Generate a conservative API client skeleton from endpoint inventory JSON."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


def method_name(method: str, path: str) -> str:
    clean = re.sub(r"\{[^}]+\}", "by_id", path.strip("/"))
    clean = re.sub(r"[^A-Za-z0-9]+", "_", clean).strip("_")
    if not clean:
        clean = "root"
    return f"{method.lower()}_{clean}".lower()


def load_endpoints(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("endpoints", [])


def infer_base_url(endpoints: list[dict]) -> str:
    for endpoint in endpoints:
        url = endpoint.get("url")
        if url:
            parsed = urlparse(url)
            if parsed.scheme and parsed.netloc:
                return f"{parsed.scheme}://{parsed.netloc}"
        host = endpoint.get("host")
        if host:
            return f"https://{host}"
    return "https://api.example.com"


def endpoint_path(endpoint: dict) -> str:
    if endpoint.get("path"):
        return endpoint["path"]
    url = endpoint.get("url", "")
    parsed = urlparse(url)
    return parsed.path or "/"


def generate_python(endpoints: list[dict], out: Path):
    out.mkdir(parents=True, exist_ok=True)
    base_url = infer_base_url(endpoints)
    methods = []
    seen = set()
    for endpoint in endpoints:
        method = endpoint.get("method", "GET").upper()
        if method == "WS":
            continue
        path = endpoint_path(endpoint)
        name = method_name(method, path)
        if name in seen:
            continue
        seen.add(name)
        body_arg = ", json: dict | None = None" if method in {"POST", "PUT", "PATCH"} else ""
        call_kwargs = ", json=json" if method in {"POST", "PUT", "PATCH"} else ""
        methods.append(
            f'''
    def {name}(self{body_arg}, **params):
        """Observed {method} {path}."""
        return self.request("{method}", "{path}", params=params{call_kwargs})
'''
        )

    client = f'''"""Generated client skeleton.

Review authentication, CSRF, pagination, retries, and error semantics before use.
"""

from __future__ import annotations

import httpx


class ApiError(RuntimeError):
    def __init__(self, status_code: int, body: str):
        super().__init__(f"API request failed: {{status_code}}")
        self.status_code = status_code
        self.body = body


class ApiClient:
    def __init__(self, base_url: str = "{base_url}", token: str | None = None, timeout: float = 20.0):
        self.client = httpx.Client(base_url=base_url, timeout=timeout, headers={{"Accept": "application/json"}})
        if token:
            self.client.headers["Authorization"] = f"Bearer {{token}}"

    def request(self, method: str, path: str, **kwargs):
        response = self.client.request(method, path, **kwargs)
        if response.status_code >= 400:
            raise ApiError(response.status_code, response.text)
        if not response.content:
            return None
        content_type = response.headers.get("content-type", "")
        return response.json() if "json" in content_type else response.text
{''.join(methods)}
'''
    (out / "client.py").write_text(client, encoding="utf-8")
    (out / "README.md").write_text(
        "# Generated API Client Skeleton\n\n"
        "This is a starting point from observed endpoints. Validate auth, CSRF, pagination, "
        "rate limits, request bodies, and error handling before using it against any real environment.\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("endpoints_json", help="JSON from extract-endpoints.py or har-summary.py")
    parser.add_argument("--lang", choices=["python"], default="python")
    parser.add_argument("--out", required=True, help="Output directory")
    args = parser.parse_args()
    try:
        endpoints = load_endpoints(Path(args.endpoints_json))
        generate_python(endpoints, Path(args.out))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {args.lang} client skeleton: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
