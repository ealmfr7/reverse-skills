#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def parse_int(value):
    return int(value, 16 if str(value).lower().startswith("0x") else 10)


def hx(value):
    return f"0x{value:x}"


def main():
    parser = argparse.ArgumentParser(description="Convert Ghidra/IDA entries and Frida module bases into offsets/runtime addresses.")
    parser.add_argument("--image-base", default="0", help="Static image base from Ghidra/IDA")
    parser.add_argument("--entry", help="Static entry address from Ghidra/IDA")
    parser.add_argument("--offset", help="Known module-relative offset")
    parser.add_argument("--module-base", help="Runtime module base from Frida")
    parser.add_argument("--json-out")
    args = parser.parse_args()

    image_base = parse_int(args.image_base)
    if args.offset:
        offset = parse_int(args.offset)
    elif args.entry:
        offset = parse_int(args.entry) - image_base
    else:
        parser.error("provide --entry or --offset")

    result = {"image_base": hx(image_base), "offset": hx(offset)}
    if args.entry:
        result["entry"] = hx(parse_int(args.entry))
    if args.module_base:
        module_base = parse_int(args.module_base)
        result["module_base"] = hx(module_base)
        result["runtime_address"] = hx(module_base + offset)

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"OFFSET:{hx(offset)}")
    if "runtime_address" in result:
        print(f"RUNTIME_ADDRESS:{result['runtime_address']}")
    print(f"FRIDA:const fn = module.base.add({hx(offset)});")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
