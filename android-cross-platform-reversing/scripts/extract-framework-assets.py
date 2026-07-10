#!/usr/bin/env python3
import argparse
import shutil
import sys
import zipfile
from pathlib import Path


INTERESTING = (
    "assets/index.android.bundle",
    ".hbc",
    "assets/www/",
    "flutter_assets/",
    "global-metadata.dat",
    "libil2cpp.so",
    "libapp.so",
    "libflutter.so",
)


def is_interesting(name: str) -> bool:
    lower = name.lower()
    return any(marker in lower for marker in INTERESTING)


def safe_target(out: Path, name: str) -> Path:
    target = (out / name).resolve()
    root = out.resolve()
    if root not in target.parents and target != root:
        raise ValueError(f"unsafe archive path: {name}")
    return target


def extract(apk: Path, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    extracted = []
    with zipfile.ZipFile(apk) as zf:
        for info in zf.infolist():
            if info.is_dir() or not is_interesting(info.filename):
                continue
            target = safe_target(out, info.filename)
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            extracted.append(str(target.relative_to(out)))
    return extracted


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract cross-platform APK assets for manual analysis.")
    parser.add_argument("apk", help="APK file")
    parser.add_argument("--out", required=True, help="Output directory")
    args = parser.parse_args()

    apk = Path(args.apk)
    if not apk.is_file():
        print(f"ERROR: file not found: {apk}", file=sys.stderr)
        return 2

    try:
        extracted = extract(apk, Path(args.out))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"EXTRACTED:{len(extracted)}")
    for item in extracted[:200]:
        print(item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
