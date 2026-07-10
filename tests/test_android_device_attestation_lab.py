import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "android-device-attestation-lab"
PREFLIGHT = SKILL / "scripts" / "android-target-preflight.py"
SUMMARY = SKILL / "scripts" / "attestation-artifact-summary.py"
ENV_CAPTURE = SKILL / "scripts" / "android-env-capture.py"
COMPARE = SKILL / "scripts" / "compare-attestation-runs.py"
PARSE = SKILL / "scripts" / "parse-android-key-attestation.py"
VERIFY = SKILL / "scripts" / "verify-attestation-report.py"
ROUTE = ROOT / "reverse-engineering-workflow" / "scripts" / "route-reversing-task.py"
FIXTURES = ROOT / "tests" / "fixtures" / "android-device-attestation-lab"


class AndroidDeviceAttestationLabTests(unittest.TestCase):
    def test_summarizes_attestation_artifacts_without_snapchat_specifics(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            (run / "env-probe.json").write_text(
                json.dumps(
                    {
                        "device": {"serial": "device-1"},
                        "key_attestation": {
                            "chain_present": True,
                            "chain_length": 3,
                            "certificates": [{"subject": "leaf"}, {"subject": "root"}],
                        },
                    }
                ),
                encoding="utf-8",
            )
            (run / "verification.json").write_text(
                json.dumps(
                    {
                        "policy": {
                            "backendStrict": {
                                "passed": False,
                                "reasons": ["missing exact Google root certificate match"],
                            }
                        },
                        "checks": {
                            "attestationSecurityLevel": "Software",
                            "keymasterSecurityLevel": "Software",
                            "deviceLocked": False,
                        },
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                ["python3", str(SUMMARY), str(run), "--json-out", str(run / "summary.json")],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads((run / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(data["artifactCount"], 2)
            self.assertIn("env-probe", data["present"])
            self.assertIn("verification", data["present"])
            self.assertIn("attestation-chain-present", data["signals"])
            self.assertIn("backend-strict-failed", data["signals"])
            self.assertIn("compare against a known-good physical-device run", data["nextSteps"])
            self.assertNotIn("snapchat", json.dumps(data).lower())

    def test_preflight_help_is_generic(self):
        result = subprocess.run(
            ["python3", str(PREFLIGHT), "--help"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        help_text = result.stdout.lower()
        self.assertIn("--package", help_text)
        self.assertIn("--foreground-regex", help_text)
        self.assertNotIn("snapchat", help_text)
        self.assertNotIn("likee", help_text)

    def test_env_capture_help_is_generic_and_supports_multiple_packages(self):
        result = subprocess.run(
            ["python3", str(ENV_CAPTURE), "--help"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        help_text = result.stdout.lower()
        self.assertIn("--package", help_text)
        self.assertIn("--raw-out", help_text)
        self.assertNotIn("snapchat", help_text)
        self.assertNotIn("likee", help_text)

    def test_compare_attestation_runs_uses_fixtures(self):
        physical = FIXTURES / "physical-pass"
        vmos = FIXTURES / "vmos-backend-fail"
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "comparison.json"
            result = subprocess.run(
                [
                    "python3",
                    str(COMPARE),
                    str(physical),
                    str(vmos),
                    "--left-label",
                    "physical",
                    "--right-label",
                    "vmos",
                    "--json-out",
                    str(out),
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(data["leftLabel"], "physical")
        self.assertEqual(data["rightLabel"], "vmos")
        self.assertIn("backendStrict", data["differences"])
        self.assertIn("attestationSecurityLevel", data["differences"])
        self.assertIn("exactGoogleRootMatch", data["differences"])
        self.assertIn("treat key possession and backend trust as separate claims", data["nextSteps"])
        self.assertNotIn("snapchat", json.dumps(data).lower())

    def test_parse_and_verify_attestation_report_fixtures(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            parsed = out_dir / "parsed.json"
            verified = out_dir / "verified.json"
            report = FIXTURES / "physical-pass" / "env-probe.json"
            result = subprocess.run(
                ["python3", str(PARSE), str(report), "--json-out", str(parsed)],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            parsed_data = json.loads(parsed.read_text(encoding="utf-8"))
            self.assertTrue(parsed_data["chainPresent"])
            self.assertEqual(parsed_data["chainLength"], 4)
            self.assertIn("chain-present", parsed_data["signals"])

            result = subprocess.run(
                [
                    "python3",
                    str(VERIFY),
                    str(report),
                    "--root-diff",
                    str(FIXTURES / "physical-pass" / "root-diff.json"),
                    "--expected-attestation-security-level",
                    "TrustedEnvironment",
                    "--expected-keymaster-security-level",
                    "TrustedEnvironment",
                    "--require-device-locked",
                    "--json-out",
                    str(verified),
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            verified_data = json.loads(verified.read_text(encoding="utf-8"))
            self.assertTrue(verified_data["policy"]["backendStrict"]["passed"])
            self.assertTrue(verified_data["checks"]["exactGoogleRootMatch"])
            self.assertTrue(verified_data["checks"]["spkiGoogleRootMatch"])
            self.assertNotIn("snapchat", json.dumps(verified_data).lower())

    def test_verify_attestation_report_flags_backend_strict_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "verified.json"
            result = subprocess.run(
                [
                    "python3",
                    str(VERIFY),
                    str(FIXTURES / "vmos-backend-fail" / "env-probe.json"),
                    "--root-diff",
                    str(FIXTURES / "vmos-backend-fail" / "root-diff.json"),
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
            self.assertFalse(data["policy"]["backendStrict"]["passed"])
            self.assertIn("missing exact Google root certificate match", data["policy"]["backendStrict"]["reasons"])
            self.assertIn("attestation security level mismatch", data["policy"]["backendStrict"]["reasons"])
            self.assertIn("device is not locked", data["policy"]["backendStrict"]["reasons"])

    def test_tool_map_uses_final_generic_tool_names(self):
        text = (SKILL / "references" / "tool-map.md").read_text(encoding="utf-8").lower()
        self.assertIn("android-env-capture.py", text)
        self.assertIn("android-target-preflight.py", text)
        self.assertIn("compare-attestation-runs.py", text)
        self.assertIn("parse-android-key-attestation.py", text)
        self.assertIn("verify-attestation-report.py", text)
        self.assertNotIn("likee_device_preflight.py", text)
        self.assertNotIn("android_env_probe.py", text)
        self.assertNotIn("../", text)

    def test_master_router_selects_attestation_lab(self):
        result = subprocess.run(
            [
                "python3",
                str(ROUTE),
                "Compare VMOS and physical Android device key attestation, root certificate source, Play Integrity backend trust",
                "--json",
            ],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertIn("android-device-attestation-lab", data["skills"])
        self.assertIn("android-anti-analysis-and-obfuscation", data["skills"])


if __name__ == "__main__":
    unittest.main()
