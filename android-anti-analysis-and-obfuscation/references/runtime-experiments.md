# Runtime Experiments

Use controlled comparisons to avoid false attribution.

| Run | Device | Root | Frida | Expected Evidence |
|---|---|---|---|---|
| real-clean | real physical | no | no | normal behavior baseline |
| real-frida | real physical | no/root as needed | attach/spawn | instrumentation effect |
| emulator-clean | emulator/VMOS | varies | no | emulator/root effect |
| emulator-frida | emulator/VMOS | varies | attach/spawn | combined effect |

For each run capture `meta.json`, logcat, screenshots/UI XML when behavior differs, attestation/verdict JSON when available, and Frida bridge/probe JSONL if instrumentation is part of the experiment.

Compare one variable at a time before claiming root, emulator, Frida, or attestation detection.

## Minimum Comparison Discipline

- Keep app version constant.
- Keep account state constant where possible.
- Record package installer and signing state.
- Record whether Frida server exists, whether it is running, and whether the app process has Gum/Frida threads.
- Record build fingerprint, security patch, vendor build date, bootloader, verified boot state, and network interface type.
- Preserve exact timestamps so backend/account rate-limit effects can be separated from device effects.

If the app still fails without Frida, Frida may remain a risk signal but is not a sufficient explanation.

If a standalone integrity checker passes while the target app fails, preserve that result as a baseline but continue investigating app-specific attestation and backend policy.
