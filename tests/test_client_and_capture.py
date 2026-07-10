import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "web-api-reverse-engineering" / "scripts" / "generate-client-skeleton.py"
CAPTURE = ROOT / "web-api-reverse-engineering" / "scripts" / "capture-playwright-flow.py"


class ClientAndCaptureTests(unittest.TestCase):
    def test_generates_python_client_skeleton_from_endpoints(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            endpoints = tmp_path / "endpoints.json"
            out = tmp_path / "client"
            endpoints.write_text(
                json.dumps(
                    {
                        "endpoints": [
                            {"method": "GET", "url": "https://api.example.com/api/v1/users", "path": "/api/v1/users"},
                            {"method": "POST", "url": "https://api.example.com/auth/login", "path": "/auth/login"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                ["python3", str(CLIENT), str(endpoints), "--lang", "python", "--out", str(out)],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            client_py = (out / "client.py").read_text()
            self.assertIn("class ApiClient", client_py)
            self.assertIn("def get_api_v1_users", client_py)
            self.assertIn("def post_auth_login", client_py)
            self.assertTrue((out / "README.md").exists())

    @unittest.skipIf(importlib.util.find_spec("playwright") is not None, "Playwright is installed")
    def test_capture_playwright_flow_reports_missing_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["python3", str(CAPTURE), "https://example.com", "--out", str(Path(tmp) / "flow.har")],
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("INSTALL_REQUIRED:playwright", result.stderr)


if __name__ == "__main__":
    unittest.main()
