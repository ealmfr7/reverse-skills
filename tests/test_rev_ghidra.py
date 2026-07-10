import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "rev-ghidra" / "scripts" / "make-frida-offset-hooks.py"


class RevGhidraTests(unittest.TestCase):
    def test_generates_frida_offset_hooks_from_function_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            functions = Path(tmp) / "functions.json"
            out = Path(tmp) / "hooks.js"
            functions.write_text(
                json.dumps(
                    {
                        "module": "libsign.so",
                        "image_base": "0x100000",
                        "functions": [
                            {"name": "Java_com_example_Sign_sign", "entry": "0x101234"},
                            {"name": "FUN_00102000", "offset": "0x2000"},
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                ["python3", str(SCRIPT), str(functions), "--out", str(out)],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            js = out.read_text(encoding="utf-8")
            self.assertIn('Process.getModuleByName("libsign.so")', js)
            self.assertIn('base.add(0x1234)', js)
            self.assertIn('base.add(0x2000)', js)
            self.assertIn("Java_com_example_Sign_sign", js)


if __name__ == "__main__":
    unittest.main()
