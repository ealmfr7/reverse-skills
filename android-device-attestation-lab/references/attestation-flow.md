# Attestation Flow Notes

## Evidence Classes

| Evidence | Meaning | Common mistake |
|---|---|---|
| app requests Play Integrity/SafetyNet | The app asks Google/device services for an integrity verdict. | Treating the request alone as proof of rejection. |
| KeyStore attestation cert chain exists | A key has attestation metadata and a certificate chain. | Assuming chain existence equals backend acceptance. |
| challenge matches backend nonce | The report is bound to a run/challenge. | Comparing stale or synthetic challenges. |
| app signature digest matches expected | Attestation is bound to the expected app identity. | Testing a repackaged APK without recording this difference. |
| exact Google root match | Stronger root trust evidence. | Accepting SPKI match as identical certificate without noting the distinction. |
| key signs challenge | The private key is usable. | Calling this backend trust; backend policy may still fail. |

## Interpretation Rules

- Compare against a known-good physical-device baseline first.
- Keep root certificate exact match and SPKI match separate.
- Record whether revocation status was checked, skipped, unavailable, or failed.
- Separate device environment evidence from server-side policy inference.
- Mark each claim as observed, inferred, or unverified.
- If VMOS/emulator fails but physical passes, compare environment, attestation,
  root certificate, app binding, and backend response independently.
