# Android API Lab Workflow

Use this workflow for an authorized test APK where the goal is to understand API
traffic and reproduce a small client request.

## Goal

Map login/API behavior from APK to traffic to repeatable request documentation.

## Flow

1. Route the APK:
   ```bash
   bash android-reversing-workflow/scripts/fingerprint-apk.sh lab.apk > fingerprint.txt
   python3 android-reversing-workflow/scripts/route-android-task.py --fingerprint fingerprint.txt
   ```
2. Static first pass:
   ```text
   Use android-reverse-engineering to inspect Manifest, BuildConfig, network packages, Retrofit/OkHttp interfaces.
   ```
3. Capture traffic:
   ```bash
   bash android-traffic-analysis/scripts/set-android-proxy.sh 10.0.2.2 8080
   python3 android-traffic-analysis/scripts/summarize-traffic.py capture.har --json-out traffic-summary.json
   bash android-traffic-analysis/scripts/clear-android-proxy.sh
   ```
4. If traffic is hidden or signed, generate hooks:
   ```bash
   python3 android-frida-hooking/scripts/make-java-hook.py com.example.AuthManager login --out login-hook.js
   ```
5. Document:
   - endpoint inventory
   - auth/session flow
   - request signing inputs
   - observed vs inferred behavior
   - minimal curl/client reproduction if authorized

## Validation

- Proxy capture shows expected request, or Frida hook fires on the target action.
- Report contains no raw secrets.
- Every conclusion is marked observed, inferred, or unverified.
