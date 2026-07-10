#!/usr/bin/env python3
"""Capture a browser flow with Playwright and save a HAR for later analysis."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="URL to open")
    parser.add_argument("--out", required=True, help="HAR output path")
    parser.add_argument("--wait-ms", type=int, default=3000, help="Extra wait after load")
    parser.add_argument("--headed", action="store_true", help="Run a visible browser for manual interaction")
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "Playwright Python package is required for browser capture.\n"
            "INSTALL_REQUIRED:playwright\n"
            "Install with: python3 -m pip install playwright && python3 -m playwright install chromium",
            file=sys.stderr,
        )
        return 2

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not args.headed)
        context = browser.new_context(record_har_path=str(out), record_har_content="embed")
        page = context.new_page()
        page.goto(args.url, wait_until="networkidle")
        if args.wait_ms:
            page.wait_for_timeout(args.wait_ms)
        context.close()
        browser.close()
    print(f"Wrote HAR: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
