from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


CASE_SUBDIRS = [
    "inputs/apks",
    "inputs/urls",
    "inputs/accounts",
    "inputs/devices",
    "artifacts/decompiled",
    "artifacts/frida",
    "artifacts/pcaps",
    "artifacts/screenshots",
    "artifacts/logs",
    "artifacts/ghidra",
    "artifacts/jadx",
    "artifacts/web",
    "runs",
    "notes",
    "reports",
    "scripts",
]

KIND_DIR = {
    "apk": "inputs/apks",
    "url": "inputs/urls",
    "device": "inputs/devices",
    "decompiled": "artifacts/decompiled",
    "frida-script": "artifacts/frida",
    "pcap": "artifacts/pcaps",
    "har": "artifacts/web",
    "screenshot": "artifacts/screenshots",
    "log": "artifacts/logs",
    "ghidra-project": "artifacts/ghidra",
    "jadx-output": "artifacts/jadx",
    "report": "reports",
    "source-dump": "artifacts/web",
    "api-client": "artifacts/web",
}

VALID_STATUSES = {"planned", "active", "blocked", "paused", "complete", "archived"}
VALID_PLATFORMS = {"android", "ios", "web", "backend", "native", "mixed"}
VALID_AUTH = {"owned", "lab", "ctf", "contracted", "defensive", "unknown"}
VALID_PHASES = {"intake", "fingerprint", "static", "dynamic", "traffic", "native", "patching", "replay", "reporting"}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_yaml_like(path: Path, data: dict) -> None:
    lines = []
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {json.dumps(item)}")
        elif isinstance(value, dict):
            lines.append(f"{key}:")
            for child_key, child_value in value.items():
                lines.append(f"  {child_key}: {json.dumps(child_value)}")
        else:
            lines.append(f"{key}: {json.dumps(value)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_case_id(case_dir: Path) -> str:
    case_yaml = case_dir / "case.yaml"
    if not case_yaml.exists():
        return case_dir.name
    for line in case_yaml.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("id:"):
            return line.split(":", 1)[1].strip().strip('"')
    return case_dir.name


def copy_artifact(src: Path, dst_dir: Path) -> Path:
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    if src.is_dir():
        if dst.exists():
            raise FileExistsError(f"destination exists: {dst}")
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)
    return dst
