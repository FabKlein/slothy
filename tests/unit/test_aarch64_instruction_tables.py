"""Check generated reference tables and compatibility with the legacy importer."""

import json
import subprocess
import sys
from pathlib import Path
import unittest

from slothy.targets.aarch64.dump_instruction_tables import (
    DIRECTORY,
    KINDS,
    render_table,
)
from slothy.targets.aarch64.load_scalar_table import parse_table
from slothy.targets.aarch64.instruction_templates import expand_instruction_templates


class InstructionTableTests(unittest.TestCase):
    def test_name_is_first_column(self):
        for kind in KINDS:
            with self.subTest(kind=kind):
                header = next(
                    line
                    for line in render_table(kind).splitlines()
                    if line.startswith("|")
                )
                fields = [cell.strip() for cell in header.split("|")[1:-1]]
                self.assertEqual(fields[0], "name")
                self.assertEqual(fields[1:], sorted(set(fields) - {"name"}))

    def test_generated_tables_are_current(self):
        for kind in KINDS:
            with self.subTest(kind=kind):
                table = DIRECTORY / f"aarch64_{kind}_inst.md"
                self.assertEqual(table.read_text(encoding="utf8"), render_table(kind))

    def test_tables_preserve_expanded_specification_fields(self):
        for kind in KINDS:
            with self.subTest(kind=kind):
                source = DIRECTORY / f"aarch64_{kind}_instructions.json"
                entries = expand_instruction_templates(
                    json.loads(source.read_text(encoding="utf8"))
                )
                self.assertEqual(
                    parse_table(DIRECTORY / f"aarch64_{kind}_inst.md"), entries
                )

    def test_placeholders_are_visible_in_markdown(self):
        content = render_table("neon")
        self.assertIn("&lt;Va&gt;", content)
        self.assertNotIn("<Va>", content)
        self.assertIn("Generated file — do not edit", content)

    def test_legacy_scalar_stdout(self):
        result = subprocess.run(
            [sys.executable, "-S", str(DIRECTORY / "dump_scalar_inst.py")],
            cwd=Path(__file__).resolve().parent,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result.stdout, render_table("scalar"))

    def test_standalone_generator_without_site_packages(self):
        subprocess.run(
            [
                sys.executable,
                "-S",
                str(DIRECTORY / "dump_instruction_tables.py"),
                "--check",
            ],
            cwd=Path(__file__).resolve().parent,
            capture_output=True,
            text=True,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
