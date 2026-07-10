import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "web-api-reverse-engineering" / "scripts" / "build-report.py"


class BuildReportTests(unittest.TestCase):
    def test_builds_markdown_report_from_analysis_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fingerprint = tmp_path / "fingerprint.json"
            endpoints = tmp_path / "endpoints.json"
            graphql = tmp_path / "graphql.json"
            out = tmp_path / "report.md"

            fingerprint.write_text(
                json.dumps(
                    {
                        "final_url": "https://app.example.com",
                        "technologies": ["Next.js"],
                        "api_styles": ["GraphQL", "REST-like paths"],
                        "protections": [],
                        "recommended_strategy": "browser-dump",
                        "recommended_commands": ["python3 scripts/dump-website-js.py https://app.example.com --out dumps/app --browser"],
                    }
                ),
                encoding="utf-8",
            )
            endpoints.write_text(
                json.dumps(
                    {
                        "endpoints": [
                            {"method": "GET", "host": "api.example.com", "path": "/api/v1/users", "sources": ["app.js"]},
                            {"method": "POST", "host": "api.example.com", "path": "/graphql", "sources": ["app.js"]},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            graphql.write_text(
                json.dumps({"operations": [{"kind": "query", "name": "CurrentUser", "sources": ["app.js"]}]}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--fingerprint",
                    str(fingerprint),
                    "--endpoints",
                    str(endpoints),
                    "--graphql",
                    str(graphql),
                    "--out",
                    str(out),
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = out.read_text()
            self.assertIn("# Web API Reverse Engineering Report", report)
            self.assertIn("Next.js", report)
            self.assertIn("/api/v1/users", report)
            self.assertIn("query CurrentUser", report)
            self.assertIn("browser-dump", report)


if __name__ == "__main__":
    unittest.main()
