import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "reverse-skill"
FIXTURES = ROOT / "tests" / "fixtures" / "android-device-attestation-lab"


class ReverseSkillCliTests(unittest.TestCase):
    def test_lists_skills_and_skill_tools(self):
        result = subprocess.run([str(CLI), "list"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("android-device-attestation-lab", result.stdout)

        result = subprocess.run(
            [str(CLI), "list", "android-device-attestation-lab"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("verify-attestation-report", result.stdout)

    def test_resolves_paths_without_cache_paths(self):
        result = subprocess.run(
            [str(CLI), "path", "android-device-attestation-lab", "verify-attestation-report"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("android-device-attestation-lab/scripts/verify-attestation-report.py", result.stdout)
        self.assertNotIn(".codex/plugins/cache", result.stdout)

    def test_runs_python_and_shell_tools(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "verification.json"
            result = subprocess.run(
                [
                    str(CLI),
                    "android-device-attestation-lab",
                    "verify-attestation-report",
                    str(FIXTURES / "physical-pass" / "env-probe.json"),
                    "--root-diff",
                    str(FIXTURES / "physical-pass" / "root-diff.json"),
                    "--expected-attestation-security-level",
                    "TrustedEnvironment",
                    "--expected-keymaster-security-level",
                    "TrustedEnvironment",
                    "--require-device-locked",
                    "--json-out",
                    str(out),
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertTrue(data["policy"]["backendStrict"]["passed"])

        result = subprocess.run(
            [str(CLI), "rev-ghidra", "check-ghidra-deps"],
            text=True,
            capture_output=True,
        )
        self.assertIn(result.returncode, (0, 1))
        self.assertNotIn(".codex/plugins/cache", " ".join(result.args))


if __name__ == "__main__":
    unittest.main()
