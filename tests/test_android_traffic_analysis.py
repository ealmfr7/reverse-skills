import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "android-traffic-analysis" / "scripts" / "summarize-traffic.py"


class AndroidTrafficAnalysisTests(unittest.TestCase):
    def test_summarizes_har_without_secret_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            har = Path(tmp) / "capture.har"
            out = Path(tmp) / "summary.json"
            har.write_text(
                json.dumps(
                    {
                        "log": {
                            "entries": [
                                {
                                    "request": {
                                        "method": "GET",
                                        "url": "https://api.example.com/v1/users?token=SECRET",
                                        "headers": [{"name": "Authorization", "value": "Bearer SECRET"}],
                                    },
                                    "response": {"status": 200, "headers": []},
                                },
                                {
                                    "request": {
                                        "method": "POST",
                                        "url": "https://api.example.com/graphql",
                                        "headers": [{"name": "Content-Type", "value": "application/json"}],
                                        "postData": {
                                            "text": json.dumps(
                                                {
                                                    "operationName": "CurrentUser",
                                                    "query": "query CurrentUser { viewer { id } }",
                                                    "variables": {"password": "SECRET"},
                                                }
                                            )
                                        },
                                    },
                                    "response": {"status": 200, "headers": []},
                                },
                                {
                                    "request": {
                                        "method": "GET",
                                        "url": "wss://api.example.com/live",
                                        "headers": [],
                                    },
                                    "response": {"status": 101, "headers": []},
                                },
                            ]
                        }
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                ["python3", str(SCRIPT), str(har), "--json-out", str(out)],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(out.read_text(encoding="utf-8"))
            endpoint_keys = {(e["method"], e["host"], e["path"]) for e in data["endpoints"]}
            self.assertIn(("GET", "api.example.com", "/v1/users"), endpoint_keys)
            self.assertIn(("POST", "api.example.com", "/graphql"), endpoint_keys)
            self.assertEqual(data["graphql_operations"][0]["name"], "CurrentUser")
            self.assertEqual(data["websockets"][0]["host"], "api.example.com")
            serialized = json.dumps(data) + result.stdout + result.stderr
            self.assertNotIn("SECRET", serialized)


if __name__ == "__main__":
    unittest.main()
