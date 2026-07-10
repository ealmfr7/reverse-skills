# Attestation Notes

Android apps may use Play Integrity, SafetyNet, or KeyStore/keymaster-backed attestation to distinguish trusted devices from emulators, rooted devices, modified OS images, or tampered app installs.

## Core Principles

- A standalone Play Integrity checker result is a baseline, not proof that a target app backend will trust the device.
- App/backend trust can combine Google verdicts, app-specific attestation, device profile coherence, account risk, request telemetry, and server-side history.
- Separate key possession from backend trust. A key can sign a fresh challenge while its attestation chain, certificate validity, root, claims, or backend policy still fail.
- Do not attribute a block to Frida unless a no-Frida baseline succeeds under otherwise similar conditions.
- Do not attribute a block to root unless a non-root baseline succeeds under otherwise similar conditions.
- Treat generic login/risk messages as ambiguous until the failing stage is known.

## Evidence To Preserve

- API surface found statically: `IntegrityManager`, `SafetyNet`, `KeyStore`, key generation specs, nonce creation.
- Runtime verdicts or parsed attestation chains when authorized to collect.
- Device properties and build fingerprint for each run.
- Comparison between real physical device and VM/emulator.
- Backend response differences when verdict changes.
- Package state, installer, signing info, version, and install source.
- UI state, screenshots, and logcat around the failure.
- Any app-specific attestation headers or request annotations discovered statically.

## Interpretation Checklist

When an app behaves differently across devices, classify each claim:

- `observed`: directly supported by artifact paths.
- `inferred`: likely explanation, but no direct app/backend verdict.
- `unverified`: plausible, needs a controlled run.

Ask:

- Did the same account/app version work on another environment?
- Did the failing environment pass a standalone integrity checker?
- Did the target app request additional attestation beyond Play Integrity?
- Did failure happen before login submit, during attestation, during API submit, or during response processing?
- Are build fingerprint, vendor patch level, bootloader, network type, and cloud/container properties coherent?

Do not assume every login failure is root detection. Attestation failures can be caused by device integrity, app integrity, account risk, backend state, clock/network issues, or missing Google services.
