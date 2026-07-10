import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "udp-protocol-reverse-engineering" / "scripts" / "udp-json-summary.py"
CLUSTER = ROOT / "udp-protocol-reverse-engineering" / "scripts" / "udp-payload-cluster.py"
FIELDS = ROOT / "udp-protocol-reverse-engineering" / "scripts" / "udp-field-candidates.py"


class UdpProtocolReverseEngineeringTests(unittest.TestCase):
    def test_summarizes_tshark_json_udp_flows(self):
        with tempfile.TemporaryDirectory() as tmp:
            packets = Path(tmp) / "packets.json"
            out = Path(tmp) / "summary.json"
            packets.write_text(
                json.dumps(
                    [
                        {
                            "_source": {
                                "layers": {
                                    "frame": {"frame.time_epoch": "1.0", "frame.len": "60"},
                                    "ip": {"ip.src": "10.0.0.2", "ip.dst": "10.0.0.3"},
                                    "udp": {"udp.srcport": "1234", "udp.dstport": "9000", "udp.length": "12", "udp.payload": "01:02:03:04"},
                                }
                            }
                        },
                        {
                            "_source": {
                                "layers": {
                                    "frame": {"frame.time_epoch": "1.5", "frame.len": "64"},
                                    "ip": {"ip.src": "10.0.0.3", "ip.dst": "10.0.0.2"},
                                    "udp": {"udp.srcport": "9000", "udp.dstport": "1234", "udp.length": "13", "udp.payload": "01:02:ff"},
                                }
                            }
                        },
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                ["python3", str(SUMMARY), str(packets), "--json-out", str(out)],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["packet_count"], 2)
            self.assertEqual(data["flows"][0]["packet_count"], 1)
            self.assertEqual(data["flows"][0]["payload_prefixes"][0]["hex"], "01020304")
            self.assertIn("10.0.0.2:1234 -> 10.0.0.3:9000", result.stdout)

    def test_clusters_payloads_by_length_and_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            payloads = Path(tmp) / "payloads.json"
            out = Path(tmp) / "clusters.json"
            payloads.write_text(
                json.dumps(
                    {
                        "payloads": [
                            {"hex": "01020304"},
                            {"hex": "0102ffff"},
                            {"hex": "aabbcc"},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                ["python3", str(CLUSTER), str(payloads), "--prefix-bytes", "2", "--json-out", str(out)],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(out.read_text(encoding="utf-8"))
            keys = {item["key"] for item in data["clusters"]}
            self.assertIn("len=4 prefix=0102", keys)
            self.assertIn("len=3 prefix=aabb", keys)

    def test_detects_constant_bytes_and_monotonic_counters(self):
        with tempfile.TemporaryDirectory() as tmp:
            payloads = Path(tmp) / "payloads.json"
            out = Path(tmp) / "fields.json"
            payloads.write_text(
                json.dumps(
                    {
                        "payloads": [
                            {"hex": "aa00010010"},
                            {"hex": "aa00020020"},
                            {"hex": "aa00030030"},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                ["python3", str(FIELDS), str(payloads), "--json-out", str(out)],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(out.read_text(encoding="utf-8"))
            constants = {(item["offset"], item["hex"]) for item in data["constant_bytes"]}
            self.assertIn((0, "aa"), constants)
            counters = {(item["offset"], item["width"], item["endian"]) for item in data["monotonic_counters"]}
            self.assertIn((1, 2, "big"), counters)


if __name__ == "__main__":
    unittest.main()
