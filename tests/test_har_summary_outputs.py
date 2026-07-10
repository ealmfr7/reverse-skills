import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "web-api-reverse-engineering" / "scripts" / "har-summary.py"


class HarSummaryOutputsTests(unittest.TestCase):
    def test_writes_structured_json_and_markdown_without_secret_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            har = Path(tmp) / "capture.har"
            har.write_text(
                json.dumps(
                    {
                        "log": {
                            "entries": [
                                {
                                    "request": {
                                        "method": "GET",
                                        "url": "https://api.example.com/api/v1/users?limit=10",
                                        "headers": [
                                            {"name": "Authorization", "value": "Bearer SECRET"},
                                            {"name": "Accept", "value": "application/json"},
                                        ],
                                    },
                                    "response": {
                                        "status": 200,
                                        "headers": [{"name": "Content-Type", "value": "application/json"}],
                                        "content": {"mimeType": "application/json", "text": "{}"},
                                    },
                                },
                                {
                                    "request": {
                                        "method": "POST",
                                        "url": "https://api.example.com/graphql",
                                        "headers": [{"name": "Content-Type", "value": "application/json"}],
                                        "postData": {
                                            "mimeType": "application/json",
                                            "text": json.dumps(
                                                {
                                                    "operationName": "CurrentUser",
                                                    "query": "query CurrentUser { viewer { id __typename } }",
                                                    "variables": {"secret": "SECRET"},
                                                }
                                            ),
                                        },
                                    },
                                    "response": {
                                        "status": 200,
                                        "headers": [{"name": "Content-Type", "value": "application/json"}],
                                        "content": {"mimeType": "application/json", "text": "{}"},
                                    },
                                },
                                {
                                    "request": {
                                        "method": "GET",
                                        "url": "https://api.example.com/graphql?query=query%20Viewer%20%7B%20viewer%20%7B%20id%20%7D%20%7D&operationName=Viewer",
                                        "headers": [{"name": "Accept", "value": "application/graphql-response+json"}],
                                    },
                                    "response": {
                                        "status": 200,
                                        "headers": [{"name": "Content-Type", "value": "application/graphql-response+json"}],
                                        "content": {"mimeType": "application/graphql-response+json", "text": "{}"},
                                    },
                                },
                                {
                                    "request": {
                                        "method": "GET",
                                        "url": "wss://api.example.com/live",
                                        "headers": [],
                                    },
                                    "response": {
                                        "status": 101,
                                        "headers": [],
                                        "content": {"mimeType": ""},
                                    },
                                    "_webSocketMessages": [
                                        {"type": "send", "data": "{\"type\":\"subscribe\",\"topic\":\"prices\"}"},
                                        {"type": "receive", "data": "{\"type\":\"event\",\"topic\":\"prices\"}"},
                                    ],
                                },
                            ]
                        }
                    }
                ),
                encoding="utf-8",
            )
            out = Path(tmp) / "har.json"
            md = Path(tmp) / "har.md"
            result = subprocess.run(
                ["python3", str(SCRIPT), str(har), "--json-out", str(out), "--markdown-out", str(md)],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(out.read_text())
            endpoint_keys = {(item["method"], item["host"], item["path"]) for item in data["endpoints"]}
            self.assertIn(("GET", "api.example.com", "/api/v1/users"), endpoint_keys)
            self.assertIn(("POST", "api.example.com", "/graphql"), endpoint_keys)
            self.assertIn(("GET", "api.example.com", "/graphql"), endpoint_keys)
            self.assertEqual(data["graphql_operations"][0]["name"], "CurrentUser")
            self.assertTrue(any(op["name"] == "Viewer" for op in data["graphql_operations"]))
            self.assertEqual(data["websockets"][0]["message_count"], 2)
            serialized = out.read_text() + md.read_text() + result.stdout
            self.assertNotIn("SECRET", serialized)
            self.assertIn("HAR Endpoint Inventory", md.read_text())


if __name__ == "__main__":
    unittest.main()
