import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "android-cross-platform-reversing" / "scripts" / "fingerprint-framework.py"


class AndroidCrossPlatformTests(unittest.TestCase):
    def test_fingerprints_framework_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk = Path(tmp) / "sample.apk"
            out = Path(tmp) / "fingerprint.json"
            with zipfile.ZipFile(apk, "w") as zf:
                zf.writestr("lib/arm64-v8a/libflutter.so", "x")
                zf.writestr("lib/arm64-v8a/libapp.so", "x")
                zf.writestr("assets/flutter_assets/AssetManifest.json", "{}")
                zf.writestr("assets/index.android.bundle", "fetch('/api/users')")
                zf.writestr("assets/main.hbc", "Hermes")
                zf.writestr("assets/www/cordova.js", "cordova")
                zf.writestr("assemblies/App.dll", "mono")
                zf.writestr("lib/arm64-v8a/libmonodroid.so", "x")
                zf.writestr("lib/arm64-v8a/libil2cpp.so", "x")
                zf.writestr("assets/bin/Data/Managed/Metadata/global-metadata.dat", "x")

            result = subprocess.run(
                ["python3", str(SCRIPT), str(apk), "--json-out", str(out)],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertIn("Flutter", data["frameworks"])
            self.assertIn("React Native", data["frameworks"])
            self.assertIn("Cordova/Capacitor", data["frameworks"])
            self.assertIn("Xamarin", data["frameworks"])
            self.assertIn("Unity IL2CPP", data["frameworks"])
            self.assertTrue(any("rev-u3d-dump" in step for step in data["recommended_next_steps"]))


if __name__ == "__main__":
    unittest.main()
