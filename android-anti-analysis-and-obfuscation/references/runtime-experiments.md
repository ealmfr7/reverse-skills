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
