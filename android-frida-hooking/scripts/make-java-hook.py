#!/usr/bin/env python3
import argparse
from pathlib import Path


def quoted_types(overload: str):
    return [item.strip() for item in overload.split(",") if item.strip()]


def method_expr(method: str) -> str:
    if method == "$init" or method.isidentifier():
        return f"Target.{method}"
    return f'Target["{method}"]'


def generate(class_name: str, method: str, overload=None, stacktrace=False):
    target = method_expr(method)
    if overload:
        args = ", ".join(f'"{item}"' for item in quoted_types(overload))
        hook_target = f"{target}.overload({args})"
        call_target = "overload"
    else:
        hook_target = target
        call_target = target

    stacktrace_block = ""
    if stacktrace:
        stacktrace_block = """
            const Exception = Java.use("java.lang.Exception");
            const Log = Java.use("android.util.Log");
            console.log(Log.getStackTraceString(Exception.$new()));
"""

    call_line = (
        "const ret = overload.apply(this, arguments);"
        if overload
        else f"const ret = {call_target}.apply(this, arguments);"
    )

    return f'''// Generated Java hook. Review target class and overload before use.
if (Java.available) {{
    Java.perform(function () {{
        const Target = Java.use("{class_name}");
        const overload = {hook_target};

        overload.implementation = function () {{
            console.log("[+] {class_name}.{method} called");
            for (let i = 0; i < arguments.length; i++) {{
                console.log("    arg" + i + ":", arguments[i]);
            }}
{stacktrace_block}
            {call_line}
            console.log("    ret:", ret);
            return ret;
        }};

        console.log("[+] Hook installed: {class_name}.{method}");
    }});
}}
'''


def main():
    parser = argparse.ArgumentParser(description="Generate a Frida Java/Kotlin method hook.")
    parser.add_argument("class_name")
    parser.add_argument("method")
    parser.add_argument("--overload", help='Comma-separated Java types, e.g. "java.lang.String,int"')
    parser.add_argument("--stacktrace", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args()

    js = generate(args.class_name, args.method, args.overload, args.stacktrace)
    if args.out:
        Path(args.out).write_text(js, encoding="utf-8")
    else:
        print(js)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
