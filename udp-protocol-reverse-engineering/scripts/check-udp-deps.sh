#!/usr/bin/env bash
set -u

for tool in tcpdump tshark python3 adb frida; do
    if command -v "$tool" >/dev/null 2>&1; then
        printf 'OK:%s:%s\n' "$tool" "$(command -v "$tool")"
    else
        printf 'INSTALL_OPTIONAL:%s\n' "$tool"
    fi
done

python3 - <<'PY'
try:
    import scapy  # noqa: F401
    print("OK:python_scapy")
except Exception:
    print("INSTALL_OPTIONAL:python_scapy")
PY
