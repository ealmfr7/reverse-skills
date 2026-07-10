import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTE = ROOT / "reverse-engineering-workflow" / "scripts" / "route-reversing-task.py"


class ReverseEngineeringWorkflowTests(unittest.TestCase):
    def test_routes_android_web_udp_and_operational_layers(self):
        result = subprocess.run(
            [
                "python3",
                str(ROUTE),
                "Analyze APK, hook Frida login, inspect UDP media traffic, and produce findings report",
                "--artifact",
                "app.apk",
                "--artifact",
                "capture.pcap",
                "--artifact",
                "notes.md",
                "--json",
            ],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        skills = data["skills"]
        self.assertIn("reverse-investigation-workflow", skills)
        self.assertIn("android-reversing-workflow", skills)
        self.assertIn("android-frida-hooking", skills)
        self.assertIn("udp-protocol-reverse-engineering", skills)
        self.assertIn("reverse-docs-workflow", skills)
        self.assertIn("reverse-probe-tooling-workflow", skills)

    def test_routes_web_api_without_android(self):
        result = subprocess.run(
            [
                "python3",
                str(ROUTE),
                "Review HAR and JavaScript bundles to document GraphQL endpoints",
                "--artifact",
                "capture.har",
                "--artifact",
                "app.js",
                "--json",
            ],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertIn("web-api-reverse-engineering", data["skills"])
        self.assertNotIn("android-reversing-workflow", data["skills"])


if __name__ == "__main__":
    unittest.main()
