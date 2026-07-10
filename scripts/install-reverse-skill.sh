#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="${HOME}/.local/bin"
TARGET="${BIN_DIR}/reverse-skill"

mkdir -p "$BIN_DIR"
ln -sf "${ROOT_DIR}/scripts/reverse-skill" "$TARGET"
chmod +x "${ROOT_DIR}/scripts/reverse-skill"

echo "INSTALLED:${TARGET}"
