#!/usr/bin/env python3
"""Generate the scalar and NEON reference tables from their JSON specifications."""

import argparse
import html
import json
from pathlib import Path

DIRECTORY = Path(__file__).resolve().parent
KINDS = ("scalar", "neon")


def render_table(kind):
    """Render explicit JSON fields, without expanding inherited instruction metadata."""
    source = DIRECTORY / f"aarch64_{kind}_instructions.json"
    instructions = json.loads(source.read_text(encoding="utf8"))["instructions"]
    fields = ["name"] + sorted(
        {key for instruction in instructions for key in instruction} - {"name"}
    )
    lines = [
        f"# AArch64 {kind.upper() if kind == 'neon' else 'scalar'} instruction table",
        "",
        "**Generated file — do not edit.**",
        f"Edit [{source.name}]({source.name}) instead; JSON is the source of truth.",
        "Regenerate both tables from the repository root with:",
        "",
        "```sh",
        "python3 slothy/targets/aarch64/dump_instruction_tables.py",
        "```",
        "",
        "Only explicit JSON fields are shown. Operand fields may inherit from the base;",
        "blank ISA requirements mean unclassified, not baseline-safe.",
        "This is not a complete ISA or CPU timing reference. See",
        "[the specification guide](README.instructions.md) for scope and semantics.",
        "",
        "| " + " | ".join(fields) + " |",
        "| " + " | ".join("---" for _ in fields) + " |",
    ]
    for instruction in instructions:
        row = []
        for field in fields:
            value = instruction.get(field, "")
            if not isinstance(value, str):
                value = json.dumps(value, separators=(",", ":"))
            # Keep placeholders visible and prevent literal pipes from splitting cells.
            row.append(html.escape(value, quote=False).replace("|", "&#124;"))
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for stale tables without writing files",
    )
    args = parser.parse_args()
    stale = []
    for kind in KINDS:
        destination = DIRECTORY / f"aarch64_{kind}_inst.md"
        content = render_table(kind)
        if args.check:
            if (
                not destination.exists()
                or destination.read_text(encoding="utf8") != content
            ):
                stale.append(destination.name)
        else:
            destination.write_text(content, encoding="utf8")
            print(f"Generated {destination.name}")
    if stale:
        parser.exit(1, "Stale generated tables: " + ", ".join(stale) + "\n")


if __name__ == "__main__":
    main()
