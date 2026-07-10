#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path


def parse_int(value):
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value, 16 if value.lower().startswith("0x") else 10)
    raise ValueError(f"cannot parse integer value: {value!r}")


def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_$]", "_", name)


def function_offset(item, image_base):
    if "offset" in item:
        return parse_int(item["offset"])
    if "entry" in item:
        return parse_int(item["entry"]) - image_base
    raise ValueError(f"function lacks offset or entry: {item}")


def generate(data):
    module = data.get("module") or "libtarget.so"
    image_base = parse_int(data.get("image_base", 0))
    functions = data.get("functions", [])
    lines = [
        "// Generated from Ghidra function export. Review offsets before use.",
        f'const moduleName = "{module}";',
        f'const mod = Process.getModuleByName("{module}");',
        "const base = mod.base;",
        "",
    ]
    for item in functions:
        name = item.get("name") or item.get("label") or "unnamed"
        offset = function_offset(item, image_base)
        ident = safe_name(name)
        lines.extend(
            [
                f"// {name}",
                f"const fn_{ident} = base.add(0x{offset:x});",
                f"Interceptor.attach(fn_{ident}, {{",
                "    onEnter(args) {",
                f'        console.log("[+] {name} called @", fn_{ident});',
                "        console.log('    arg0:', args[0]);",
                "        console.log('    arg1:', args[1]);",
                "    },",
                "    onLeave(retval) {",
                "        console.log('    ret:', retval);",
                "    }",
                "});",
                "",
            ]
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate Frida native offset hook templates from Ghidra JSON.")
    parser.add_argument("functions_json", help="JSON exported by Ghidra script")
    parser.add_argument("--out", help="Output hook.js")
    args = parser.parse_args()

    try:
        data = json.loads(Path(args.functions_json).read_text(encoding="utf-8"))
        js = generate(data)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.out:
        Path(args.out).write_text(js + "\n", encoding="utf-8")
    else:
        print(js)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
