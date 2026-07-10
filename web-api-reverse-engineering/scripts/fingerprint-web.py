#!/usr/bin/env python3
"""Fingerprint a web app to choose a targeted API reverse-engineering path."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_USER_AGENT = "Mozilla/5.0 (compatible; web-api-reverse-engineering/1.0)"


class ScriptParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts: list[dict] = []
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attr_map = {k.lower(): v or "" for k, v in attrs}
        if tag.lower() == "script":
            self.scripts.append(
                {
                    "src": attr_map.get("src"),
                    "type": attr_map.get("type"),
                    "id": attr_map.get("id"),
                }
            )
        elif tag.lower() == "meta":
            name = attr_map.get("name") or attr_map.get("property")
            if name:
                self.meta[name.lower()] = attr_map.get("content", "")


@dataclass
class FetchResult:
    url: str
    status_code: int
    headers: dict[str, str]
    body: bytes


def fetch(url: str, timeout: float, user_agent: str) -> FetchResult:
    request = Request(url, headers={"User-Agent": user_agent})
    try:
        with urlopen(request, timeout=timeout) as response:
            return FetchResult(
                url=response.geturl(),
                status_code=response.status,
                headers={k.lower(): v for k, v in response.headers.items()},
                body=response.read(),
            )
    except HTTPError as response:
        return FetchResult(
            url=response.geturl(),
            status_code=response.code,
            headers={k.lower(): v for k, v in response.headers.items()},
            body=response.read(),
        )


def decode_body(body: bytes, content_type: str) -> str:
    charset = "utf-8"
    match = re.search(r"charset=([^;\s]+)", content_type, re.I)
    if match:
        charset = match.group(1)
    return body.decode(charset, errors="replace")


def same_origin(a: str, b: str) -> bool:
    left = urlparse(a)
    right = urlparse(b)
    return (left.scheme, left.hostname, left.port) == (right.scheme, right.hostname, right.port)


def parse_html(html: str) -> ScriptParser:
    parser = ScriptParser()
    parser.feed(html)
    return parser


TECH_PATTERNS = {
    "Next.js": [r"__NEXT_DATA__", r"/_next/", r"next/router"],
    "Nuxt": [r"__NUXT__", r"/_nuxt/"],
    "React": [r"react(?:-dom)?", r"__REACT_DEVTOOLS_GLOBAL_HOOK__"],
    "Vue": [r"\bVue\b", r"createApp\(", r"__VUE__"],
    "Angular": [r"ng-version", r"@angular", r"zone\.js"],
    "Svelte/SvelteKit": [r"/_app/immutable/", r"\bsvelte\b"],
    "Remix": [r"__remixContext", r"@remix-run/", r"/build/_assets/"],
    "Astro": [r"astro-island", r"data-astro", r"/_astro/"],
    "Vite": [r"type=\"module\"", r"/assets/[^\"']+\.[A-Za-z0-9_-]+\.js", r"import\.meta\.env"],
    "Webpack": [r"webpackJsonp", r"__webpack_require__", r"webpackChunk"],
    "Apollo GraphQL": [r"ApolloClient", r"apollo-link", r"@apollo/client"],
    "Relay GraphQL": [r"RelayModern", r"relay-runtime"],
    "Axios": [r"\baxios\b"],
    "tRPC": [r"@trpc/client", r"\btrpc\b", r"/trpc/"],
    "gRPC-web": [r"grpc-web", r"application/grpc-web", r"X-Grpc-Web"],
    "Supabase": [r"@supabase/supabase-js", r"supabase\.co", r"createClient\([^)]*supabase"],
    "Firebase": [r"firebaseapp\.com", r"@firebase/", r"firebase/auth", r"firestore"],
    "Auth0": [r"auth0", r"@auth0/auth0-spa-js"],
    "Clerk": [r"clerk\.com", r"@clerk/", r"__clerk"],
    "Cognito": [r"amazon-cognito", r"cognito-idp", r"USER_SRP_AUTH"],
    "Stripe": [r"js\.stripe\.com", r"Stripe\(", r"@stripe/stripe-js"],
    "Shopify": [r"cdn\.shopify\.com", r"Shopify\.", r"myshopify\.com"],
    "WordPress": [r"wp-content", r"wp-json", r"wp-includes"],
    "Laravel": [r"laravel_session", r"XSRF-TOKEN"],
    "Rails": [r"csrf-token", r"_rails_session", r"rails-ujs"],
    "Django": [r"csrftoken", r"django"],
}

API_PATTERNS = {
    "GraphQL": [r"/graphql\b", r"\b(query|mutation|subscription)\s+[A-Za-z_]", r"__typename", r"persistedQuery"],
    "REST-like paths": [r"['\"`](/(?:api|v\d+|rest|auth|oauth|session|token|users?|account|profile|orders?|checkout|payment)[^'\"`]*)"],
    "RPC-style APIs": [r"/trpc/", r"grpc-web", r"application/grpc-web"],
    "WebSocket/SSE": [r"\bWebSocket\s*\(", r"\bEventSource\s*\(", r"wss?://"],
    "Auth/session": [r"authorization", r"x-csrf-token", r"x-xsrf-token", r"csrf", r"oidc", r"oauth", r"pkce"],
    "Request signing": [r"x-signature", r"x-timestamp", r"x-nonce", r"HmacSHA", r"crypto\.subtle"],
}

PROTECTION_PATTERNS = {
    "Cloudflare": [r"cf-ray", r"cloudflare", r"__cf_bm"],
    "DDoS-Guard": [r"ddos-guard", r"__ddg", r"check\.ddos-guard\.net"],
    "Akamai": [r"akamai", r"_abck", r"bm_sz"],
    "reCAPTCHA": [r"recaptcha", r"www\.google\.com/recaptcha"],
    "hCaptcha": [r"hcaptcha"],
}


def match_patterns(text: str, patterns: dict[str, list[str]]) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for name, regexes in patterns.items():
        evidence = []
        for regex in regexes:
            if re.search(regex, text, re.I):
                evidence.append(regex)
        if evidence:
            found[name] = evidence
    return found


def fetch_script_samples(page_url: str, scripts: list[dict], timeout: float, user_agent: str, limit: int) -> list[dict]:
    samples = []
    for script in scripts:
        src = script.get("src")
        if not src:
            continue
        script_url = urljoin(page_url, src)
        item = {"url": script_url, "same_origin": same_origin(page_url, script_url), "text": ""}
        if item["same_origin"] and len(samples) < limit:
            try:
                response = fetch(script_url, timeout, user_agent)
            except (HTTPError, URLError, TimeoutError, OSError) as exc:
                item["error"] = exc.__class__.__name__
            else:
                item["status_code"] = response.status_code
                item["content_type"] = response.headers.get("content-type", "")
                item["bytes"] = len(response.body)
                item["text"] = decode_body(response.body[:1_000_000], item["content_type"])
        samples.append(item)
    return samples


def choose_strategy(technologies: list[str], api_styles: list[str], scripts: list[dict]) -> str:
    if any(style in api_styles for style in ("Protection/friction",)):
        return "har-or-browser-capture"
    if any(tech in technologies for tech in ("Next.js", "Nuxt", "Angular", "Svelte/SvelteKit")):
        return "browser-dump"
    if any(style in api_styles for style in ("GraphQL", "WebSocket/SSE")):
        return "browser-dump"
    return "static-dump"


def recommended_commands(url: str, strategy: str, api_styles: list[str], technologies: list[str]) -> list[str]:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "-", urlparse(url).netloc).strip("-") or "site"
    out = f"dumps/{slug}"
    commands = ["bash scripts/check-deps.sh"]
    if strategy == "browser-dump":
        commands.append(f"python3 scripts/dump-website-js.py {url} --out {out} --browser")
    elif strategy == "static-dump":
        commands.append(f"python3 scripts/dump-website-js.py {url} --out {out}")
    else:
        commands.append("# Capture an authorized HAR in DevTools, then:")
        commands.append("python3 scripts/har-summary.py capture.har")
    if strategy in {"browser-dump", "static-dump"}:
        commands.append(f"python3 scripts/scan-js-bundle.py {out}")
    if "GraphQL" in api_styles:
        commands.append("# Focus follow-up: GraphQL operation names, persisted queries, variables, and /graphql traffic")
    if "Next.js" in technologies:
        commands.append("# Focus follow-up: __NEXT_DATA__, /_next/data/*.json, and API routes")
    return commands


def fingerprint(url: str, timeout: float, user_agent: str, script_limit: int) -> dict:
    page = fetch(url, timeout, user_agent)
    content_type = page.headers.get("content-type", "")
    html = decode_body(page.body, content_type)
    parser = parse_html(html)
    early_combined = "\n".join([html, "\n".join(f"{k}: {v}" for k, v in page.headers.items())])
    early_protection_evidence = match_patterns(early_combined, PROTECTION_PATTERNS)
    blocked_by_protection = page.status_code >= 400 and bool(early_protection_evidence)
    script_samples = [] if blocked_by_protection else fetch_script_samples(page.url, parser.scripts, timeout, user_agent, script_limit)

    combined = "\n".join(
        [
            html,
            "\n".join(f"{k}: {v}" for k, v in page.headers.items()),
            "\n".join(script.get("url", "") for script in script_samples),
            "\n".join(script.get("text", "") for script in script_samples),
        ]
    )

    tech_evidence = match_patterns(combined, TECH_PATTERNS)
    api_evidence = match_patterns(combined, API_PATTERNS)
    protection_evidence = early_protection_evidence or match_patterns(combined, PROTECTION_PATTERNS)
    technologies = sorted(tech_evidence)
    api_styles = sorted(api_evidence)
    protections = sorted(protection_evidence)

    host_counts = Counter(urlparse(script.get("url", "")).netloc for script in script_samples if script.get("url"))
    cross_origin_scripts = [script["url"] for script in script_samples if script.get("url") and not script.get("same_origin")]
    if protections and "Protection/friction" not in api_styles:
        api_styles.append("Protection/friction")
        api_styles = sorted(api_styles)
    strategy = choose_strategy(technologies, api_styles, parser.scripts)

    result = {
        "url": url,
        "final_url": page.url,
        "status_code": page.status_code,
        "content_type": content_type,
        "technologies": technologies,
        "technology_evidence": tech_evidence,
        "api_styles": api_styles,
        "api_evidence": api_evidence,
        "protections": protections,
        "protection_evidence": protection_evidence,
        "script_count": len([script for script in parser.scripts if script.get("src")]),
        "same_origin_script_samples": len([script for script in script_samples if script.get("same_origin") and script.get("text")]),
        "cross_origin_scripts": cross_origin_scripts,
        "script_hosts": dict(host_counts.most_common()),
        "recommended_strategy": strategy,
        "recommended_commands": recommended_commands(page.url, strategy, api_styles, technologies),
    }
    return result


def print_report(data: dict):
    print(f"=== Web Fingerprint: {data['final_url']} ===")
    print(f"Status: {data['status_code']}  Content-Type: {data['content_type'] or '?'}")
    print()
    print("Technologies:")
    if data["technologies"]:
        for tech in data["technologies"]:
            print(f"  - {tech}")
    else:
        print("  none detected")
    print()
    print("API styles:")
    if data["api_styles"]:
        for style in data["api_styles"]:
            print(f"  - {style}")
    else:
        print("  none detected")
    print()
    print("Protection / friction signals:")
    if data["protections"]:
        for protection in data["protections"]:
            print(f"  - {protection}")
    else:
        print("  none detected")
    print()
    print(f"Scripts: total={data['script_count']} sampled_same_origin={data['same_origin_script_samples']} cross_origin={len(data['cross_origin_scripts'])}")
    if data["cross_origin_scripts"]:
        print("Cross-origin scripts:")
        for script in data["cross_origin_scripts"][:10]:
            print(f"  - {script}")
    print()
    print(f"Recommended strategy: {data['recommended_strategy']}")
    print("Recommended commands:")
    for command in data["recommended_commands"]:
        print(f"  {command}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Page URL to fingerprint")
    parser.add_argument("--json-out", help="Write machine-readable fingerprint JSON")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--script-limit", type=int, default=8, help="Maximum same-origin scripts to fetch for signal detection")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    args = parser.parse_args()

    try:
        data = fingerprint(args.url, args.timeout, args.user_agent, args.script_limit)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print_report(data)
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
