# Folder Layout

Each investigation lives in `cases/<case-id>/`.

```text
case.yaml                 Canonical metadata and scope.
README.md                 Short human summary of goal and current state.
timeline.md               Dated actions, decisions, and notable discoveries.
inputs/apks/              Original APK/XAPK/AAB/JAR/AAR inputs.
inputs/urls/              Seed URLs, endpoint lists, documentation links.
inputs/accounts/          Account descriptors, never raw passwords or tokens.
inputs/devices/           Device/emulator profiles and setup notes.
artifacts/decompiled/     Decompiled source exports and selected snippets.
artifacts/frida/          Frida scripts and captured hook output.
artifacts/pcaps/          PCAP/PCAPNG traffic captures.
artifacts/screenshots/    UI screenshots and visual evidence.
artifacts/logs/           logcat, console, server, and tool logs.
artifacts/ghidra/         Ghidra exports, scripts, and project notes.
artifacts/jadx/           JADX outputs and analysis notes.
artifacts/web/            HAR files, JS bundles, API clients, replay notes.
runs/                     Numbered experiments with commands and observations.
                          Attestation cases may use physical-attestation-baseline,
                          vmos-attestation-compare, and frida-attestation-observation.
notes/hypotheses.md       Things believed but not proven.
notes/findings.md         Proven facts with artifact references.
notes/unknowns.md         Questions, blockers, and follow-up targets.
reports/                  Evidence indexes, final reports, summaries.
scripts/                  Case-specific helpers safe to run in this case only.
```

Prefer copying important files with `scripts/add-artifact.py` so metadata is logged. For very large artifacts, add a small manifest or note that points to external storage and records hash, size, origin, and retention rules.
