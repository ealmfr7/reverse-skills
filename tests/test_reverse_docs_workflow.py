import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "reverse-docs-workflow" / "scripts" / "init-docs.py"
NEW_FINDING = ROOT / "reverse-docs-workflow" / "scripts" / "new-finding.py"
NEW_DECISION = ROOT / "reverse-docs-workflow" / "scripts" / "new-decision.py"
INDEX = ROOT / "reverse-docs-workflow" / "scripts" / "index-docs.py"
SUPERSEDE = ROOT / "reverse-docs-workflow" / "scripts" / "mark-superseded.py"
LINT = ROOT / "reverse-docs-workflow" / "scripts" / "lint-docs.py"


class ReverseDocsWorkflowTests(unittest.TestCase):
    def test_creates_docs_generates_ids_indexes_and_marks_superseded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = subprocess.run(
                ["python3", str(INIT), "--root", str(root), "--project", "live protocol reconstruction"],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            docs = root / "docs"
            self.assertTrue((docs / "INDEX.md").exists())
            self.assertTrue((docs / "findings").is_dir())
            self.assertIn("DOCS_CREATED", result.stdout)

            result = subprocess.run(
                [
                    "python3",
                    str(NEW_FINDING),
                    str(docs),
                    "udp bootstrap uses dominant session",
                    "--target",
                    "likee",
                    "--case-id",
                    "2026-07-10-likee-live",
                    "--evidence",
                    "cases/2026-07-10-likee-live/runs/0001/observations.md",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            finding = docs / "findings" / "F-0001-udp-bootstrap-uses-dominant-session.md"
            self.assertTrue(finding.exists())
            self.assertIn("id: F-0001", finding.read_text(encoding="utf-8"))

            result = subprocess.run(
                [
                    "python3",
                    str(NEW_DECISION),
                    str(docs),
                    "prefer case folders over tmp",
                    "--status",
                    "active",
                    "--rationale",
                    "Artifacts need stable paths for reports.",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            decision = docs / "decisions" / "D-0001-prefer-case-folders-over-tmp.md"
            self.assertTrue(decision.exists())

            result = subprocess.run(
                [
                    "python3",
                    str(SUPERSEDE),
                    str(finding),
                    "--by",
                    "F-0002",
                    "--reason",
                    "Replaced by cleaner packet-level evidence.",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status: superseded", finding.read_text(encoding="utf-8"))

            result = subprocess.run(
                ["python3", str(INDEX), str(docs), "--json-out", str(docs / "docs-index.json")],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            index = json.loads((docs / "docs-index.json").read_text(encoding="utf-8"))
            self.assertEqual(len(index["documents"]), 2)
            self.assertTrue(any(item["id"] == "F-0001" and item["status"] == "superseded" for item in index["documents"]))

            result = subprocess.run(["python3", str(LINT), str(docs)], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("DOCS_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
