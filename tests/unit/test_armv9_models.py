"""A320/A520 coverage derived from their own guides, plus model regressions."""

from itertools import combinations
from types import SimpleNamespace
import shutil
import subprocess
import tempfile
from pathlib import Path
import unittest

from ortools.sat.python import cp_model
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM
from unicorn import arm64_const as registers
from unicorn.arm64_const import UC_ARM64_REG_Q0, UC_ARM64_REG_Q1, UC_ARM64_REG_X2

from slothy.core.core import SlothyBase
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as arch
from slothy.targets.aarch64 import cortex_a320, cortex_a520, cortex_a55


def parse(text):
    return arch.Instruction.parser(SourceLine(text))[0]


SCALAR = (
    "cmp x0, xzr",
    "csel x0, x1, x2, eq",
    "csel x0, x1, xzr, ne",
    "asr x0, x1, #3",
    "asr x0, x1, x2",
    "lsr x0, x1, x2",
    "sxtb x0, w1",
    "uxtb w0, w1",
    "mov x0, x1",
    "movk x0, #1, lsl #16",
)
CRC = tuple(
    f"{name} w0, w1, {'x2' if name.endswith('x') else 'w2'}"
    for name in (
        "crc32b",
        "crc32h",
        "crc32w",
        "crc32x",
        "crc32cb",
        "crc32ch",
        "crc32cw",
        "crc32cx",
    )
)
# Source, A320 (resource duration, latency), A520 (duration, latency).
CASES = (
    ("ld1 {v0.4s, v1.4s}, [x0]", (2, 4), (1, 3)),
    ("ld1 {v0.2s, v1.2s}, [x0]", (1, 3), (1, 3)),
    ("st1 {v0.4s, v1.4s, v2.4s, v3.4s}, [x0], #64", (4, 1), (4, 1)),
    ("st1 {v0.2s, v1.2s, v2.2s, v3.2s}, [x0], #32", (2, 1), (2, 1)),
    ("ld2 {v0.s, v1.s}[1], [x2]", (6, 4), (2, 4)),
    ("ld2 {v0.s, v1.s}[1], [x2], #8", (6, 4), (2, 4)),
    ("ushl v0.4s, v1.4s, v2.4s", (1, 3), (1, 3)),
    ("ushl v0.2s, v1.2s, v2.2s", (1, 3), (1, 3)),
    ("tbl v0.16b, {v1.16b, v2.16b}, v3.16b", (2, 5), (5, 8)),
    ("tbl v0.8b, {v1.16b, v2.16b}, v3.8b", (2, 5), (5, 8)),
    ("fmov x0, d1", (1, 3), (1, 3)),
    ("dup v0.4s, w1", (1, 3), (1, 3)),
    ("mov v0.s[0], w1", (1, 3), (1, 3)),
    ("mov v0.d[1], v1.d[0]", (1, 3), (1, 4)),
    ("ldp w0, w1, [x2]", (1, 4), (1, 2)),
    ("ldp w0, w1, [x2, #8]", (1, 4), (1, 2)),
    ("stp w0, w1, [x2]", (1, 1), (1, 1)),
    ("stp w0, w1, [x2, #8]", (1, 1), (1, 1)),
    ("ldp q0, q1, [x2, #32]", (2, 3), (1, 3)),
    ("ldp q0, q1, [x2], #32", (2, 3), (1, 3)),
    ("ldr x0, [sp, #16]", (1, 4), (1, 4)),
    ("str x0, [sp, #16]", (1, 4), (1, 4)),
    ("uxtl v0.8h, v1.8b", (1, 2), (1, 2)),
    ("fmov d0, x1", (1, 3), (1, 3)),
    ("fmov s0, w1", (1, 3), (1, 3)),
    ("fmov w0, s1", (1, 3), (1, 3)),
    ("fadd d0, d1, d2", (1, 4), (1, 4)),
    ("adds x0, x1, #1", (1, 1), (1, 1)),
    ("add w0, w1, #1", (1, 1), (1, 1)),
    ("mul x0, x1, x2", (2, 4), (2, 4)),
)


class Armv9ModelTests(unittest.TestCase):
    @unittest.skipUnless(
        shutil.which("clang-19") and shutil.which("llvm-objcopy-19"),
        "Requires AArch64-capable Clang and llvm-objcopy",
    )
    def test_scalar_transfer_execution(self):
        source = [
            "fmov s0, w0",
            "fmov w1, s0",
            "fmov d2, x2",
            "fadd d2, d2, d3",
            "fmov x3, d2",
        ]
        with tempfile.TemporaryDirectory() as temp:
            assembly = Path(temp) / "transfers.s"
            obj = Path(temp) / "transfers.o"
            binary = Path(temp) / "transfers.bin"
            assembly.write_text(".text\n" + "\n".join(parse(s).write() for s in source))
            subprocess.run(
                [
                    "clang-19",
                    "--target=aarch64-none-elf",
                    "-c",
                    str(assembly),
                    "-o",
                    str(obj),
                ],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                [
                    "llvm-objcopy-19",
                    "-O",
                    "binary",
                    "--only-section=.text",
                    str(obj),
                    str(binary),
                ],
                check=True,
                capture_output=True,
            )
            code = binary.read_bytes()
        uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
        uc.mem_map(0x1000, 0x1000)
        uc.mem_write(0x1000, code)
        uc.reg_write(registers.UC_ARM64_REG_X0, 0xFFFFFFFF3F800000)
        uc.reg_write(registers.UC_ARM64_REG_Q0, (1 << 128) - 1)
        uc.reg_write(registers.UC_ARM64_REG_X2, 0x3FF0000000000000)  # 1.0
        uc.reg_write(registers.UC_ARM64_REG_Q3, 0x4000000000000000)  # 2.0
        uc.emu_start(0x1000, 0x1000 + len(code))
        self.assertEqual(uc.reg_read(registers.UC_ARM64_REG_Q0), 0x3F800000)
        self.assertEqual(uc.reg_read(registers.UC_ARM64_REG_X1), 0x3F800000)
        self.assertEqual(
            uc.reg_read(registers.UC_ARM64_REG_X3), 0x4008000000000000
        )  # 3.0

    def test_units_throughput_latency_and_roundtrip(self):
        for target, column in ((cortex_a320, 1), (cortex_a520, 2)):
            cases = list(CASES) + [(s, (1, 1), (1, 1)) for s in SCALAR]
            cases += [(s, (1, 2), (1, 2)) for s in CRC]
            for case in cases:
                with self.subTest(target=target.__name__, source=case[0]):
                    inst = parse(case[0])
                    self.assertIs(type(parse(inst.write())), type(inst))
                    self.assertTrue(target.get_units(inst))
                    self.assertEqual(
                        target.get_inverse_throughput(inst), case[column][0]
                    )
                    self.assertEqual(target.get_latency(inst, 0, inst), case[column][1])
                    if case[0] in CRC:
                        self.assertEqual(
                            target.get_units(inst), target.ExecutionUnit.SCALAR_MUL()
                        )

    def test_memory_classification(self):
        for text, vector, store in (
            (CASES[0][0], True, False),
            (CASES[2][0], True, True),
            (CASES[4][0], True, False),
            (CASES[14][0], False, False),
            (CASES[16][0], False, True),
        ):
            inst = parse(text)
            self.assertTrue(inst.is_load_store_instruction())
            self.assertEqual(inst.is_store(), store)
            self.assertEqual(inst.is_load(), not store)
            self.assertEqual(inst.is_vector_load(), vector and not store)
            self.assertEqual(inst.is_vector_store(), vector and store)

    def test_lane_and_flag_dependencies(self):
        inst = parse(CASES[4][0])
        self.assertEqual(inst.args_in, ["x2"])
        self.assertEqual(inst.args_in_out, ["v0", "v1"])
        self.assertEqual(inst.args_out, [])
        self.assertEqual(inst.addr, "x2")
        self.assertFalse(inst.is_q_form_vector_instruction())
        pairs = inst.args_in_out_combinations[0][1]
        self.assertIn(["v30", "v31"], pairs)
        self.assertIn(["v31", "v0"], pairs)
        with self.assertRaises(arch.ParsingException):
            arch.q_ld2_lane_s.make("ld2 {v0.s, v1.s}[4], [x2]")
        self.assertIn("flags", parse(SCALAR[0]).args_out)
        self.assertIn("flags", parse(SCALAR[1]).args_in)
        self.assertEqual(parse("mov v0.s[0], w1").args_in_out, ["v0"])

    def test_hazard_classification_reaches_constraints(self):
        def solve(target, texts, distance):
            model = cp_model.CpModel()
            nodes = [
                SimpleNamespace(
                    inst=parse(text),
                    is_locked=False,
                    cycle_start_var=model.NewIntVar(0, 10, f"c{i}"),
                )
                for i, text in enumerate(texts)
            ]
            model.Add(nodes[0].cycle_start_var == distance)
            model.Add(nodes[1].cycle_start_var == 0)
            fake = SimpleNamespace(
                config=SimpleNamespace(
                    constraints=SimpleNamespace(functional_only=False)
                ),
                get_inst_pairs=lambda cond: [
                    p for p in combinations(nodes, 2) if cond(*p)
                ],
                _Add=model.Add,
            )
            if target is cortex_a520:
                target.add_further_constraints(fake)
            else:
                target.add_st_hazard(fake)
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = 1
            return solver.Solve(model)

        for texts in ((CASES[0][0], "ldr q4, [x3]"), (CASES[4][0], CASES[2][0])):
            self.assertEqual(solve(cortex_a520, texts, 2), cp_model.INFEASIBLE)
            self.assertIn(
                solve(cortex_a520, texts, 3), (cp_model.OPTIMAL, cp_model.FEASIBLE)
            )
        self.assertEqual(
            solve(cortex_a320, (CASES[2][0], "str q4, [x3]"), 1), cp_model.INFEASIBLE
        )

    def test_real_optimizer(self):
        text = "\n".join(
            (
                "ld1 {v0.4s, v1.4s}, [x0]",
                "ld2 {v0.s, v1.s}[1], [x2]",
                "ushl v4.4s, v0.4s, v1.4s",
                "dup v5.4s, w3",
                "tbl v6.16b, {v4.16b, v5.16b}, v1.16b",
                "st1 {v0.4s, v1.4s, v2.4s, v3.4s}, [x7], #64",
                "crc32w w8, w8, w9",
                "cmp x8, xzr",
                "csel x10, x8, xzr, ne",
            )
        )
        for target in (cortex_a320, cortex_a520):
            with self.subTest(target=target.__name__):
                core = SlothyBase(arch, target)
                core.config.outputs = {"v0", "v1", "v6", "x7", "x10"}
                core.config.constraints.allow_renaming = False
                core.config.variable_size = True
                core.config.constraints.stalls_allowed = 80
                core.config.selftest = False
                core.config.timeout = 10
                self.assertTrue(core.optimize(SourceLine.read_multiline(text)))

    @unittest.skipUnless(
        shutil.which("clang-19") and shutil.which("llvm-objcopy-19"),
        "Requires AArch64-capable Clang and llvm-objcopy",
    )
    def test_assembly_and_lane_preservation(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "coverage.s"
            obj = Path(temp) / "coverage.o"
            binary = Path(temp) / "coverage.bin"
            # Put lane LD2 first so it can also be executed independently.
            source.write_text(
                ".text\n"
                + CASES[4][0]
                + "\n"
                + "\n".join([c[0] for c in CASES] + list(SCALAR) + list(CRC))
            )
            subprocess.run(
                [
                    "clang-19",
                    "--target=aarch64-none-elf",
                    "-march=armv8-a+crc",
                    "-c",
                    str(source),
                    "-o",
                    str(obj),
                ],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                [
                    "llvm-objcopy-19",
                    "-O",
                    "binary",
                    "--only-section=.text",
                    str(obj),
                    str(binary),
                ],
                check=True,
                capture_output=True,
            )
            emulator = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
            emulator.mem_map(0x10000, 0x1000)
            emulator.mem_map(0x20000, 0x1000)
            emulator.mem_write(0x10000, binary.read_bytes())
            emulator.mem_write(0x20000, bytes(range(8)))
            emulator.reg_write(UC_ARM64_REG_X2, 0x20000)
            original = [bytes(range(16)), bytes(range(16, 32))]
            for reg, value in zip((UC_ARM64_REG_Q0, UC_ARM64_REG_Q1), original):
                emulator.reg_write(reg, int.from_bytes(value, "little"))
            emulator.emu_start(0x10000, 0x10004)
            for i, reg in enumerate((UC_ARM64_REG_Q0, UC_ARM64_REG_Q1)):
                expected = (
                    original[i][:4] + bytes(range(i * 4, i * 4 + 4)) + original[i][8:]
                )
                self.assertEqual(
                    emulator.reg_read(reg).to_bytes(16, "little"), expected
                )

    def test_a55_timings_not_replaced(self):
        inst = parse("ldp q0, q1, [x2, #32]")
        self.assertEqual(cortex_a55.get_inverse_throughput(inst), 4)
        self.assertEqual(cortex_a55.get_latency(inst, 0, inst), 6)


if __name__ == "__main__":
    unittest.main()
