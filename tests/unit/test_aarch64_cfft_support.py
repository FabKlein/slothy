"""CFFT scalar/addressing coverage and Cortex-A520 scheduling regressions."""

import logging
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM
from unicorn import arm64_const as regs

from slothy.core.config import Config
from slothy.core.core import SlothyBase
from slothy.helper import SourceLine, lookup_multidict
from slothy.targets.aarch64 import aarch64_neon as arch, cortex_a520 as target
from slothy.targets.aarch64.isa import (
    UnsupportedISA,
    instruction_features,
    validate_instruction_features,
)
from slothy.targets.exceptions import ParsingException

LOGGER = logging.getLogger(__name__)
HAS_ASSEMBLER = shutil.which("clang-19") and shutil.which("llvm-objcopy-19")
FORMS = (
    "cmp w24, w11",
    "cmp w19, #1",
    "ldr d1, [x8, x5]",
    "ldr d1, [x8, x5, lsl #0]",
    "ldr d1, [x8, x5, lsl #3]",
    "lsl x8, x10, #2",
    "madd x8, x10, x4, x21",
)


def parse(text):
    return arch.Instruction.parser(SourceLine(text))[0]


def assemble(text):
    with tempfile.TemporaryDirectory() as directory:
        obj = Path(directory) / "test.o"
        binary = obj.with_suffix(".bin")
        subprocess.run(
            [
                "clang-19",
                "--target=aarch64-none-elf",
                "-x",
                "assembler",
                "-c",
                "-",
                "-o",
                str(obj),
            ],
            input=".text\n" + text + "\n",
            text=True,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["llvm-objcopy-19", "-O", "binary", "--only-section=.text", obj, binary],
            capture_output=True,
            check=True,
        )
        return binary.read_bytes()


def emulator(code):
    uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    uc.mem_map(0x10000, 0x1000)
    uc.mem_write(0x10000, code)
    uc.reg_write(regs.UC_ARM64_REG_CPACR_EL1, 3 << 20)
    return uc


class CFFTSupportTests(unittest.TestCase):
    def optimize(self, text, pipeline=False, isa_check="strict", outputs=()):
        core = SlothyBase(arch, target)
        core.config.inputs_are_outputs = True
        core.config.outputs = list(outputs)
        core.config.isa_check = isa_check
        core.config.selftest = False
        core.config.variable_size = True
        core.config.constraints.stalls_allowed = 32
        core.config.sw_pipelining.enabled = pipeline
        if pipeline:
            core.config.sw_pipelining.min_overlapping = 1
        core.config.timeout = 10
        self.assertTrue(core.optimize(SourceLine.read_multiline(text)))
        return core.result

    def test_roundtrip_roles_and_isa(self):
        for text in FORMS:
            with self.subTest(text=text):
                inst = parse(text)
                again = parse(inst.write())
                self.assertIs(type(inst), type(again))
                self.assertEqual(inst.args_in, again.args_in)
                self.assertEqual(inst.args_out, again.args_out)
                self.assertEqual(inst.args_in_out, [])
                if text.startswith("cmp"):
                    expected = ["x24", "x11"] if "w24" in text else ["x19"]
                    self.assertEqual(inst.args_in, expected)
                    self.assertEqual(inst.args_out, ["flags"])
                elif text.startswith("ldr"):
                    self.assertEqual(inst.args_in, ["x8", "x5"])
                    self.assertEqual(inst.args_out, ["v1"])
                    self.assertEqual(inst.addr, "x8")
                    self.assertIsNone(inst.increment)
                    self.assertIsNone(inst.pre_index)
                    self.assertFalse(inst.offset_adjustable)
                    self.assertTrue(inst.is_load())
                    self.assertTrue(inst.is_vector_load())
                    self.assertFalse(inst.is_q_form_vector_instruction())
                elif text.startswith("lsl"):
                    self.assertEqual(inst.args_in, ["x10"])
                    self.assertEqual(inst.args_out, ["x8"])
                else:
                    self.assertEqual(inst.args_in, ["x10", "x4", "x21"])
                    self.assertEqual(inst.args_out, ["x8"])
                    self.assertEqual(inst.inputs, ["Xa", "Xb", "Xacc"])
                expected = {"FEAT_FP"} if text.startswith("ldr") else set()
                self.assertEqual(instruction_features(inst), expected)
                config = Config(arch, target, LOGGER)
                config.isa_check = "strict"
                validate_instruction_features([inst], config, LOGGER)
                if expected:
                    config.isa_features = {"FEAT_FP": False}
                    with self.assertRaises(UnsupportedISA):
                        validate_instruction_features([inst], config, LOGGER)

    def test_symbolic_operands_and_renaming(self):
        cases = (
            ("cmp W<lhs>, W<rhs>", ["lhs", "rhs"], ["x24", "x11"], ["flags"]),
            ("cmp W<lhs>, #1", ["lhs"], ["x19"], ["flags"]),
            (
                "ldr D<value>, [X<base>, X<index>, LSL #3]",
                ["base", "index"],
                ["x8", "x5"],
                ["v1"],
            ),
        )
        for text, symbolic, renamed, outputs in cases:
            inst = parse(text)
            self.assertEqual(inst.args_in, symbolic)
            inst.args_in = renamed
            inst.args_out = outputs
            again = parse(inst.write())
            self.assertEqual(again.args_in, renamed)
            self.assertEqual(again.args_out, outputs)

    def test_invalid_load_shifts_and_mixed_compare_widths(self):
        cls = arch.d_ldr_with_reg_offset_shifted
        for shift in ("lsl #1", "lsl #4", "lsr #0", "asr #3", "ror #0"):
            with self.subTest(shift=shift), self.assertRaises(ParsingException):
                cls.make(f"ldr d1, [x8, x5, {shift}]")
        inst = cls.make("ldr d1, [x8, x5, lsl #3]")
        inst.immediate = "4"
        with self.assertRaises(ParsingException):
            inst.write()
        for cls, text in (
            (arch.cmp_wform, "cmp w24, x11"),
            (arch.cmp_wform, "cmp x24, w11"),
            (arch.cmp_imm_wform, "cmp x19, #1"),
            (arch.d_ldr_with_reg_offset, "ldr d1, [x8, w5]"),
        ):
            with self.subTest(text=text), self.assertRaises(ParsingException):
                cls.make(text)

    def test_a520_lookups_and_madd_forwarding(self):
        for text in FORMS:
            inst = parse(text)
            latency = (
                3 if text.startswith("ldr") else 4 if text.startswith("madd") else 1
            )
            occupancy = 2 if text.startswith("madd") else 1
            self.assertEqual(target.get_inverse_throughput(inst), occupancy)
            self.assertEqual(target.get_latency(inst, 0, inst), latency)
            self.assertEqual(
                lookup_multidict(target.default_latencies, inst, type(inst)), latency
            )
            self.assertTrue(target.get_units(inst))
        source = parse("madd x8, x10, x4, x21")
        for text, expected in (
            ("madd x9, x10, x4, x8", 2),  # true accumulator, not destination
            ("madd x8, x10, x4, x8", 2),
            ("madd x9, x8, x4, x21", 4),
            ("madd x9, x10, x8, x21", 4),
            ("madd x9, x8, x4, x8", 4),  # accumulator AND multiplicand
            ("madd x9, x10, x8, x8", 4),
            ("add x9, x8, #1", 4),
            ("mul x9, x8, x10", 4),
        ):
            self.assertEqual(target.get_latency(source, 0, parse(text)), expected, text)
        self.assertEqual(
            target.get_latency(
                parse("mul x8, x10, x4"), 0, parse("madd x9, x1, x2, x8")
            ),
            4,
        )

    def test_dependency_and_independent_schedules(self):
        for instruction, spacing in (
            ("lsl x8, x8, #2", 1),
            ("madd x8, x10, x4, x8", 2),
            ("madd x8, x8, x4, x21", 4),
            ("madd x8, x10, x8, x8", 4),
        ):
            result = self.optimize("\n".join([instruction] * 3))
            cycles = result.cycle_position_with_bubbles
            self.assertEqual([cycles[i + 1] - cycles[i] for i in (0, 1)], [spacing] * 2)
        result = self.optimize("\n".join(f"lsl x{i}, x{i}, #2" for i in range(8)))
        cycles = sorted(result.cycle_position_with_bubbles.values())
        self.assertEqual([c - cycles[0] for c in cycles], [0, 0, 1, 1, 2, 2, 3, 3])
        result = self.optimize(
            "\n".join(f"madd x{i}, x20, x21, x{i}" for i in range(8))
        )
        cycles = sorted(result.cycle_position_with_bubbles.values())
        self.assertEqual([c - cycles[0] for c in cycles], list(range(0, 16, 2)))

    @unittest.skipUnless(HAS_ASSEMBLER, "Requires AArch64 LLVM tools")
    def test_assembly_and_equivalent_offset_encodings(self):
        assemble("\n".join(parse(text).write() for text in FORMS))
        self.assertEqual(assemble(FORMS[2]), assemble(FORMS[3]))

    @unittest.skipUnless(HAS_ASSEMBLER, "Requires AArch64 LLVM tools")
    def test_cmp_32bit_flags_execute(self):
        for immediate in (False, True):
            code = assemble("cmp w24, #1" if immediate else "cmp w24, w11")
            for lhs, rhs in (
                (0xFFFFFFFFFFFFFFFF, 0),
                (0x100000000, 0),
                (0x80000000, 1),
                (0x7FFFFFFF, 0xFFFFFFFF),
                (0x100000001, 1),
            ):
                uc = emulator(code)
                uc.reg_write(regs.UC_ARM64_REG_X24, lhs)
                uc.reg_write(regs.UC_ARM64_REG_X11, rhs)
                uc.emu_start(0x10000, 0x10000 + len(code))
                a, b = lhs & 0xFFFFFFFF, 1 if immediate else rhs & 0xFFFFFFFF
                diff = (a - b) & 0xFFFFFFFF
                flags = (
                    ((diff >> 31) << 31)
                    | (int(diff == 0) << 30)
                    | (int(a >= b) << 29)
                    | (int(bool((a ^ b) & (a ^ diff) & 0x80000000)) << 28)
                )
                self.assertEqual(uc.reg_read(regs.UC_ARM64_REG_NZCV), flags)
                self.assertEqual(uc.reg_read(regs.UC_ARM64_REG_X24), lhs)
                self.assertEqual(uc.reg_read(regs.UC_ARM64_REG_X11), rhs)

    @unittest.skipUnless(HAS_ASSEMBLER, "Requires AArch64 LLVM tools")
    def test_indexed_d_load_execution(self):
        for shift, scale in (("", 1), (", lsl #0", 1), (", lsl #3", 8)):
            code = assemble(parse(f"ldr d1, [x8, x5{shift}]").write())
            uc = emulator(code)
            uc.mem_map(0x20000, 0x1000)
            data = bytes(range(128))
            uc.mem_write(0x20000, data)
            uc.reg_write(regs.UC_ARM64_REG_X8, 0x20000)
            uc.reg_write(regs.UC_ARM64_REG_X5, 3)
            uc.reg_write(regs.UC_ARM64_REG_Q1, (1 << 128) - 1)
            uc.emu_start(0x10000, 0x10000 + len(code))
            self.assertEqual(
                uc.reg_read(regs.UC_ARM64_REG_Q1),
                int.from_bytes(data[3 * scale : 3 * scale + 8], "little"),
            )
            self.assertEqual(uc.reg_read(regs.UC_ARM64_REG_X8), 0x20000)
            self.assertEqual(uc.reg_read(regs.UC_ARM64_REG_X5), 3)
            self.assertEqual(bytes(uc.mem_read(0x20000, len(data))), data)

    @unittest.skipUnless(HAS_ASSEMBLER, "Requires AArch64 LLVM tools")
    def test_reordered_and_pipelined_execution(self):
        body = (
            "lsl x5, x6, #2\n"
            "madd x5, x5, x7, x9\n"
            "ldr d1, [x0, x5]\n"
            "add v2.2d, v2.2d, v1.2d\n"
            "add x6, x6, #2\n"
            "cmp w24, w11\n"
            "csel x12, x12, x14, eq\n"
            "cmp w19, #1\n"
            "csel x15, x16, x15, hi\n"
        )
        for pipeline in (False, True):
            # Existing CSEL is unclassified. New forms have strict ISA checks
            # above and in the isolated scheduling tests. Flags are consumed
            # inside the loop, not part of its live-out contract.
            result = self.optimize(
                body,
                pipeline,
                isa_check="warn",
                outputs=("v1", "x5", "x12", "x15"),
            )
            if pipeline:
                self.assertGreater(result.num_exceptional_iterations, 0)
                original, optimized = result.get_fully_unrolled_loop(4)
            else:
                original = SourceLine.read_multiline(body) * 4
                optimized = result.code * 4
            for source in (original, optimized):
                code = assemble("\n".join(line.text for line in source))
                uc = emulator(code)
                uc.mem_map(0x20000, 0x1000)
                data = bytes(range(128))
                uc.mem_write(0x20000, data)
                values = {
                    0: 0x20000,
                    6: 0,
                    7: 1,
                    9: 16,
                    24: 0x100000009,
                    11: 9,
                    19: 0x100000001,
                    12: 123,
                    14: 456,
                    16: 789,
                    15: 987,
                }
                for index, value in values.items():
                    uc.reg_write(getattr(regs, f"UC_ARM64_REG_X{index}"), value)
                uc.reg_write(regs.UC_ARM64_REG_Q1, (1 << 128) - 1)
                uc.reg_write(regs.UC_ARM64_REG_Q2, 0)
                uc.emu_start(0x10000, 0x10000 + len(code))
                for index, expected in ((5, 40), (6, 8), (12, 123), (15, 987)):
                    self.assertEqual(
                        uc.reg_read(getattr(regs, f"UC_ARM64_REG_X{index}")), expected
                    )
                self.assertEqual(
                    uc.reg_read(regs.UC_ARM64_REG_Q1),
                    int.from_bytes(data[40:48], "little"),
                )
                expected_sum = sum(
                    int.from_bytes(data[offset : offset + 8], "little")
                    for offset in (16, 24, 32, 40)
                ) % (1 << 64)
                self.assertEqual(uc.reg_read(regs.UC_ARM64_REG_Q2), expected_sum)
                self.assertEqual(bytes(uc.mem_read(0x20000, len(data))), data)
                for index, expected in values.items():
                    if index != 6:
                        self.assertEqual(
                            uc.reg_read(getattr(regs, f"UC_ARM64_REG_X{index}")),
                            expected,
                        )


if __name__ == "__main__":
    unittest.main()
