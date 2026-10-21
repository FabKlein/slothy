"""Stable parser/model observations used by the JSON migration regression test."""

import re

from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as arch
from slothy.targets.aarch64 import cortex_a55, cortex_a520


def observe(text, targets=None):
    inst = arch.Instruction.parser(SourceLine(text))[0]
    fields = (
        "args_in",
        "args_out",
        "args_in_out",
        "datatype",
        "immediate",
        "index",
        "addr",
        "increment",
        "pre_index",
        "args_in_restrictions",
        "args_out_restrictions",
        "args_in_out_restrictions",
        "args_in_combinations",
        "args_out_combinations",
        "args_in_out_combinations",
    )
    result = {key: getattr(inst, key) for key in fields}
    result["class"] = type(inst).__name__
    result["bases"] = [c.__name__ for c in type(inst).__mro__[1:-1]]
    result["write"] = inst.write()
    result["roundtrip_class"] = type(
        arch.Instruction.parser(SourceLine(inst.write()))[0]
    ).__name__
    for target in targets if targets is not None else (cortex_a55, cortex_a520):
        values = []
        for query in (
            target.get_units,
            target.get_inverse_throughput,
            lambda i: target.get_latency(i, 0, i),
        ):
            try:
                # Latency queries can return constraint callbacks. Their memory
                # addresses vary between processes; retain their qualified names.
                values.append(re.sub(r" at 0x[0-9a-f]+", "", str(query(inst))))
            except Exception as exc:
                values.append(f"{type(exc).__name__}: {exc}")
        result[target.__name__.rsplit(".", 1)[1]] = values
    return result
