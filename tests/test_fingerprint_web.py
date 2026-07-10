import http.server
import json
import socketserver
import subprocess
import threading
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "web-api-reverse-engineering" / "scripts" / "fingerprint-web.py"


class FingerprintHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/blocked":
            body = b"""<!doctype html><title>DDoS-Guard</title><script src="/.well-known/ddos-guard/js-challenge/index.js"></script>"""
            self.send_response(403)
            self.send_header("server", "ddos-guard")
            self.send_header("content-type", "text/html")
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/.well-known/ddos-guard/js-challenge/index.js":
            body = b"webpackChunk=[]; const React = {}; WebSocket;"
            self.send_response(200)
            self.send_header("content-type", "application/javascript")
            self.end_headers()
            self.wfile.write(body)
            return
        routes = {
            "/next": (
                "text/html",
                b"""
                <html>
                  <head>
                    <script id="__NEXT_DATA__" type="application/json">{"props":{}}</script>
                    <script src="/_next/static/chunks/main.js"></script>
                  </head>
                </html>
                """,
            ),
            "/_next/static/chunks/main.js": (
                "application/javascript",
                b"""
                import { ApolloClient } from '@apollo/client';
                fetch('/api/v1/users');
                const q = `query CurrentUser { viewer { id __typename } }`;
                new WebSocket('wss://api.example.test/live');
                """,
            ),
            "/static": (
                "text/html",
                b"""
                <html>
                  <head><link rel="stylesheet" href="/style.css"></head>
                  <body><h1>Docs</h1></body>
                </html>
                """,
            ),
            "/modern": (
                "text/html",
                b"""
                <html>
                  <head>
                    <script src="/assets/modern.js" type="module"></script>
                    <script src="https://js.stripe.com/v3/"></script>
                  </head>
                </html>
                """,
            ),
            "/assets/modern.js": (
                "application/javascript",
                b"""
                import { createClient } from '@supabase/supabase-js';
                import { createTRPCClient } from '@trpc/client';
                const auth = '@auth0/auth0-spa-js';
                window.__remixContext = {};
                fetch('/trpc/user.byId');
                """,
            ),
        }
        if self.path not in routes:
            self.send_response(404)
            self.end_headers()
            return
        content_type, body = routes[self.path]
        self.send_response(200)
        self.send_header("content-type", content_type)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def serve_fixture():
    server = socketserver.TCPServer(("127.0.0.1", 0), FingerprintHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


class FingerprintWebTests(unittest.TestCase):
    def test_fingerprints_next_graphql_and_recommends_browser_dump(self):
        with tempfile.TemporaryDirectory() as tmp:
            server = serve_fixture()
            try:
                url = f"http://127.0.0.1:{server.server_address[1]}/next"
                out = Path(tmp) / "fingerprint.json"
                result = subprocess.run(
                    ["python3", str(SCRIPT), url, "--json-out", str(out)],
                    text=True,
                    capture_output=True,
                )
            finally:
                server.shutdown()
                server.server_close()

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(out.read_text())
            self.assertIn("Next.js", data["technologies"])
            self.assertIn("GraphQL", data["api_styles"])
            self.assertIn("WebSocket/SSE", data["api_styles"])
            self.assertIn("REST-like paths", data["api_styles"])
            self.assertEqual(data["recommended_strategy"], "browser-dump")
            self.assertTrue(any("--browser" in command for command in data["recommended_commands"]))
            self.assertIn("GraphQL", result.stdout)

    def test_fingerprints_static_site_and_recommends_static_dump(self):
        with tempfile.TemporaryDirectory() as tmp:
            server = serve_fixture()
            try:
                url = f"http://127.0.0.1:{server.server_address[1]}/static"
                out = Path(tmp) / "fingerprint.json"
                result = subprocess.run(
                    ["python3", str(SCRIPT), url, "--json-out", str(out)],
                    text=True,
                    capture_output=True,
                )
            finally:
                server.shutdown()
                server.server_close()

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(out.read_text())
            self.assertEqual(data["technologies"], [])
            self.assertEqual(data["api_styles"], [])
            self.assertEqual(data["recommended_strategy"], "static-dump")
            self.assertTrue(any("dump-website-js.py" in command for command in data["recommended_commands"]))

    def test_fingerprints_modern_api_platforms(self):
        with tempfile.TemporaryDirectory() as tmp:
            server = serve_fixture()
            try:
                url = f"http://127.0.0.1:{server.server_address[1]}/modern"
                out = Path(tmp) / "fingerprint.json"
                result = subprocess.run(
                    ["python3", str(SCRIPT), url, "--json-out", str(out)],
                    text=True,
                    capture_output=True,
                )
            finally:
                server.shutdown()
                server.server_close()

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(out.read_text())
            for tech in ["Remix", "tRPC", "Supabase", "Auth0", "Stripe"]:
                self.assertIn(tech, data["technologies"])
            self.assertIn("RPC-style APIs", data["api_styles"])

    def test_fingerprints_http_error_pages_for_protection_signals(self):
        with tempfile.TemporaryDirectory() as tmp:
            server = serve_fixture()
            try:
                url = f"http://127.0.0.1:{server.server_address[1]}/blocked"
                out = Path(tmp) / "fingerprint.json"
                result = subprocess.run(
                    ["python3", str(SCRIPT), url, "--json-out", str(out)],
                    text=True,
                    capture_output=True,
                )
            finally:
                server.shutdown()
                server.server_close()

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(out.read_text())
            self.assertEqual(data["status_code"], 403)
            self.assertIn("DDoS-Guard", data["protections"])
            self.assertEqual(data["recommended_strategy"], "har-or-browser-capture")
            self.assertNotIn("React", data["technologies"])
            self.assertFalse(any("scan-js-bundle.py dumps" in command for command in data["recommended_commands"]))


if __name__ == "__main__":
    unittest.main()
