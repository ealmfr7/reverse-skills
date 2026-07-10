import http.server
import importlib.util
import json
import socketserver
import subprocess
import threading
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "web-api-reverse-engineering" / "scripts" / "dump-website-js.py"


class FixtureHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        routes = {
            "/": (
                "text/html",
                b"""
                <html>
                  <head>
                    <script src="/static/app.js"></script>
                    <script type="module" src="https://cdn.invalid/skip.js"></script>
                  </head>
                  <body>
                    <script src="relative/chunk.js?ver=1"></script>
                    <script>window.inline = true;</script>
                  </body>
                </html>
                """,
            ),
            "/static/app.js": (
                "application/javascript",
                b'fetch("/api/v1/users");\n//# sourceMappingURL=app.js.map\n',
            ),
            "/static/app.js.map": (
                "application/json",
                b'{"version":3,"sources":["app.ts"],"mappings":""}',
            ),
            "/relative/chunk.js?ver=1": (
                "application/javascript",
                b'const socket = new WebSocket("wss://api.example.test/ws");',
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
    server = socketserver.TCPServer(("127.0.0.1", 0), FixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


class DumpWebsiteJsTests(unittest.TestCase):
    def test_dumps_same_origin_scripts_and_sourcemaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            server = serve_fixture()
            try:
                url = f"http://127.0.0.1:{server.server_address[1]}/"
                out = Path(tmp) / "dump"
                result = subprocess.run(
                    ["python3", str(SCRIPT), url, "--out", str(out)],
                    text=True,
                    capture_output=True,
                )
            finally:
                server.shutdown()
                server.server_close()

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((out / "index.html").exists())
            self.assertEqual(
                (out / "scripts" / "001-app.js").read_text(),
                'fetch("/api/v1/users");\n//# sourceMappingURL=app.js.map\n',
            )
            self.assertTrue((out / "scripts" / "001-app.js.map").exists())
            self.assertEqual(
                (out / "scripts" / "002-chunk.js").read_text(),
                'const socket = new WebSocket("wss://api.example.test/ws");',
            )

            manifest = json.loads((out / "manifest.json").read_text())
            self.assertEqual(manifest["url"], url)
            self.assertEqual(manifest["mode"], "static")
            self.assertEqual(len(manifest["scripts"]), 3)
            self.assertEqual(manifest["scripts"][0]["kind"], "external")
            self.assertIs(manifest["scripts"][0]["downloaded"], True)
            self.assertIs(manifest["scripts"][0]["sourcemap_downloaded"], True)
            self.assertIs(manifest["scripts"][1]["downloaded"], False)
            self.assertEqual(manifest["scripts"][1]["skip_reason"], "cross-origin")
            self.assertIs(manifest["scripts"][2]["downloaded"], True)

    def test_allow_cross_origin_downloads_cross_origin_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            server = serve_fixture()
            try:
                port = server.server_address[1]
                url = f"http://127.0.0.1:{port}/"
                out = Path(tmp) / "dump"
                result = subprocess.run(
                    [
                        "python3",
                        str(SCRIPT),
                        url,
                        "--out",
                        str(out),
                        "--allow-cross-origin",
                    ],
                    text=True,
                    capture_output=True,
                )
            finally:
                server.shutdown()
                server.server_close()

            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((out / "manifest.json").read_text())
            self.assertEqual(manifest["scripts"][1]["url"], "https://cdn.invalid/skip.js")
            self.assertIs(manifest["scripts"][1]["downloaded"], False)
            self.assertEqual(manifest["scripts"][1]["status"], "error")

    @unittest.skipIf(importlib.util.find_spec("playwright") is not None, "Playwright is installed")
    def test_browser_mode_reports_missing_playwright_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            server = serve_fixture()
            try:
                url = f"http://127.0.0.1:{server.server_address[1]}/"
                result = subprocess.run(
                    [
                        "python3",
                        str(SCRIPT),
                        url,
                        "--out",
                        str(Path(tmp) / "dump"),
                        "--browser",
                    ],
                    text=True,
                    capture_output=True,
                )
            finally:
                server.shutdown()
                server.server_close()

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("INSTALL_REQUIRED:playwright", result.stderr)


if __name__ == "__main__":
    unittest.main()
