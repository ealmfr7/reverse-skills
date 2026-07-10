import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "reverse-investigation-workflow" / "scripts" / "init-case.py"
ARTIFACT = ROOT / "reverse-investigation-workflow" / "scripts" / "add-artifact.py"
INDEX = ROOT / "reverse-investigation-workflow" / "scripts" / "index-artifacts.py"
RUN = ROOT / "reverse-investigation-workflow" / "scripts" / "new-run.py"


class ReverseInvestigationWorkflowTests(unittest.TestCase):
    def test_creates_case_adds_artifact_and_indexes_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            case_id = "2026-07-10-likee-live"

            result = subprocess.run(
                [
                    "python3",
                    str(INIT),
                    case_id,
                    "--root",
                    str(root),
                    "--target",
                    "likee",
                    "--platform",
                    "android",
                    "--country",
                    "US",
                    "--authorization",
                    "lab",
                    "--goal",
                    "Trace live room bootstrap",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            case_dir = root / "cases" / case_id
            self.assertTrue((case_dir / "case.yaml").exists())
            self.assertTrue((case_dir / "artifacts" / "frida").is_dir())
            self.assertIn("CASE_CREATED", result.stdout)

            src = root / "hook.js"
            src.write_text("console.log('hook');\n", encoding="utf-8")
            result = subprocess.run(
                [
                    "python3",
                    str(ARTIFACT),
                    str(case_dir),
                    str(src),
                    "--kind",
                    "frida-script",
                    "--phase",
                    "dynamic",
                    "--note",
                    "login hook",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            result = subprocess.run(
                ["python3", str(INDEX), str(case_dir), "--json-out", str(case_dir / "reports" / "evidence-index.json")],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads((case_dir / "reports" / "evidence-index.json").read_text(encoding="utf-8"))
            self.assertEqual(data["case_id"], case_id)
            self.assertTrue(any(item["kind"] == "frida-script" for item in data["artifacts"]))

            result = subprocess.run(
                [
                    "python3",
                    str(RUN),
                    str(case_dir),
                    "dynamic-login-hook",
                    "--phase",
                    "dynamic",
                    "--command",
                    "frida -U -f com.example.app -l artifacts/frida/hook.js",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("RUN_CREATED", result.stdout)
            self.assertTrue((case_dir / "runs" / "0001-dynamic-dynamic-login-hook" / "command.md").exists())


if __name__ == "__main__":
    unittest.main()
