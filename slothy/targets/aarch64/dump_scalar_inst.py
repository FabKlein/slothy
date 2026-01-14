#!/usr/bin/env python3
import json
from pathlib import Path

spec = json.loads(
    Path("slothy/targets/aarch64/aarch64_scalar_instructions.json").read_text()
)["instructions"]

# Compute the union of keys that appear anywhere.
all_fields = sorted({k for inst in spec for k in inst.keys()})

print("| " + " | ".join(all_fields) + " |")
print("| " + " | ".join("---" for _ in all_fields) + " |")

for inst in spec:
    row = []
    for field in all_fields:
        val = inst.get(field, "")
        if isinstance(val, (list, dict)):
            val = json.dumps(val, separators=(",", ":"))
        row.append(str(val))
    print("| " + " | ".join(row) + " |")
