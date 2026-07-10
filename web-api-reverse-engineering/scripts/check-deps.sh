#!/usr/bin/env bash
# check-deps.sh - Verify useful tools for web/API reverse engineering.
set -euo pipefail

missing_optional=()

echo "=== Web API Reverse Engineering: Dependency Check ==="
echo

if command -v python3 >/dev/null 2>&1; then
  echo "[OK] python3 detected"
else
  echo "[MISSING] python3 is required for bundled scripts"
  echo
  echo "INSTALL_REQUIRED:python3"
  exit 1
fi

check_optional() {
  local cmd="$1"
  local label="$2"
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "[OK] $label detected"
  else
    echo "[MISSING] $label not found (optional)"
    missing_optional+=("$cmd")
  fi
}

check_optional curl "curl"
check_optional jq "jq"
check_optional node "Node.js"
check_optional npm "npm"
check_optional mitmproxy "mitmproxy"
check_optional mitmdump "mitmdump"
check_optional whatweb "WhatWeb"
check_optional httpx "ProjectDiscovery httpx"
check_optional websocat "websocat"
check_optional prettier "Prettier"

for script in fingerprint-web.py dump-website-js.py capture-playwright-flow.py scan-js-bundle.py extract-endpoints.py har-summary.py extract-sourcemaps.py analyze-graphql.py build-report.py generate-client-skeleton.py; do
  if [[ -x "$(dirname "$0")/$script" ]]; then
    echo "[OK] bundled script detected: $script"
  else
    echo "[MISSING] bundled script is not executable: $script"
  fi
done

if python3 -c 'import importlib.util, sys; sys.exit(0 if importlib.util.find_spec("playwright") else 1)' >/dev/null 2>&1; then
  echo "[OK] Playwright Python package detected (--browser mode)"
else
  echo "[MISSING] Playwright Python package not found (optional; required for dump-website-js.py --browser)"
  missing_optional+=("playwright")
fi

if command -v playwright >/dev/null 2>&1; then
  echo "[OK] Playwright CLI detected"
elif python3 -m playwright --version >/dev/null 2>&1; then
  echo "[OK] Playwright CLI available through python3 -m playwright"
else
  echo "[MISSING] Playwright CLI not found (optional; useful for browser install/status)"
fi

if command -v google-chrome >/dev/null 2>&1 || command -v chromium >/dev/null 2>&1 || command -v chromium-browser >/dev/null 2>&1; then
  echo "[OK] System Chrome/Chromium detected (fallback for --browser mode)"
else
  echo "[MISSING] System Chrome/Chromium not found (optional if Playwright-managed Chromium is installed)"
fi

echo
for dep in "${missing_optional[@]}"; do
  echo "INSTALL_OPTIONAL:$dep"
done

echo
if [[ ${#missing_optional[@]} -eq 0 ]]; then
  echo "All useful tools detected."
else
  echo "Required dependencies OK. ${#missing_optional[@]} optional tool(s) missing."
fi
