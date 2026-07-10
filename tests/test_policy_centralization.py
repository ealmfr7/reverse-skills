import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PolicyCentralizationTests(unittest.TestCase):
    def test_repository_use_policy_is_centralized_in_readme(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Repository Use Policy", readme)
        self.assertIn("explicitly authorized analysis", readme)
        self.assertIn("redact secrets", readme)
        self.assertIn("outside scope", readme)

    def test_repeated_safety_blocks_are_removed_from_primary_skills(self):
        primary = [
            "android-frida-hooking/SKILL.md",
            "android-apk-patching/SKILL.md",
            "android-traffic-analysis/SKILL.md",
            "udp-protocol-reverse-engineering/SKILL.md",
            "web-api-reverse-engineering/SKILL.md",
            "android-reversing-workflow/SKILL.md",
            "reverse-engineering-workflow/SKILL.md",
        ]
        forbidden = [
            "Work only on",
            "Patch only apps",
            "Analyze only traffic",
            "Do not help abuse",
            "Do not help attack",
            "Do not help bypass",
            "Confirm authorization",
            "Redact tokens",
            "owned app",
        ]
        for rel in primary:
            text = (ROOT / rel).read_text(encoding="utf-8")
            for phrase in forbidden:
                self.assertNotIn(phrase, text, rel)


if __name__ == "__main__":
    unittest.main()
