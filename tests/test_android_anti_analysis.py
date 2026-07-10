import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCAN = ROOT / "android-anti-analysis-and-obfuscation" / "scripts" / "scan-anti-analysis.py"


class AndroidAntiAnalysisTests(unittest.TestCase):
    def test_scans_static_tree_for_anti_analysis_signals(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp)
            manifest = tree / "AndroidManifest.xml"
            manifest.write_text(
                '<manifest><application android:debuggable="false" android:extractNativeLibs="false"/></manifest>',
                encoding="utf-8",
            )
            source = tree / "sources" / "com" / "example" / "Guard.java"
            source.parent.mkdir(parents=True)
            source.write_text(
                """
                if (Build.FINGERPRINT.contains("generic") || Build.MODEL.contains("sdk_gphone")) {}
                String[] root = {"/system/xbin/su", "magisk", "busybox"};
                Class.forName("de.robv.android.xposed.XposedBridge");
                ptrace(PTRACE_TRACEME, 0, 0, 0);
                CertificatePinner.Builder builder = new CertificatePinner.Builder();
                IntegrityManager manager = IntegrityManagerFactory.create(context);
                SafetyNet.getClient(context).attest(nonce, apiKey);
                System.loadLibrary("jiagu");
                """,
                encoding="utf-8",
            )
            native = tree / "lib" / "arm64-v8a" / "libguard.so.strings.txt"
            native.parent.mkdir(parents=True)
            native.write_text("frida-server gum-js-loop /proc/self/maps tracerpid", encoding="utf-8")

            result = subprocess.run(
                ["python3", str(SCAN), str(tree), "--json-out", str(tree / "anti-analysis.json")],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads((tree / "anti-analysis.json").read_text(encoding="utf-8"))
            categories = {item["category"] for item in data["findings"]}
            self.assertTrue(
                {
                    "root-detection",
                    "emulator-detection",
                    "frida-detection",
                    "native-anti-debug",
                    "certificate-pinning",
                    "play-integrity-attestation",
                    "packing-loader",
                }.issubset(categories)
            )
            self.assertGreaterEqual(data["riskScore"], 7)


if __name__ == "__main__":
    unittest.main()
