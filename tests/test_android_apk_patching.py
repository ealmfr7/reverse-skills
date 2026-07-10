import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "android-apk-patching" / "scripts" / "add-network-security-config.py"


class AndroidApkPatchingTests(unittest.TestCase):
    def test_adds_network_security_config_idempotently(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "decoded"
            project.mkdir()
            manifest = project / "AndroidManifest.xml"
            manifest.write_text(
                """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application android:label="@string/app_name" />
</manifest>
""",
                encoding="utf-8",
            )

            for _ in range(2):
                result = subprocess.run(
                    ["python3", str(SCRIPT), str(project), "--cleartext", "--trust-user-certs"],
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

            config = project / "res" / "xml" / "network_security_config.xml"
            self.assertTrue(config.exists())
            config_text = config.read_text(encoding="utf-8")
            self.assertEqual(config_text.count("<network-security-config>"), 1)
            self.assertIn("<certificates src=\"user\" />", config_text)
            self.assertIn("cleartextTrafficPermitted=\"true\"", config_text)

            tree = ET.parse(manifest)
            app = tree.getroot().find("application")
            self.assertIsNotNone(app)
            ns = "{http://schemas.android.com/apk/res/android}"
            self.assertEqual(app.attrib[f"{ns}networkSecurityConfig"], "@xml/network_security_config")


if __name__ == "__main__":
    unittest.main()
