#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_NAME="reverse-skills"
PLUGIN_PARENT="${PLUGIN_PARENT:-$HOME/plugins}"
PLUGIN_DIR="$PLUGIN_PARENT/$PLUGIN_NAME"
MARKETPLACE_PATH="$HOME/.agents/plugins/marketplace.json"
PLUGIN_CREATOR="/home/ubuntu/.codex/skills/.system/plugin-creator/scripts"

if [[ ! -d "$PLUGIN_DIR" ]]; then
  python3 "$PLUGIN_CREATOR/create_basic_plugin.py" "$PLUGIN_NAME" \
    --path "$PLUGIN_PARENT" \
    --with-skills \
    --with-marketplace
fi

mkdir -p "$PLUGIN_DIR/skills"

python3 "$ROOT_DIR/scripts/lint-skills.py"
python3 "$ROOT_DIR/scripts/generate-tools-index.py" --check

while IFS= read -r skill_dir; do
  rel="${skill_dir#./}"
  mkdir -p "$PLUGIN_DIR/skills/$rel"
  rsync -a --delete "$ROOT_DIR/$rel/" "$PLUGIN_DIR/skills/$rel/"
done < <(cd "$ROOT_DIR" && find . -maxdepth 2 -name SKILL.md -printf '%h\n' | sort)

python3 "$PLUGIN_CREATOR/validate_plugin.py" "$PLUGIN_DIR"
python3 "$PLUGIN_CREATOR/update_plugin_cachebuster.py" "$PLUGIN_DIR"
codex plugin add "$PLUGIN_NAME@personal" >/dev/null
bash "$ROOT_DIR/scripts/install-reverse-skill.sh" >/dev/null

echo "PLUGIN_SYNCED:$PLUGIN_DIR"
echo "MARKETPLACE:$MARKETPLACE_PATH"
