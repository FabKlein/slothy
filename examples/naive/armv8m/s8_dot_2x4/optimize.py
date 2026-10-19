"""Schedule the dot-product body, then synthesize byte-count loop control.

Run from the repository root with PYTHONPATH=. venv/bin/python <this file>.
The M55 architecture's built-in loop extractor only handles LE/LETP.
"""

import argparse
import logging
from pathlib import Path

from slothy.core.core import SlothyBase
from slothy.helper import SourceLine
from slothy.targets.arm_v81m import arch_v81m as arch
from slothy.targets.arm_v81m import cortex_m55r1 as target


def schedule(body, pipelined, timeout):
    core = SlothyBase(arch, target)
    config = core.config
    config.inputs_are_outputs = True
    config.selftest = False  # No MVE emulator backend in this architecture module.
    config.variable_size = True
    config.timeout = timeout
    config.constraints.stalls_allowed = 64
    config.constraints.allow_reordering = pipelined
    config.constraints.allow_renaming = pipelined
    # Keep the byte counter and spare GPRs untouched by register allocation.
    # R14 is intentionally available as the eighth accumulator, not a counter.
    config.reserved_regs = {"r7", "r9", "r11", "r13"}
    config.sw_pipelining.enabled = pipelined
    config.sw_pipelining.minimize_overlapping = False
    config.sw_pipelining.allow_post = False
    config.visualize_reordering = False
    # Core API takes the already-unrolled source, unlike optimize_loop().
    source = SourceLine.read_multiline(body * (2 if pipelined else 1))
    if not core.optimize(source):
        raise RuntimeError("No schedule found within the timeout/stall budget")
    return core.result


def synthesize(body, result):
    """Use pairs where profitable; handle short/odd counts with the scalar loop."""
    exceptional = result.num_exceptional_iterations
    step = 32  # Two original iterations, each consuming 16 bytes per row.
    minimum = step * (exceptional + 1)
    parts = [
        "    cmp r7, #16\n    blo done\n",
        f"    cmp r7, #{minimum}\n    blo scalar_tail\n",
        SourceLine.write_multiline(result.preamble) + "\n",
    ]
    if exceptional:
        parts.append(f"    sub r7, r7, #{step * exceptional}\n")
    parts += [
        ".p2align 2\nstart:\n",
        SourceLine.write_multiline(result.code) + "\n",
        f"    subs r7, r7, #{step}\n    cmp r7, #{step}\n    bhs start\n",
        SourceLine.write_multiline(result.postamble) + "\n",
        "    cmp r7, #16\n    blo done\n",
        ".p2align 2\nscalar_tail:\n",
        body,
        "    subs r7, r7, #16\n    cmp r7, #16\n    bhs scalar_tail\ndone:\n",
    ]
    return "".join(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    source = Path(__file__).with_name("s8_dot_2x4_cm55.s").read_text()
    body = source.split("start:\n", 1)[1].split("body_end:\n", 1)[0]
    baseline = schedule(body, False, args.timeout)
    optimized = schedule(body, True, args.timeout)
    header = source.split("start:\n", 1)[0].replace(
        "// Initial count must be >=16 here; count%16 remains on exit. No partial tail.",
        "// Any unsigned count: process full blocks, leave count%16. No partial tail.",
    ).replace("// Scratch q0-q5, NZCV.", "// Scratch q0-q7, NZCV.")
    stats = (
        f"// Original body: {baseline.cycles} estimated cycles per 16-byte block.\n"
        f"// SWP unroll x2: {optimized.cycles} estimated cycles per 32-byte pair "
        f"({optimized.cycles / 2:g} per original block); bound {optimized.cycles_bound}.\n"
        f"// Early instructions: {optimized.num_pre}; exceptional pairs: "
        f"{optimized.num_exceptional_iterations}.\n"
        "// Estimates exclude scalar loop control, setup, drain and tail costs.\n"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(stats + header + synthesize(body, optimized))
    print(stats, end="")
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
