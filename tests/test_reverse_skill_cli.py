import json
import re
import shlex
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

    def test_skill_docs_prefer_stable_cli_for_bundled_tools(self):
        direct_script_patterns = [
            re.compile(r"\b(?:python3|bash)\s+scripts/[A-Za-z0-9_.-]+\.(?:py|sh)\b"),
            re.compile(r"\b(?:python3|bash)\s+[A-Za-z0-9_.-]+/scripts/[A-Za-z0-9_.-]+\.(?:py|sh)\b"),
        ]

        offenders = []
        for skill_doc in sorted(ROOT.glob("*/SKILL.md")):
            text = skill_doc.read_text(encoding="utf-8")
            for line_no, line in enumerate(text.splitlines(), start=1):
                if any(pattern.search(line) for pattern in direct_script_patterns):
                    offenders.append(f"{skill_doc.relative_to(ROOT)}:{line_no}:{line.strip()}")

        self.assertEqual([], offenders)

    def test_doctor_reports_cli_and_skill_roots(self):
        result = subprocess.run(
            [str(CLI), "doctor"],
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Reverse Skill Doctor", result.stdout)
        self.assertIn("cli:", result.stdout)
        self.assertIn("skills:", result.stdout)
        self.assertIn("roots:", result.stdout)
        self.assertIn("repo", result.stdout)
        self.assertIn(str(ROOT), result.stdout)

    def test_doctor_reports_json(self):
        result = subprocess.run(
            [str(CLI), "doctor", "--json"],
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["cli"]["path"], str(CLI))
        self.assertGreaterEqual(data["skills"]["count"], 1)
        self.assertIn("repo", {root["kind"] for root in data["roots"]})
        self.assertIn("python3", data["tools"])

    def test_documented_reverse_skill_commands_resolve(self):
        offenders = []
        docs = [ROOT / "README.md", *sorted(ROOT.glob("*/SKILL.md"))]
        for doc in docs:
            for line_no, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), start=1):
                if "reverse-skill " not in line:
                    continue
                command = line.strip().removesuffix("\\").strip()
                if not command.startswith("reverse-skill "):
                    continue
                try:
                    parts = shlex.split(command)
                except ValueError as exc:
                    offenders.append(f"{doc.relative_to(ROOT)}:{line_no}: cannot parse: {exc}")
                    continue
                if len(parts) < 3 or parts[1] in {"doctor", "list", "path"}:
                    continue
                result = subprocess.run(
                    [str(CLI), "path", parts[1], parts[2]],
                    text=True,
                    capture_output=True,
                )
                if result.returncode != 0:
                    offenders.append(
                        f"{doc.relative_to(ROOT)}:{line_no}: {parts[1]} {parts[2]}: {result.stderr.strip()}"
                    )

        self.assertEqual([], offenders)

    def test_outputs_bash_completion(self):
        result = subprocess.run(
            [str(CLI), "completion", "bash"],
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("_reverse_skill()", result.stdout)
        self.assertIn("complete -F _reverse_skill reverse-skill", result.stdout)
        self.assertIn("doctor list path completion", result.stdout)
        self.assertNotIn("_init_completion", result.stdout)

    def test_plugin_build_refreshes_cli_symlink(self):
        build_script = ROOT / "scripts" / "build-local-plugin.sh"
        text = build_script.read_text(encoding="utf-8")

        self.assertIn("install-reverse-skill.sh", text)


if __name__ == "__main__":
    unittest.main()
