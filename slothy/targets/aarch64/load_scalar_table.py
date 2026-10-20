#!/usr/bin/env python3
import argparse
import csv
import html
import json
from pathlib import Path


def _normalize_row(row):
    row = [cell.strip() for cell in row]
    if row and row[0] == "":
        row = row[1:]
    if row and row[-1] == "":
        row = row[:-1]
    return row


def parse_table(table_path: Path):
    with table_path.open(encoding="utf8") as f:
        reader = csv.reader(
            (line for line in f if line.lstrip().startswith("|")), delimiter="|"
        )
        raw_rows = [_normalize_row(row) for row in reader]

    raw_rows = [row for row in raw_rows if any(cell for cell in row)]
    if len(raw_rows) < 2:
        raise ValueError(f"{table_path} does not look like a Markdown table")

    header = raw_rows[0]
    body = raw_rows[2:]

    instructions = []
    for row in body:
        inst = {}
        for key, value in zip(header, row):
            if value == "":
                continue
            value = html.unescape(value)
            try:
                inst[key] = json.loads(value)
            except json.JSONDecodeError:
                inst[key] = value
        instructions.append(inst)
    return instructions


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown table of scalar instructions back to JSON spec."
    )
    parser.add_argument(
        "--table",
        "-t",
        default="slothy/targets/aarch64/aarch64_scalar_inst.md",
        help="Input Markdown/pipe table file",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="slothy/targets/aarch64/aarch64_scalar_instructions.json",
        help="Destination JSON file",
    )
    args = parser.parse_args()

    table_path = Path(args.table)
    json_path = Path(args.output)

    instructions = parse_table(table_path)
    json_path.write_text(
        json.dumps({"instructions": instructions}, indent=2) + "\n", encoding="utf8"
    )
    print(f"Wrote {len(instructions)} entries to {json_path}")


if __name__ == "__main__":
    main()
