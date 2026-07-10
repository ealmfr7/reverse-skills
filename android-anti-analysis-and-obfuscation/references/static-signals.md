# Static Signals

Scan manifest, resources, decompiled source, smali, native strings, and package names.

- Root detection: `su`, Magisk, BusyBox, `test-keys`, root paths, mount/property checks.
- Emulator detection: `goldfish`, `ranchu`, `generic`, `sdk_gphone`, `qemu`, VMOS, build props.
- Frida/instrumentation: `frida`, Gum threads, Xposed, Substrate, `/proc/self/maps`.
- Native anti-debug: `ptrace`, `TracerPid`, `prctl`, `seccomp`, syscall checks.
- Certificate pinning: OkHttp `CertificatePinner`, custom `TrustManager`, `pin-sha256`.
- Attestation: Play Integrity, SafetyNet, KeyStore key attestation, keymaster.
- Packing/loaders: `DexClassLoader`, encrypted assets, Jiagu/Bangcle/Legu indicators.
- Obfuscation: reflection dispatch, encrypted strings, sparse xrefs, tiny identifiers.
- Integrity/tamper: signature digest, installer checks, CRC/hash validation.

Treat static matches as leads. Confirm with environment comparisons and runtime evidence.
