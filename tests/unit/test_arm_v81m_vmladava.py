"""MVE accumulating dot product: even scalar destination and M55 timing."""

import shutil
import subprocess
import tempfile
from pathlib import Path
import unittest

from slothy.helper import SourceLine
from slothy.targets.arm_v81m import arch_v81m as arch
from slothy.targets.arm_v81m import cortex_m55r1 as target


def parse(text):
    return arch.Instruction.parser(SourceLine(text))[0]


class VmladavaTests(unittest.TestCase):
    def test_dependencies_and_even_registers(self):
        legal = [f"r{i}" for i in range(0, 15, 2)]
        for datatype in ("s8", "u8", "s16", "u16", "s32", "u32"):
            for reg in legal:
                with self.subTest(datatype=datatype, reg=reg):
                    inst = parse(f"vmladava.{datatype} {reg}, q0, q2")
                    self.assertEqual(inst.args_in, ["q0", "q2"])
                    self.assertEqual(inst.args_out, [])
                    self.assertEqual(inst.args_in_out, [reg])
                    self.assertEqual(inst.args_in_out_restrictions[0], legal)
                    self.assertEqual(parse(inst.write()).args_in_out, [reg])

    def test_illegal_accumulators_and_datatypes(self):
        for reg in range(1, 16, 2):
            with self.subTest(reg=reg):
                with self.assertRaises(arch.ParsingException):
                    arch.vmladava.make(f"vmladava.s8 r{reg}, q0, q2")
        for datatype in ("i8", "s64", "f16"):
            with self.assertRaises(arch.ParsingException):
                arch.vmladava.make(f"vmladava.{datatype} r0, q0, q2")

    def test_symbolic_accumulator_restriction(self):
        inst = parse("vmladava.s8 r<acc>, q<row>, q<column>")
        self.assertEqual(inst.args_in_out, ["acc"])
        self.assertEqual(
            inst.args_in_out_restrictions[0], [f"r{i}" for i in range(0, 15, 2)]
        )

    def test_m55_timing(self):
        inst = parse("vmladava.s8 r0, q0, q2")
        self.assertEqual(target.get_units(inst), [target.ExecutionUnit.VEC_MUL])
        self.assertEqual(target.get_inverse_throughput(inst), 2)
        self.assertEqual(target.get_latency(inst, 0, inst), 3)

    @unittest.skipUnless(shutil.which("clang-19"), "Clang 19 required")
    def test_assembler_accepts_even_and_rejects_odd_accumulator(self):
        with tempfile.TemporaryDirectory() as tmp:
            command = [
                "clang-19",
                "--target=arm-none-eabi",
                "-mcpu=cortex-m55",
                "-mfloat-abi=hard",
                "-mthumb",
                "-x",
                "assembler",
                "-c",
                "-",
                "-o",
                str(Path(tmp) / "dot.o"),
            ]
            for reg in range(16):
                with self.subTest(reg=reg):
                    result = subprocess.run(
                        command,
                        input=f".syntax unified\n.thumb\nvmladava.s8 r{reg}, q0, q2\n",
                        text=True,
                        capture_output=True,
                    )
                    self.assertEqual(result.returncode == 0, reg % 2 == 0)


if __name__ == "__main__":
    unittest.main()
