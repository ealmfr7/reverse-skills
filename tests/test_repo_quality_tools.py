import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepoQualityToolsTests(unittest.TestCase):
    def test_generate_tools_index_outputs_commands_by_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "TOOLS.md"
            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "generate-tools-index.py"),
                    "--out",
                    str(out),
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            text = out.read_text(encoding="utf-8")
            self.assertIn("# Reverse Skill Tool Index", text)
            self.assertIn("## android-frida-hooking", text)
            self.assertIn("`reverse-skill android-frida-hooking make-java-hook`", text)
            self.assertIn("## web-api-reverse-engineering", text)
            self.assertIn("`reverse-skill web-api-reverse-engineering fingerprint-web`", text)
            self.assertNotIn("__pycache__", text)
            self.assertNotIn("`reverse-skill reverse-docs-workflow common`", text)

    def test_tools_index_is_current(self):
        result = subprocess.run(
            ["python3", str(ROOT / "scripts" / "generate-tools-index.py"), "--check"],
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_lint_skills_passes_current_repo(self):
        result = subprocess.run(
            ["python3", str(ROOT / "scripts" / "lint-skills.py")],
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("SKILL_LINT_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
