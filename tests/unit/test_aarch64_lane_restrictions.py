"""Declarative by-element register restrictions, including allocator enforcement."""

import shutil
import subprocess
import unittest

from slothy.core.core import SlothyBase
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as arch
from slothy.targets.aarch64 import cortex_a320, cortex_a520, cortex_a55


def parse(source):
    return arch.Instruction.parser(SourceLine(source))[0]


def lane_cases():
    """Mnemonic, family, accumulation, destination/source arrangement, element."""
    for mnemonic, base, accumulates in (
        ("sqrdmulh", arch.Vqdmulh, False),
        ("sqdmulh", arch.Vqdmulh, False),
        ("mul", arch.Vmul, False),
        ("mla", arch.Vmla, True),
        ("mls", arch.Vmla, True),
    ):
        for arrangement in ("4h", "8h", "2s", "4s"):
            yield mnemonic, base, accumulates, arrangement, arrangement, arrangement[-1]
    for op in ("mull", "mlal", "mlsl"):
        for sign in ("u", "s"):
            for upper in ("", "2"):
                for dest, src, element in (
                    ("4s", "8h" if upper else "4h", "h"),
                    ("2d", "4s" if upper else "2s", "s"),
                ):
                    yield (
                        sign + op + upper,
                        arch.Vmull if op == "mull" else arch.Vmlal,
                        op != "mull",
                        dest,
                        src,
                        element,
                    )


def class_name(mnemonic):
    return (
        "v"
        + (mnemonic[1:] if mnemonic in ("sqrdmulh", "sqdmulh") else mnemonic)
        + "_lane"
    )


def boundary_cases():
    for mnemonic, _, _, dest, src, element in lane_cases():
        for lane, accepted in (
            ((15, True), (16, False)) if element == "h" else ((31, True),)
        ):
            yield f"{mnemonic} v0.{dest}, v31.{src}, v{lane}.{element}[0]", accepted


class LaneRestrictionTests(unittest.TestCase):
    def test_parse_and_roundtrip(self):
        specs = {entry["name"] for entry in arch._NEON_SPECS}
        for mnemonic, base, accumulates, dest, src, element in lane_cases():
            for uppercase in (False, True):
                source = f"{mnemonic} v0.{dest}, v31.{src}, v15.{element}[0]"
                if uppercase:
                    source = (
                        f"{mnemonic} v0.{dest.upper()}, v31.{src.upper()}, "
                        f"v15.{element.upper()}[0]"
                    )
                with self.subTest(source=source):
                    inst = parse(source)
                    name = class_name(mnemonic)
                    self.assertIn(name, specs)
                    self.assertIs(type(inst), getattr(arch, name))
                    self.assertIsInstance(inst, base)
                    self.assertEqual(type(inst).__module__, arch.__name__)
                    self.assertIn(type(inst), arch.Instruction.all_subclass_leaves)
                    self.assertEqual(inst.args_in, ["v31", "v15"])
                    self.assertEqual(inst.args_out, [] if accumulates else ["v0"])
                    self.assertEqual(inst.args_in_out, ["v0"] if accumulates else [])
                    expected = [
                        None,
                        [f"v{i}" for i in range(16)] if element == "h" else None,
                    ]
                    self.assertEqual(inst.args_in_restrictions, expected)
                    other = parse(inst.write())
                    self.assertEqual(other.args_in_restrictions, expected)
                    self.assertEqual(other.args_in_out, inst.args_in_out)

    def test_symbolic_lane_operand(self):
        for mnemonic, _, accumulates, dest, src, element in lane_cases():
            index = 7 if element == "h" else 3
            source = (
                f"{mnemonic} v<out>.{dest}, v<input>.{src}, v<lane>.{element}[{index}]"
            )
            with self.subTest(source=source):
                inst = parse(source)
                self.assertEqual(inst.args_in, ["input", "lane"])
                self.assertEqual(inst.args_out, [] if accumulates else ["out"])
                self.assertEqual(inst.args_in_out, ["out"] if accumulates else [])
                self.assertEqual(inst.index, index)
                self.assertEqual(
                    inst.args_in_restrictions,
                    [None, [f"v{i}" for i in range(16)] if element == "h" else None],
                )

    def test_allocator_enforces_boundaries(self):
        for target in (cortex_a320, cortex_a520, cortex_a55):
            for source, accepted in boundary_cases():
                with self.subTest(target=target.__name__, source=source):
                    core = SlothyBase(arch, target)
                    core.config.outputs = {"v0"}
                    core.config.constraints.allow_renaming = False
                    core.config.variable_size = True
                    core.config.constraints.stalls_allowed = 8
                    core.config.selftest = False
                    core.config.timeout = 3
                    self.assertEqual(
                        core.optimize(SourceLine.read_multiline(source)), accepted
                    )

    def test_a520_mul_lane_resources_and_timings(self):
        for arrangement in ("4h", "8h", "2s", "4s"):
            with self.subTest(arrangement=arrangement):
                inst = parse(
                    f"mul v0.{arrangement}, v1.{arrangement}, v15.{arrangement[-1]}[0]"
                )
                self.assertEqual(
                    cortex_a520.get_units(inst),
                    [cortex_a520.ExecutionUnit.VEC0, cortex_a520.ExecutionUnit.VEC1],
                )
                self.assertEqual(cortex_a520.get_inverse_throughput(inst), 1)
                self.assertEqual(cortex_a520.get_latency(inst, 0, inst), 4)

    @unittest.skipUnless(shutil.which("clang-19"), "requires clang-19")
    def test_assembler_agrees_with_boundaries(self):
        for source, accepted in boundary_cases():
            with self.subTest(source=source):
                result = subprocess.run(
                    [
                        "clang-19",
                        "--target=aarch64-none-elf",
                        "-x",
                        "assembler",
                        "-c",
                        "-",
                        "-o",
                        "/dev/null",
                    ],
                    input=source + "\n",
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode == 0, accepted, result.stderr)


if __name__ == "__main__":
    unittest.main()
