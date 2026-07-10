#!/usr/bin/env bash
set -u

apk="${1:-}"
if [ -z "$apk" ] || [ ! -f "$apk" ]; then
    echo "Usage: $0 app.apk" >&2
    exit 2
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

printf 'APK=%s\n' "$apk"
if command -v sha256sum >/dev/null 2>&1; then
    printf 'SHA256=%s\n' "$(sha256sum "$apk" | awk '{print $1}')"
elif command -v shasum >/dev/null 2>&1; then
    printf 'SHA256=%s\n' "$(shasum -a 256 "$apk" | awk '{print $1}')"
fi

if command -v aapt >/dev/null 2>&1; then
    badging="$(aapt dump badging "$apk" 2>/dev/null || true)"
    package="$(printf '%s\n' "$badging" | sed -n "s/^package: name='\([^']*\)'.*/\1/p" | head -1)"
    launchable="$(printf '%s\n' "$badging" | sed -n "s/^launchable-activity: name='\([^']*\)'.*/\1/p" | head -1)"
    [ -n "$package" ] && printf 'PACKAGE=%s\n' "$package"
    [ -n "$launchable" ] && printf 'LAUNCHABLE_ACTIVITY=%s\n' "$launchable"
else
    printf 'WARN=aapt_missing_package_manifest_summary_unavailable\n'
fi

unzip -Z1 "$apk" > "$tmp/files.txt" 2>/dev/null || {
    echo "ERROR=not_a_readable_apk_zip" >&2
    exit 1
}

printf 'DEX_COUNT=%s\n' "$(grep -Ec '^classes[0-9]*\.dex$' "$tmp/files.txt" 2>/dev/null || true)"
printf 'NATIVE_LIB_COUNT=%s\n' "$(grep -Ec '^lib/[^/]+/.*\.so$' "$tmp/files.txt" 2>/dev/null || true)"

detect_file() {
    local key="$1"
    local pattern="$2"
    if grep -Eq "$pattern" "$tmp/files.txt"; then
        printf '%s=yes\n' "$key"
    else
        printf '%s=no\n' "$key"
    fi
}

detect_file HAS_FLUTTER '(^lib/[^/]+/libflutter\.so$|^lib/[^/]+/libapp\.so$|flutter_assets/)'
detect_file HAS_REACT_NATIVE '(index\.android\.bundle$|\.hbc$|libhermes\.so$|assets/.*/.*bundle)'
detect_file HAS_CORDOVA '(assets/www/|cordova\.js|capacitor\.config)'
detect_file HAS_XAMARIN '(libmonodroid\.so|assemblies/|\.dll$)'
detect_file HAS_UNITY '(libil2cpp\.so|global-metadata\.dat|UnityPlayerActivity)'
detect_file HAS_NATIVE_LIBS '^lib/[^/]+/.*\.so$'

unzip -p "$apk" '*.dex' 2>/dev/null | strings > "$tmp/dex_strings.txt" || true
unzip -p "$apk" 'lib/*/*.so' 2>/dev/null | strings > "$tmp/native_strings.txt" || true
cat "$tmp/dex_strings.txt" "$tmp/native_strings.txt" > "$tmp/all_strings.txt"

detect_string() {
    local key="$1"
    local pattern="$2"
    if grep -Eqi "$pattern" "$tmp/all_strings.txt"; then
        printf '%s=yes\n' "$key"
    else
        printf '%s=no\n' "$key"
    fi
}

detect_string USES_OKHTTP 'okhttp3|okhttp/'
detect_string USES_RETROFIT 'retrofit2|retrofit/'
detect_string USES_WEBVIEW 'android/webkit/WebView|addJavascriptInterface'
detect_string USES_CRYPTO 'javax/crypto|MessageDigest|SecretKeySpec|Cipher\.getInstance'
detect_string USES_DYNAMIC_DEX 'DexClassLoader|PathClassLoader|InMemoryDexClassLoader|loadDex|openDexFile'
detect_string USES_SYSTEM_LOADLIBRARY 'System\.loadLibrary|loadLibrary'
detect_string MALWARE_SIGNAL 'AccessibilityService|DeviceAdminReceiver|BOOT_COMPLETED|SEND_SMS|READ_SMS|SYSTEM_ALERT_WINDOW|REQUEST_INSTALL_PACKAGES'
detect_string NATIVE_JNI_SIGNAL 'RegisterNatives|JNI_OnLoad|Java_'

echo 'TOP_NATIVE_LIBS='
grep -E '^lib/[^/]+/.*\.so$' "$tmp/files.txt" | sed -n '1,30p'

echo 'TOP_URL_STRINGS='
grep -Eio 'https?://[^[:space:]")<>]+' "$tmp/all_strings.txt" | sort -u | sed -n '1,30p'
