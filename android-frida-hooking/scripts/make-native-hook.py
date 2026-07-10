#!/usr/bin/env python3
import argparse
from pathlib import Path


DLOPEN_HELPER = r'''function hookModuleLoad(moduleName, callback) {
    const dlopen = Module.findGlobalExportByName("android_dlopen_ext")
        || Module.findGlobalExportByName("dlopen");
    if (!dlopen) throw new Error("dlopen/android_dlopen_ext not found");
    const hooked = new Set();
    Interceptor.attach(dlopen, {
        onEnter(args) {
            this.path = args[0].isNull() ? null : args[0].readCString();
            this.shouldHook = this.path && this.path.indexOf(moduleName) !== -1;
        },
        onLeave(retval) {
            if (!this.shouldHook || retval.isNull()) return;
            const mod = Process.findModuleByName(moduleName);
            if (!mod) return;
            const key = mod.base.toString();
            if (hooked.has(key)) return;
            hooked.add(key);
            callback(mod);
        }
    });
}

function hookNowOrOnLoad(moduleName, callback) {
    const mod = Process.findModuleByName(moduleName);
    if (mod) {
        callback(mod);
        return;
    }
    hookModuleLoad(moduleName, callback);
}
'''


def generate(module_name: str, export=None, offset=None, wait_load=False):
    if not export and not offset:
        raise ValueError("provide --export or --offset")
    target_expr = f'mod.getExportByName("{export}")' if export else f"mod.base.add({offset})"
    body = f'''function installHooks(mod) {{
    console.log("[+] Module ready:", mod.name, mod.base);
    const target = {target_expr};
    Interceptor.attach(target, {{
        onEnter(args) {{
            console.log("[+] native target called:", target);
            console.log("    arg0:", args[0]);
            console.log("    arg1:", args[1]);
            console.log("    arg2:", args[2]);
        }},
        onLeave(retval) {{
            console.log("    ret:", retval);
        }}
    }});
}}
'''
    if wait_load:
        return (
            "// Generated native hook. Review module/export/offset before use.\n"
            + DLOPEN_HELPER
            + "\n"
            + body
            + f'\nhookNowOrOnLoad("{module_name}", installHooks);\n'
        )
    return f'''// Generated native hook. Review module/export/offset before use.
const mod = Process.getModuleByName("{module_name}");
{body}
installHooks(mod);
'''


def main():
    parser = argparse.ArgumentParser(description="Generate a Frida native export/offset hook.")
    parser.add_argument("module_name")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--export")
    group.add_argument("--offset", help="Offset expression, e.g. 0x1234")
    parser.add_argument("--wait-load", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args()

    js = generate(args.module_name, args.export, args.offset, args.wait_load)
    if args.out:
        Path(args.out).write_text(js, encoding="utf-8")
    else:
        print(js)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
