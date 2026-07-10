#!/usr/bin/env python3
"""Dump JavaScript assets from a web page for later API analysis."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_USER_AGENT = "Mozilla/5.0 (compatible; web-api-reverse-engineering/1.0)"
SOURCEMAP_RE = re.compile(r"sourceMappingURL=([^\s*]+)")


class ScriptParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag.lower() != "script":
            return
        attr_map = {k.lower(): v for k, v in attrs}
        src = attr_map.get("src")
        self.scripts.append(
            {
                "kind": "external" if src else "inline",
                "src": src,
                "type": attr_map.get("type"),
            }
        )


@dataclass
class FetchResult:
    url: str
    status_code: int
    content_type: str
    body: bytes


class DependencyError(RuntimeError):
    pass


def fetch(url: str, timeout: float, user_agent: str) -> FetchResult:
    request = Request(url, headers={"User-Agent": user_agent})
    with urlopen(request, timeout=timeout) as response:
        body = response.read()
        return FetchResult(
            url=response.geturl(),
            status_code=response.status,
            content_type=response.headers.get("content-type", ""),
            body=body,
        )


def same_origin(a: str, b: str) -> bool:
    left = urlparse(a)
    right = urlparse(b)
    return (left.scheme, left.hostname, left.port) == (right.scheme, right.hostname, right.port)


def safe_script_name(index: int, url: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name or "script.js"
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-") or "script.js"
    if not name.endswith((".js", ".mjs", ".cjs")):
        name += ".js"
    return f"{index:03d}-{name}"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def text_from_bytes(data: bytes, content_type: str) -> str:
    charset = "utf-8"
    match = re.search(r"charset=([^;\s]+)", content_type, re.I)
    if match:
        charset = match.group(1)
    return data.decode(charset, errors="replace")


def extract_scripts(html: str) -> list[dict]:
    parser = ScriptParser()
    parser.feed(html)
    return [script for script in parser.scripts if script["kind"] == "external"]


def discover_sourcemap_url(script_url: str, script_text: str) -> str | None:
    matches = SOURCEMAP_RE.findall(script_text)
    if not matches:
        candidate = script_url.split("?", 1)[0] + ".map"
        return candidate
    value = matches[-1].strip().strip("\"'")
    if value.startswith("data:"):
        return None
    return urljoin(script_url, value)


def write_bytes(path: Path, body: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)


def base_manifest(url: str, final_url: str, mode: str, html_body: bytes, content_type: str, status_code: int) -> dict:
    return {
        "url": url,
        "final_url": final_url,
        "mode": mode,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "html": {
            "file": "index.html",
            "status_code": status_code,
            "content_type": content_type,
            "sha256": sha256(html_body),
            "bytes": len(html_body),
        },
        "scripts": [],
    }


def dump_static(
    url: str,
    out_dir: Path,
    allow_cross_origin: bool,
    timeout: float,
    user_agent: str,
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    scripts_dir = out_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)

    page = fetch(url, timeout, user_agent)
    html = text_from_bytes(page.body, page.content_type)
    write_bytes(out_dir / "index.html", page.body)

    manifest = base_manifest(url, page.url, "static", page.body, page.content_type, page.status_code)

    download_index = 0
    for script in extract_scripts(html):
        script_url = urljoin(page.url, script["src"])
        item = {
            "kind": "external",
            "src": script["src"],
            "url": script_url,
            "type": script.get("type"),
            "downloaded": False,
        }

        if not allow_cross_origin and not same_origin(page.url, script_url):
            item["skip_reason"] = "cross-origin"
            manifest["scripts"].append(item)
            continue

        download_index += 1
        filename = safe_script_name(download_index, script_url)
        try:
            result = fetch(script_url, timeout, user_agent)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            item["status"] = "error"
            item["error"] = exc.__class__.__name__
            manifest["scripts"].append(item)
            continue

        rel = Path("scripts") / filename
        write_bytes(out_dir / rel, result.body)
        script_text = text_from_bytes(result.body, result.content_type)
        item.update(
            {
                "downloaded": True,
                "status_code": result.status_code,
                "content_type": result.content_type,
                "file": rel.as_posix(),
                "sha256": sha256(result.body),
                "bytes": len(result.body),
            }
        )

        sourcemap_url = discover_sourcemap_url(result.url, script_text)
        if sourcemap_url:
            item["sourcemap_url"] = sourcemap_url
            try:
                sourcemap = fetch(sourcemap_url, timeout, user_agent)
            except (HTTPError, URLError, TimeoutError, OSError):
                item["sourcemap_downloaded"] = False
            else:
                map_rel = Path("scripts") / f"{filename}.map"
                write_bytes(out_dir / map_rel, sourcemap.body)
                item["sourcemap_downloaded"] = True
                item["sourcemap_file"] = map_rel.as_posix()
                item["sourcemap_sha256"] = sha256(sourcemap.body)
                item["sourcemap_bytes"] = len(sourcemap.body)

        manifest["scripts"].append(item)

    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def looks_like_script(url: str, content_type: str) -> bool:
    lower_type = content_type.lower()
    if "javascript" in lower_type or "ecmascript" in lower_type:
        return True
    path = urlparse(url).path.lower()
    return path.endswith((".js", ".mjs", ".cjs"))


def dump_browser(
    url: str,
    out_dir: Path,
    allow_cross_origin: bool,
    timeout: float,
    user_agent: str,
    wait_ms: int,
) -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise DependencyError(
            "Playwright Python package is required for --browser mode.\n"
            "INSTALL_REQUIRED:playwright\n"
            "Install with: python3 -m pip install playwright && python3 -m playwright install chromium"
        ) from exc

    out_dir.mkdir(parents=True, exist_ok=True)
    scripts_dir = out_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)

    response_records = []
    with sync_playwright() as playwright:
        browser = launch_chromium(playwright)
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()
        page.on("response", lambda response: response_records.append(response))
        page.goto(url, wait_until="networkidle", timeout=int(timeout * 1000))
        if wait_ms > 0:
            page.wait_for_timeout(wait_ms)

        html = page.content().encode("utf-8")
        final_url = page.url
        script_urls = page.eval_on_selector_all(
            "script[src]",
            "els => els.map(el => new URL(el.getAttribute('src'), document.baseURI).href)",
        )
        write_bytes(out_dir / "index.html", html)
        manifest = base_manifest(url, final_url, "browser", html, "text/html; charset=utf-8", 200)

        responses_by_url = {}
        for response in response_records:
            content_type = response.headers.get("content-type", "")
            if looks_like_script(response.url, content_type):
                responses_by_url[response.url] = response

        ordered_urls = []
        for script_url in script_urls:
            if script_url not in ordered_urls:
                ordered_urls.append(script_url)
        for script_url in responses_by_url:
            if script_url not in ordered_urls:
                ordered_urls.append(script_url)

        download_index = 0
        for script_url in ordered_urls:
            item = {
                "kind": "external",
                "src": script_url,
                "url": script_url,
                "downloaded": False,
            }

            if not allow_cross_origin and not same_origin(final_url, script_url):
                item["skip_reason"] = "cross-origin"
                manifest["scripts"].append(item)
                continue

            response = responses_by_url.get(script_url)
            try:
                if response is not None:
                    body = response.body()
                    content_type = response.headers.get("content-type", "")
                    status_code = response.status
                else:
                    api_response = context.request.get(script_url, timeout=int(timeout * 1000))
                    body = api_response.body()
                    content_type = api_response.headers.get("content-type", "")
                    status_code = api_response.status
            except Exception as exc:
                item["status"] = "error"
                item["error"] = exc.__class__.__name__
                manifest["scripts"].append(item)
                continue

            download_index += 1
            filename = safe_script_name(download_index, script_url)
            rel = Path("scripts") / filename
            write_bytes(out_dir / rel, body)
            script_text = text_from_bytes(body, content_type)
            item.update(
                {
                    "downloaded": True,
                    "status_code": status_code,
                    "content_type": content_type,
                    "file": rel.as_posix(),
                    "sha256": sha256(body),
                    "bytes": len(body),
                }
            )

            sourcemap_url = discover_sourcemap_url(script_url, script_text)
            if sourcemap_url:
                item["sourcemap_url"] = sourcemap_url
                try:
                    map_response = context.request.get(sourcemap_url, timeout=int(timeout * 1000))
                    if map_response.ok:
                        sourcemap_body = map_response.body()
                    else:
                        sourcemap_body = None
                except Exception:
                    sourcemap_body = None
                if sourcemap_body is None:
                    item["sourcemap_downloaded"] = False
                else:
                    map_rel = Path("scripts") / f"{filename}.map"
                    write_bytes(out_dir / map_rel, sourcemap_body)
                    item["sourcemap_downloaded"] = True
                    item["sourcemap_file"] = map_rel.as_posix()
                    item["sourcemap_sha256"] = sha256(sourcemap_body)
                    item["sourcemap_bytes"] = len(sourcemap_body)

            manifest["scripts"].append(item)

        browser.close()

    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def launch_chromium(playwright):
    try:
        return playwright.chromium.launch(headless=True)
    except Exception as first_error:
        for channel in ("chrome", "chromium", "msedge"):
            try:
                return playwright.chromium.launch(headless=True, channel=channel)
            except Exception:
                continue
        raise first_error


def print_summary(manifest: dict):
    downloaded = sum(1 for script in manifest["scripts"] if script.get("downloaded"))
    skipped = sum(1 for script in manifest["scripts"] if script.get("skip_reason"))
    errors = sum(1 for script in manifest["scripts"] if script.get("status") == "error")
    maps = sum(1 for script in manifest["scripts"] if script.get("sourcemap_downloaded"))
    print(f"Dumped page: {manifest['final_url']}")
    print(f"Scripts: total={len(manifest['scripts'])} downloaded={downloaded} skipped={skipped} errors={errors} sourcemaps={maps}")
    print("Output: manifest.json, index.html, scripts/")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Page URL to fetch")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Execute the page with Playwright and dump scripts loaded after browser runtime execution",
    )
    parser.add_argument(
        "--allow-cross-origin",
        action="store_true",
        help="Download cross-origin script URLs instead of listing them as skipped",
    )
    parser.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout in seconds")
    parser.add_argument("--wait-ms", type=int, default=1000, help="Extra browser wait after network idle in --browser mode")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT, help="User-Agent header")
    args = parser.parse_args(argv)

    try:
        if args.browser:
            manifest = dump_browser(
                args.url,
                Path(args.out),
                allow_cross_origin=args.allow_cross_origin,
                timeout=args.timeout,
                user_agent=args.user_agent,
                wait_ms=args.wait_ms,
            )
        else:
            manifest = dump_static(
                args.url,
                Path(args.out),
                allow_cross_origin=args.allow_cross_origin,
                timeout=args.timeout,
                user_agent=args.user_agent,
            )
    except DependencyError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print_summary(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
