import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCEMAPS = ROOT / "web-api-reverse-engineering" / "scripts" / "extract-sourcemaps.py"
GRAPHQL = ROOT / "web-api-reverse-engineering" / "scripts" / "analyze-graphql.py"


class SourcemapsAndGraphqlTests(unittest.TestCase):
    def test_extracts_embedded_sources_from_sourcemap(self):
        with tempfile.TemporaryDirectory() as tmp:
            dump = Path(tmp) / "dump"
            scripts = dump / "scripts"
            scripts.mkdir(parents=True)
            (scripts / "001-app.js.map").write_text(
                json.dumps(
                    {
                        "version": 3,
                        "sourceRoot": "src",
                        "sources": ["webpack://app/src/api.ts", "../components/User.tsx"],
                        "sourcesContent": [
                            "export const path = '/api/v1/users';",
                            "export const query = `query CurrentUser { viewer { id } }`;",
                        ],
                    }
                ),
                encoding="utf-8",
            )
            out = Path(tmp) / "sources"
            result = subprocess.run(
                ["python3", str(SOURCEMAPS), str(dump), "--out", str(out), "--json-out", str(Path(tmp) / "maps.json")],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            files = sorted(p.name for p in out.rglob("*") if p.is_file())
            self.assertIn("api.ts", files)
            self.assertIn("User.tsx", files)
            self.assertTrue((out / "src" / "app" / "src" / "api.ts").exists())
            manifest = json.loads((Path(tmp) / "maps.json").read_text())
            self.assertEqual(manifest["extracted_sources"], 2)

    def test_analyzes_graphql_from_dump_and_har_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            dump = Path(tmp) / "dump"
            dump.mkdir()
            (dump / "app.js").write_text(
                """
                const q = `query CurrentUser { viewer { id __typename } }`;
                const m = `mutation SaveUser($id: ID!) { saveUser(id: $id) { id } }`;
                fetch('/graphql', { method: 'POST', body: JSON.stringify({ operationName: 'CurrentUser', query: q }) });
                """,
                encoding="utf-8",
            )
            har = Path(tmp) / "har.json"
            har.write_text(
                json.dumps(
                    {
                        "graphql_operations": [
                            {"kind": "query", "name": "CurrentUser", "count": 1, "endpoints": ["POST api.example.com/graphql"]},
                            {"kind": "subscription", "name": "LiveUpdates", "count": 1, "endpoints": ["WS api.example.com/graphql"]},
                        ],
                        "endpoints": [{"method": "POST", "host": "api.example.com", "path": "/graphql"}],
                    }
                ),
                encoding="utf-8",
            )
            out = Path(tmp) / "graphql.json"
            result = subprocess.run(
                ["python3", str(GRAPHQL), str(dump), "--har-json", str(har), "--json-out", str(out)],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(out.read_text())
            names = {op["name"] for op in data["operations"]}
            self.assertIn("CurrentUser", names)
            self.assertIn("SaveUser", names)
            self.assertIn("LiveUpdates", names)
            self.assertIn("https://api.example.com/graphql", data["endpoint_candidates"])


if __name__ == "__main__":
    unittest.main()
