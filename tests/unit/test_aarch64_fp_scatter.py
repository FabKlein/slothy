"""FP32 subtraction and register-addressed SIMD memory dependencies."""

import logging
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest

from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM
from unicorn import arm64_const as regs

from slothy.core.config import Config
from slothy.core.core import SlothyBase
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as arch, cortex_a520 as target
from slothy.targets.aarch64.isa import (
    UnsupportedISA,
    instruction_features,
    validate_instruction_features,
)
from slothy.targets.exceptions import FatalParsingException, ParsingException

LOGGER = logging.getLogger(__name__)
HAS_ASSEMBLER = shutil.which("clang-19") and shutil.which("llvm-objcopy-19")
FORMS = (
    "fsub v0.4s, v1.4s, v2.4s",
    "fsub v0.2s, v1.2s, v2.2s",
    "str q0, [x0, x1]",
    "str q0, [x0, x1, lsl #0]",
    "str q0, [x0, x1, lsl #4]",
    "ldr q0, [x0, x1]",
    "ldr q0, [x0, x1, lsl #0]",
    "ldr q0, [x0, x1, lsl #4]",
    "st1 {v0.d}[0], [x0], x1",
    "st1 {v0.d}[1], [x0], x1",
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


class FPScatterTests(unittest.TestCase):
    def optimize(self, text, pipeline=False):
        core = SlothyBase(arch, target)
        core.config.inputs_are_outputs = True
        core.config.isa_check = "strict"
        core.config.selftest = False
        core.config.variable_size = True
        core.config.constraints.stalls_allowed = 32
        core.config.sw_pipelining.enabled = pipeline
        if pipeline:
            core.config.sw_pipelining.min_overlapping = 1
        core.config.timeout = 10
        self.assertTrue(core.optimize(SourceLine.read_multiline(text)))
        return core.result

    def test_roundtrip_roles_and_features(self):
        for text in FORMS:
            with self.subTest(text=text):
                inst = parse(text)
                again = parse(inst.write())
                self.assertIs(type(inst), type(again))
                self.assertEqual(inst.args_in, again.args_in)
                self.assertEqual(inst.args_in_out, again.args_in_out)
                self.assertEqual(inst.args_out, again.args_out)
                if text.startswith("fsub"):
                    self.assertEqual(inst.args_in, ["v1", "v2"])
                    self.assertEqual(inst.args_out, ["v0"])
                else:
                    self.assertIsNone(inst.increment)
                    self.assertIsNone(inst.pre_index)
                    self.assertFalse(inst.offset_adjustable)
                    self.assertEqual(inst.addr, "x0")
                    if text.startswith("st1"):
                        self.assertEqual(inst.args_in, ["v0", "x1"])
                        self.assertEqual(inst.args_in_out, ["x0"])
                        self.assertFalse(inst.is_q_form_vector_instruction())
                    elif text.startswith("str"):
                        self.assertEqual(inst.args_in, ["v0", "x0", "x1"])
                        self.assertEqual(inst.args_in_out, [])
                    else:
                        self.assertEqual(inst.args_in, ["x0", "x1"])
                        self.assertEqual(inst.args_out, ["v0"])
                feature = (
                    "FEAT_AdvSIMD" if text.startswith(("fsub", "st1")) else "FEAT_FP"
                )
                expected = (
                    {"FEAT_FP", "FEAT_AdvSIMD"}
                    if feature == "FEAT_AdvSIMD"
                    else {"FEAT_FP"}
                )
                self.assertEqual(instruction_features(inst), expected)
                config = Config(arch, target, LOGGER)
                config.isa_check = "strict"
                validate_instruction_features([inst], config, LOGGER)
                config.isa_features = {feature: False}
                with self.assertRaises(UnsupportedISA):
                    validate_instruction_features([inst], config, LOGGER)

    def test_symbolic_operands_and_renamed_index(self):
        inst = parse("str Q<value>, [X<base>, X<index>, lsl #0]")
        self.assertEqual(inst.args_in, ["value", "base", "index"])
        inst.args_in = ["v5", "x6", "x7"]
        self.assertEqual(parse(inst.write()).args_in, inst.args_in)
        inst = parse("st1 {V<value>.D}[1], [X<base>], X<step>")
        self.assertEqual(inst.args_in, ["value", "step"])
        self.assertEqual(inst.args_in_out, ["base"])
        inst.args_in = ["v3", "x9"]
        inst.args_in_out = ["x8"]
        again = parse(inst.write())
        self.assertEqual(again.args_in, ["v3", "x9"])
        self.assertEqual(again.args_in_out, ["x8"])

    def test_invalid_forms_and_write_validation(self):
        for text in (
            "fsub v0.4s, v1.2s, v2.4s",
            "fsub v0.16b, v1.16b, v2.16b",
            "fsub v0.8h, v1.8h, v2.8h",
        ):
            with self.assertRaises((ParsingException, FatalParsingException)):
                arch.vsubf.make(text)
        for cls, op in (
            (arch.q_ldr_with_imm_shifted, "ldr"),
            (arch.q_str_with_reg_offset_shifted, "str"),
        ):
            for shift in ("lsl #1", "lsl #3", "lsr #0", "ror #4"):
                with self.assertRaises(ParsingException):
                    cls.make(f"{op} q0, [x0, x1, {shift}]")
            inst = cls.make(f"{op} q0, [x0, x1, lsl #0]")
            inst.immediate = "2"
            with self.assertRaises(ParsingException):
                inst.write()
        for suffix in ("d}[2]", "s}[0]", "2d}[0]"):
            with self.assertRaises(ParsingException):
                arch.q_st1_lane_with_reg_postinc.make(f"st1 {{v0.{suffix}, [x0], x1")
        inst = parse("st1 {v0.d}[0], [x0], x1")
        inst.index = 2
        with self.assertRaises(ParsingException):
            inst.write()

    def test_a520_model_and_fsub_schedules(self):
        for text in FORMS:
            inst = parse(text)
            self.assertEqual(target.get_inverse_throughput(inst), 1)
            self.assertEqual(
                target.get_latency(inst, 0, inst), 4 if text.startswith("fsub") else 3
            )
            self.assertTrue(target.get_units(inst))
        result = self.optimize("\n".join(["fsub v0.4s, v0.4s, v1.4s"] * 3))
        positions = result.cycle_position_with_bubbles
        self.assertEqual([positions[i + 1] - positions[i] for i in (0, 1)], [4, 4])
        result = self.optimize(
            "\n".join(f"fsub v{i}.4s, v{i}.4s, v31.4s" for i in range(8))
        )
        positions = result.cycle_position_with_bubbles.values()
        self.assertEqual(max(positions) - min(positions) + 1, 4)

    @unittest.skipUnless(HAS_ASSEMBLER, "Requires AArch64 LLVM tools")
    def test_assembly_and_equivalent_offset_encodings(self):
        assemble("\n".join(parse(text).write() for text in FORMS))
        for op in ("ldr", "str"):
            self.assertEqual(
                assemble(f"{op} q0, [x0, x1]"), assemble(f"{op} q0, [x0, x1, lsl #0]")
            )

    @unittest.skipUnless(HAS_ASSEMBLER, "Requires AArch64 LLVM tools")
    def test_fp32_subtraction_execution(self):
        for shape, elements in (("2s", 2), ("4s", 4)):
            code = assemble(f"fsub v0.{shape}, v1.{shape}, v2.{shape}")
            uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
            uc.mem_map(0x10000, 0x1000)
            uc.mem_write(0x10000, code)
            uc.reg_write(regs.UC_ARM64_REG_CPACR_EL1, 3 << 20)
            uc.reg_write(regs.UC_ARM64_REG_Q0, (1 << 128) - 1)
            for reg, values in (
                (regs.UC_ARM64_REG_Q1, (-4, 0, 1, 8)),
                (regs.UC_ARM64_REG_Q2, (1, -1, 2, 4)),
            ):
                uc.reg_write(reg, int.from_bytes(struct.pack("<4f", *values), "little"))
            uc.emu_start(0x10000, 0x10000 + len(code))
            expected = struct.pack(f"<{elements}f", *(-5, 1, -1, 4)[:elements])
            self.assertEqual(
                uc.reg_read(regs.UC_ARM64_REG_Q0),
                int.from_bytes(expected.ljust(16, b"\0"), "little"),
            )

    @unittest.skipUnless(HAS_ASSEMBLER, "Requires AArch64 LLVM tools")
    def test_scaled_register_offsets_execute(self):
        for op in ("ldr", "str"):
            for shift, scale in (("", 1), (", lsl #0", 1), (", lsl #4", 16)):
                with self.subTest(op=op, shift=shift):
                    inst = parse(f"{op} q0, [x0, x1{shift}]")
                    code = assemble(inst.write())
                    uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
                    uc.mem_map(0x10000, 0x1000)
                    uc.mem_write(0x10000, code)
                    uc.mem_map(0x20000, 0x1000)
                    uc.reg_write(regs.UC_ARM64_REG_CPACR_EL1, 3 << 20)
                    uc.reg_write(regs.UC_ARM64_REG_X0, 0x20000)
                    uc.reg_write(regs.UC_ARM64_REG_X1, 3)
                    payload = bytes(range(16))
                    uc.reg_write(
                        regs.UC_ARM64_REG_Q0, int.from_bytes(payload, "little")
                    )
                    memory = bytearray(range(128))
                    uc.mem_write(0x20000, bytes(memory))
                    uc.emu_start(0x10000, 0x10000 + len(code))
                    offset = 3 * scale
                    if op == "str":
                        memory[offset : offset + 16] = payload
                    else:
                        self.assertEqual(
                            uc.reg_read(regs.UC_ARM64_REG_Q0),
                            int.from_bytes(memory[offset : offset + 16], "little"),
                        )
                    self.assertEqual(bytes(uc.mem_read(0x20000, 128)), memory)
                    self.assertEqual(uc.reg_read(regs.UC_ARM64_REG_X0), 0x20000)
                    self.assertEqual(uc.reg_read(regs.UC_ARM64_REG_X1), 3)

    @unittest.skipUnless(HAS_ASSEMBLER, "Requires AArch64 LLVM tools")
    def test_reordered_and_pipelined_execution(self):
        body = (
            "add x3, x3, #16\n"
            "ldr q0, [x0, x3]\n"
            "ldr q6, [x0], #16\n"
            "fsub v1.4s, v0.4s, v2.4s\n"
            "str q1, [x1, x3, lsl #0]\n"
            "str q6, [x1], #16\n"
            "add x4, x4, #16\n"
            "st1 {v1.d}[0], [x5], x4\n"
            "st1 {v1.d}[1], [x5], x4\n"
        )
        for pipeline in (False, True):
            result = self.optimize(body, pipeline)
            if pipeline:
                self.assertGreater(result.num_exceptional_iterations, 0)
                original, optimized = result.get_fully_unrolled_loop(4)
            else:
                original = SourceLine.read_multiline(body) * 4
                optimized = result.code * 4
            for source in (original, optimized):
                code = assemble("\n".join(line.text for line in source))
                uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
                uc.mem_map(0x10000, 0x1000)
                uc.mem_write(0x10000, code)
                uc.mem_map(0x20000, 0x4000)
                uc.reg_write(regs.UC_ARM64_REG_CPACR_EL1, 3 << 20)
                uc.reg_write(regs.UC_ARM64_REG_X0, 0x20000)
                uc.reg_write(regs.UC_ARM64_REG_X1, 0x21000)
                uc.reg_write(regs.UC_ARM64_REG_X5, 0x22000)
                values = struct.pack("<32f", *range(32))
                uc.mem_write(0x20000, values)
                uc.mem_write(0x21000, bytes([0xA5]) * 512)
                uc.mem_write(0x22000, bytes([0xA5]) * 512)
                uc.reg_write(
                    regs.UC_ARM64_REG_Q2,
                    int.from_bytes(struct.pack("<4f", 1, 2, 4, 8), "little"),
                )
                uc.emu_start(0x10000, 0x10000 + len(code))
                expected = bytearray([0xA5] * 512)
                lanes = bytearray(expected)
                ptr = 0
                for iteration in range(1, 5):
                    data = struct.pack(
                        "<4f",
                        *(
                            8 * iteration - 4 + j - sub
                            for j, sub in enumerate((1, 2, 4, 8))
                        ),
                    )
                    offset = 16 * (2 * iteration - 1)
                    expected[offset : offset + 16] = data
                    offset = 16 * (iteration - 1)
                    expected[offset : offset + 16] = values[offset : offset + 16]
                    for lane in (0, 1):
                        lanes[ptr : ptr + 8] = data[lane * 8 : lane * 8 + 8]
                        ptr += 16 * iteration
                self.assertEqual(bytes(uc.mem_read(0x21000, 512)), expected)
                self.assertEqual(bytes(uc.mem_read(0x22000, 512)), lanes)
                self.assertEqual(bytes(uc.mem_read(0x20000, len(values))), values)
                self.assertEqual(uc.reg_read(regs.UC_ARM64_REG_X3), 64)
                self.assertEqual(uc.reg_read(regs.UC_ARM64_REG_X0), 0x20040)
                self.assertEqual(uc.reg_read(regs.UC_ARM64_REG_X1), 0x21040)
                self.assertEqual(uc.reg_read(regs.UC_ARM64_REG_X4), 64)
                self.assertEqual(uc.reg_read(regs.UC_ARM64_REG_X5), 0x22000 + ptr)


if __name__ == "__main__":
    unittest.main()
