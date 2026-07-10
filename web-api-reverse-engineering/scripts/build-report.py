#!/usr/bin/env python3
"""Build a Markdown report from web/API reverse-engineering artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_json(path: str | None) -> dict:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    return json.loads(p.read_text(encoding="utf-8"))


def bullet_list(values: list[str]) -> list[str]:
    return [f"- {value}" for value in values] if values else ["- None detected."]


def build_report(fingerprint: dict, endpoints: dict, har: dict, graphql: dict) -> str:
    lines = ["# Web API Reverse Engineering Report", ""]
    target = fingerprint.get("final_url") or fingerprint.get("url") or har.get("har") or endpoints.get("root") or graphql.get("root") or "Unknown"
    lines.extend([f"Target: `{target}`", ""])

    lines.extend(["## Technology Fingerprint", ""])
    lines.append(f"Recommended strategy: `{fingerprint.get('recommended_strategy', 'unknown')}`")
    lines.append("")
    lines.append("Technologies:")
    lines.extend(bullet_list(fingerprint.get("technologies", [])))
    lines.append("")
    lines.append("API styles:")
    lines.extend(bullet_list(fingerprint.get("api_styles", [])))
    lines.append("")
    lines.append("Protection/friction signals:")
    lines.extend(bullet_list(fingerprint.get("protections", [])))
    lines.append("")

    endpoint_items = endpoints.get("endpoints") or har.get("endpoints") or []
    lines.extend(["## Endpoint Inventory", ""])
    if endpoint_items:
        lines.append("| Method | Host | Path | Sources/Count |")
        lines.append("|---|---|---|---|")
        for item in endpoint_items[:200]:
            method = item.get("method", "?")
            host = item.get("host", "-")
            path = item.get("path", item.get("url", "-"))
            source = ", ".join(item.get("sources", [])) if item.get("sources") else str(item.get("count", "-"))
            lines.append(f"| `{method}` | `{host}` | `{path}` | {source} |")
    else:
        lines.append("No endpoints detected.")
    lines.append("")

    graphql_ops = graphql.get("operations") or har.get("graphql_operations") or endpoints.get("graphql_operations") or []
    lines.extend(["## GraphQL", ""])
    if graphql.get("endpoint_candidates"):
        lines.append("Endpoint candidates:")
        for endpoint in graphql["endpoint_candidates"]:
            lines.append(f"- `{endpoint}`")
        lines.append("")
    if graphql_ops:
        lines.append("Operations:")
        for op in graphql_ops[:200]:
            kind = op.get("kind", "?")
            name = op.get("name", "?")
            lines.append(f"- `{kind} {name}`")
    else:
        lines.append("No GraphQL operations detected.")
    lines.append("")

    lines.extend(["## Recommended Next Steps", ""])
    commands = fingerprint.get("recommended_commands", [])
    if commands:
        lines.append("```bash")
        lines.extend(commands)
        lines.append("```")
    else:
        lines.extend(
            [
                "- Capture a HAR for authenticated or interaction-dependent flows.",
                "- Run `extract-endpoints.py` on downloaded bundles.",
                "- Reproduce one low-risk request with curl before generating client code.",
            ]
        )
    lines.append("")

    lines.extend(["## Limitations", ""])
    lines.extend(
        [
            "- Treat all conclusions as observed or inferred from supplied artifacts.",
            "- Do not use captured secrets or personal tokens in generated clients.",
            "- For protected or bot-friction flows, prefer official API access or authorized browser captures.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fingerprint", help="fingerprint-web.py JSON")
    parser.add_argument("--endpoints", help="extract-endpoints.py JSON")
    parser.add_argument("--har", help="har-summary.py JSON")
    parser.add_argument("--graphql", help="analyze-graphql.py JSON")
    parser.add_argument("--out", required=True, help="Markdown report output path")
    args = parser.parse_args()
    try:
        report = build_report(
            load_json(args.fingerprint),
            load_json(args.endpoints),
            load_json(args.har),
            load_json(args.graphql),
        )
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    Path(args.out).write_text(report, encoding="utf-8")
    print(f"Wrote report: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
