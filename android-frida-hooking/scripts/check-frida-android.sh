#!/usr/bin/env bash
set -u

missing=0

check_cmd() {
    local name="$1"
    if command -v "$name" >/dev/null 2>&1; then
        printf 'OK:%s:%s\n' "$name" "$(command -v "$name")"
    else
        printf 'INSTALL_REQUIRED:%s\n' "$name"
        missing=1
    fi
}

check_cmd adb
check_cmd frida
check_cmd frida-ps

if command -v frida >/dev/null 2>&1; then
    printf 'INFO:frida_version:%s\n' "$(frida --version 2>/dev/null || true)"
fi

if command -v adb >/dev/null 2>&1; then
    adb_state="$(adb get-state 2>/dev/null || true)"
    if [ "$adb_state" = "device" ]; then
        printf 'OK:adb_device:connected\n'
        printf 'INFO:android_version:%s\n' "$(adb shell getprop ro.build.version.release 2>/dev/null | tr -d '\r')"
        printf 'INFO:device_abi:%s\n' "$(adb shell getprop ro.product.cpu.abi 2>/dev/null | tr -d '\r')"
        if adb shell su -c id >/dev/null 2>&1; then
            printf 'OK:root:su_available\n'
        else
            printf 'WARN:root:su_not_available_or_denied\n'
        fi
    else
        printf 'WARN:adb_device:not_connected\n'
    fi
fi

if [ "$missing" -ne 0 ]; then
    exit 1
fi
