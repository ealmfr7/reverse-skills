#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from common import slugify


FRIDA_COMMON = r"""'use strict';

const SOURCE = '__SOURCE__';
const startedAt = Date.now();

function ts() {
  return Date.now() / 1000;
}

function tid() {
  try { return Process.getCurrentThreadId(); } catch (_) { return null; }
}

function safeString(value) {
  try {
    if (value === null || value === undefined) return String(value);
    const text = String(value);
    if (/token|cookie|signature|secret|authorization/i.test(text)) return '<redacted>';
    if (text.indexOf('://') !== -1) return '<url-redacted>';
    if (text.indexOf('/data/') === 0 || text.indexOf('/storage/') === 0 || text.indexOf('/sdcard/') === 0) return '<path-redacted>';
    return text.length > 160 ? text.slice(0, 160) + '...' : text;
  } catch (_) {
    return '<toString failed>';
  }
}

function emit(type, event, data) {
  send({
    schema: 1,
    type: type,
    event: event,
    ts: ts(),
    monoMs: Date.now() - startedAt,
    pid: Process.id,
    tid: tid(),
    source: SOURCE,
    data: data || {},
  });
}

function status(event, data) { emit('status', event, data); }
function event(eventName, data) { emit('event', eventName, data); }
"""


JAVA_TEMPLATE = FRIDA_COMMON + r"""
Java.perform(function () {
  status('probe.start', { runtime: Script.runtime, arch: Process.arch });

  // Replace this with target-specific Java.use hooks.
  try {
    const ActivityThread = Java.use('android.app.ActivityThread');
    const currentProcessName = ActivityThread.currentProcessName();
    event('java.process', { processName: safeString(currentProcessName) });
  } catch (e) {
    status('hook.skipped', { hook: 'ActivityThread.currentProcessName', reason: safeString(e) });
  }
});
"""


NATIVE_TEMPLATE = FRIDA_COMMON + r"""
status('probe.start', { runtime: Script.runtime, arch: Process.arch });

// Replace this with target-specific Module.findExportByName or offset hooks.
Process.enumerateModules()
  .filter(function (module) { return module.name.indexOf('.so') !== -1; })
  .slice(0, 20)
  .forEach(function (module) {
    event('native.module', { name: safeString(module.name), base: module.base.toString(), size: module.size });
  });
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a standardized Frida probe scaffold.")
    parser.add_argument("runtime", choices=["frida"])
    parser.add_argument("kind", choices=["java", "native"])
    parser.add_argument("name")
    parser.add_argument("--out", type=Path, default=Path("probes"))
    parser.add_argument("--source", default="")
    args = parser.parse_args()

    name = slugify(args.name)
    source = args.source or f"frida.{name}"
    body = JAVA_TEMPLATE if args.kind == "java" else NATIVE_TEMPLATE
    body = body.replace("__SOURCE__", source)
    path = args.out / "frida" / f"{name}.js"
    if path.exists():
        print(f"ERROR: probe already exists: {path}", file=sys.stderr)
        return 1
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    print(f"PROBE_CREATED:{path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
