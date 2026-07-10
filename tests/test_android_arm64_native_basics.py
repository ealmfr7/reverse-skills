import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "android-arm64-native-basics" / "scripts" / "offset-math.py"


class AndroidArm64NativeBasicsTests(unittest.TestCase):
    def test_computes_offset_and_runtime_address(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "offset.json"
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--image-base",
                    "0x100000",
                    "--entry",
                    "0x101234",
                    "--module-base",
                    "0x7a00000000",
                    "--json-out",
                    str(out),
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["offset"], "0x1234")
            self.assertEqual(data["runtime_address"], "0x7a00001234")
            self.assertIn("module.base.add(0x1234)", result.stdout)


if __name__ == "__main__":
    unittest.main()
