#!/usr/bin/env python3
"""Legacy stdout entry point; use dump_instruction_tables.py to update both tables."""

if __package__:
    from .dump_instruction_tables import render_table
else:
    from dump_instruction_tables import render_table


if __name__ == "__main__":
    print(render_table("scalar"), end="")
