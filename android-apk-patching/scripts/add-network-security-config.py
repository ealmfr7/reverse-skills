#!/usr/bin/env python3
import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ANDROID_NS = "http://schemas.android.com/apk/res/android"
ANDROID = f"{{{ANDROID_NS}}}"
ET.register_namespace("android", ANDROID_NS)


def indent(elem: ET.Element, level: int = 0) -> None:
    space = "\n" + level * "    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = space + "    "
        for child in elem:
            indent(child, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = space
    elif level and (not elem.tail or not elem.tail.strip()):
        elem.tail = space


def write_config(project: Path, cleartext: bool, trust_user_certs: bool) -> Path:
    xml_dir = project / "res" / "xml"
    xml_dir.mkdir(parents=True, exist_ok=True)
    config = xml_dir / "network_security_config.xml"

    attrs = {"cleartextTrafficPermitted": "true"} if cleartext else {}
    root = ET.Element("network-security-config")
    base = ET.SubElement(root, "base-config", attrs)
    if trust_user_certs:
        trust = ET.SubElement(base, "trust-anchors")
        ET.SubElement(trust, "certificates", {"src": "system"})
        ET.SubElement(trust, "certificates", {"src": "user"})

    indent(root)
    config.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        + ET.tostring(root, encoding="unicode")
        + "\n",
        encoding="utf-8",
    )
    return config


def update_manifest(project: Path) -> Path:
    manifest = project / "AndroidManifest.xml"
    if not manifest.exists():
        raise FileNotFoundError(f"AndroidManifest.xml not found under {project}")

    tree = ET.parse(manifest)
    root = tree.getroot()
    app = root.find("application")
    if app is None:
        app = ET.SubElement(root, "application")
    app.set(f"{ANDROID}networkSecurityConfig", "@xml/network_security_config")
    indent(root)
    tree.write(manifest, encoding="utf-8", xml_declaration=True)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add a lab network_security_config.xml to a decoded apktool project."
    )
    parser.add_argument("project", help="Decoded apktool project directory")
    parser.add_argument("--cleartext", action="store_true", help="Permit cleartext traffic in the generated base-config")
    parser.add_argument("--trust-user-certs", action="store_true", help="Trust user-installed CA certificates in lab builds")
    args = parser.parse_args()

    project = Path(args.project)
    if not project.is_dir():
        print(f"ERROR: project directory not found: {project}", file=sys.stderr)
        return 2

    try:
        config = write_config(project, args.cleartext, args.trust_user_certs)
        manifest = update_manifest(project)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"WROTE:{config}")
    print(f"UPDATED:{manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
