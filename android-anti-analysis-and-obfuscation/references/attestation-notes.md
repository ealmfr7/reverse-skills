# Attestation Notes

Android apps may use Play Integrity, SafetyNet, or KeyStore/keymaster-backed attestation to distinguish trusted devices from emulators, rooted devices, modified OS images, or tampered app installs.

## Evidence To Preserve

- API surface found statically: `IntegrityManager`, `SafetyNet`, `KeyStore`, key generation specs, nonce creation.
- Runtime verdicts or parsed attestation chains when authorized to collect.
- Device properties and build fingerprint for each run.
- Comparison between real physical device and VM/emulator.
- Backend response differences when verdict changes.

Do not assume every login failure is root detection. Attestation failures can be caused by device integrity, app integrity, account risk, backend state, clock/network issues, or missing Google services.
