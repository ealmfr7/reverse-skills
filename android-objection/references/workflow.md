# Objection Workflow

## Good Uses

- quick app storage exploration
- quick class/method discovery
- fast runtime checks before writing Frida JS
- testing whether a Frida environment works

## Boundaries

Objection is convenient but less reproducible than a committed Frida script.
When a finding matters, write the exact command, app state, and follow-up Frida
script or static evidence.

## Troubleshooting

- If Objection cannot attach, debug Frida first with `frida-ps -U`.
- If commands fail after spawn, attach to an already-running process.
- If class inspection is incomplete, the target code may use another ClassLoader
  or may not be loaded yet.
