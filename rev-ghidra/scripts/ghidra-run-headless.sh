#!/usr/bin/env bash
set -euo pipefail

binary="${1:-}"
project_dir="${2:-/tmp/ghidra-projects}"
project_name="${3:-CodexGhidraProject}"
post_script="${4:-}"

if [ -z "$binary" ]; then
    echo "Usage: $0 binary [project-dir] [project-name] [post-script]" >&2
    exit 2
fi

if ! command -v analyzeHeadless >/dev/null 2>&1; then
    echo "INSTALL_REQUIRED:analyzeHeadless" >&2
    exit 1
fi

mkdir -p "$project_dir"
cmd=(analyzeHeadless "$project_dir" "$project_name" -import "$binary")
if [ -n "$post_script" ]; then
    cmd+=(-postScript "$post_script")
fi
cmd+=(-deleteProject)

printf 'RUN:'
printf ' %q' "${cmd[@]}"
printf '\n'
"${cmd[@]}"
