import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "web-api-reverse-engineering" / "scripts" / "extract-endpoints.py"


class ExtractEndpointsTests(unittest.TestCase):
    def test_extracts_deduplicated_endpoints_and_graphql(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "dump"
            root.mkdir()
            (root / "index.html").write_text(
                '<script>fetch("/api/v1/bootstrap")</script>',
                encoding="utf-8",
            )
            (root / "app.js").write_text(
                """
                const base = "https://api.example.com";
                fetch("/api/v1/users?limit=10", { headers: { "Authorization": token }});
                axios.post('/auth/login', body);
                const q = `query CurrentUser { viewer { id __typename } }`;
                fetch("https://api.example.com/graphql", { method: "POST", body: JSON.stringify({query: q}) });
                new WebSocket("wss://api.example.com/live");
                """,
                encoding="utf-8",
            )
            out = Path(tmp) / "endpoints.json"
            md = Path(tmp) / "endpoints.md"

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    str(root),
                    "--base-url",
                    "https://app.example.com",
                    "--json-out",
                    str(out),
                    "--markdown-out",
                    str(md),
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(out.read_text())
            keys = {(item["method"], item["url"]) for item in data["endpoints"]}
            self.assertIn(("GET", "https://app.example.com/api/v1/bootstrap"), keys)
            self.assertIn(("GET", "https://app.example.com/api/v1/users?limit=10"), keys)
            self.assertIn(("POST", "https://app.example.com/auth/login"), keys)
            self.assertIn(("POST", "https://api.example.com/graphql"), keys)
            self.assertIn(("WS", "wss://api.example.com/live"), keys)
            self.assertEqual(data["graphql_operations"][0]["name"], "CurrentUser")
            self.assertIn("Endpoint Inventory", md.read_text())


if __name__ == "__main__":
    unittest.main()
