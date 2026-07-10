import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "reverse-probe-tooling-workflow"
NEW_PROBE = SKILL / "scripts" / "new-probe.py"
NEW_ANALYZER = SKILL / "scripts" / "new-analyzer.py"
INIT_RUN = SKILL / "scripts" / "init-run.py"
LINT_EVENTS = SKILL / "scripts" / "lint-events.py"
INDEX_RUN = SKILL / "scripts" / "index-run.py"


class ReverseProbeToolingWorkflowTests(unittest.TestCase):
    def test_scaffolds_probe_analyzer_validates_events_and_indexes_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = subprocess.run(
                [
                    "python3",
                    str(NEW_PROBE),
                    "frida",
                    "java",
                    "likee-bootstrap",
                    "--out",
                    str(root / "probes"),
                    "--source",
                    "frida.likee.bootstrap",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            probe = root / "probes" / "frida" / "likee-bootstrap.js"
            self.assertTrue(probe.exists())
            self.assertIn("schema: 1", probe.read_text(encoding="utf-8"))

            result = subprocess.run(
                [
                    "python3",
                    str(NEW_ANALYZER),
                    "udp-summary",
                    "--out",
                    str(root / "probes" / "python"),
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            analyzer = root / "probes" / "python" / "udp-summary.py"
            self.assertTrue(analyzer.exists())
            self.assertIn("def iter_jsonl", analyzer.read_text(encoding="utf-8"))

            result = subprocess.run(
                [
                    "python3",
                    str(INIT_RUN),
                    str(root / "runs"),
                    "dynamic-bootstrap",
                    "--case-id",
                    "2026-07-10-likee-live",
                    "--probe",
                    "probes/frida/likee-bootstrap.js",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            run = root / "runs" / "0001-dynamic-bootstrap"
            self.assertTrue((run / "meta.json").exists())
            self.assertTrue((run / "events.jsonl").exists())

            event = {
                "schema": 1,
                "type": "event",
                "event": "probe.start",
                "ts": 1.0,
                "source": "frida.likee.bootstrap",
                "data": {"status": "ok"},
            }
            (run / "events.jsonl").write_text(json.dumps(event, sort_keys=True) + "\n", encoding="utf-8")

            result = subprocess.run(["python3", str(LINT_EVENTS), str(run / "events.jsonl")], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("EVENTS_OK", result.stdout)

            result = subprocess.run(
                ["python3", str(INDEX_RUN), str(run), "--json-out", str(run / "run-index.json")],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            index = json.loads((run / "run-index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["eventCount"], 1)
            self.assertEqual(index["caseId"], "2026-07-10-likee-live")


if __name__ == "__main__":
    unittest.main()
