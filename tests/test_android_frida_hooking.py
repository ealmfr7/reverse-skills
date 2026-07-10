import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JAVA_SCRIPT = ROOT / "android-frida-hooking" / "scripts" / "make-java-hook.py"
NATIVE_SCRIPT = ROOT / "android-frida-hooking" / "scripts" / "make-native-hook.py"


class AndroidFridaHookingTests(unittest.TestCase):
    def test_generates_java_hook_with_overload_and_stacktrace(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "hook.js"
            result = subprocess.run(
                [
                    "python3",
                    str(JAVA_SCRIPT),
                    "com.example.AuthManager",
                    "login",
                    "--overload",
                    "java.lang.String,java.lang.String",
                    "--stacktrace",
                    "--out",
                    str(out),
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            js = out.read_text(encoding="utf-8")
            self.assertIn('Java.use("com.example.AuthManager")', js)
            self.assertIn('Target.login.overload("java.lang.String", "java.lang.String")', js)
            self.assertIn("Log.getStackTraceString", js)
            self.assertIn("return ret;", js)

    def test_generates_native_hook_waiting_for_module_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "native.js"
            result = subprocess.run(
                [
                    "python3",
                    str(NATIVE_SCRIPT),
                    "libsign.so",
                    "--export",
                    "sign_payload",
                    "--wait-load",
                    "--out",
                    str(out),
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            js = out.read_text(encoding="utf-8")
            self.assertIn('hookNowOrOnLoad("libsign.so"', js)
            self.assertIn('mod.getExportByName("sign_payload")', js)
            self.assertIn("Interceptor.attach", js)


if __name__ == "__main__":
    unittest.main()
