"""NEON unscaled loads and FP by-element instruction coverage."""

from collections import Counter
from pathlib import Path
import random
import shutil
import struct
import subprocess
import tempfile
import unittest

from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM
from unicorn.arm64_const import (
    UC_ARM64_REG_CPACR_EL1,
    UC_ARM64_REG_Q0,
    UC_ARM64_REG_X0,
    UC_ARM64_REG_X1,
    UC_ARM64_REG_X2,
)

from slothy.helper import SourceLine
from slothy.core.core import SlothyBase
from slothy.targets.aarch64 import aarch64_neon as arch
from slothy.targets.aarch64 import cortex_a520 as target


def parse(text):
    return arch.Instruction.parser(SourceLine(text))[0]


class FPLaneTests(unittest.TestCase):
    def test_ldur_signed_byte_offsets(self):
        for offset in (-256, -4, 0, 4, 236, 255):
            with self.subTest(offset=offset):
                inst = parse(f"ldur q16, [x0, #{offset}]")
                self.assertIsInstance(inst, arch.Ldr_Q)
                self.assertEqual(inst.args_in, ["x0"])
                self.assertEqual(inst.args_out, ["v16"])
                self.assertEqual(inst.addr, "x0")
                self.assertIsNone(inst.increment)
                self.assertEqual(int(inst.pre_index), offset)
                self.assertTrue(inst.is_vector_load())
                self.assertEqual(int(parse(inst.write()).pre_index), offset)
        for offset in (-257, 256):
            with self.assertRaises(arch.Instruction.ParsingException):
                arch.q_ldur.make(f"ldur q16, [x0, #{offset}]")

    def test_ldur_address_fixup(self):
        inst = parse("ldur q16, [x0, #4]")
        inst.pre_index = -124
        self.assertEqual(int(parse(inst.write()).pre_index), -124)
        inst.pre_index = 256
        with self.assertRaises(arch.Instruction.ParsingException):
            inst.write()

    def test_lane_multiply_and_accumulate_dependencies(self):
        for mnemonic, cls in (("fmul", arch.vmulf_lane), ("fmla", arch.vfmla_lane)):
            for lane in range(4):
                with self.subTest(mnemonic=mnemonic, lane=lane):
                    inst = parse(f"{mnemonic} v0.4s, v16.4s, v31.s[{lane}]")
                    self.assertIsInstance(inst, cls)
                    self.assertEqual(inst.args_in, ["v16", "v31"])
                    self.assertEqual(inst.index, lane)
                    self.assertEqual(
                        inst.args_out, ["v0"] if mnemonic == "fmul" else []
                    )
                    self.assertEqual(
                        inst.args_in_out, ["v0"] if mnemonic == "fmla" else []
                    )
                    self.assertEqual(parse(inst.write()).index, lane)

    def test_lane_arrangements(self):
        for text in (
            "fmul v0.2s, v1.2s, v31.s[3]",
            "fmla v0.2d, v1.2d, v31.d[1]",
            "fmul v0.8h, v1.8h, v15.h[7]",
        ):
            inst = parse(text)
            self.assertEqual(parse(inst.write()).datatype, inst.datatype)
        self.assertEqual(
            parse("fmul v0.8h, v1.8h, v15.h[7]").args_in_restrictions[1],
            [f"v{i}" for i in range(16)],
        )
        for text in (
            "fmul v0.4s, v1.4s, v2.s[4]",
            "fmul v0.4s, v1.4s, v2.d[1]",
            "fmul v0.16b, v1.16b, v2.b[0]",
        ):
            with self.assertRaises(arch.Instruction.ParsingException):
                arch.vmulf_lane.make(text)

    def test_a520_scheduling(self):
        dst = parse("fmla v0.4s, v16.4s, v24.s[1]")
        for text, latency in (
            ("ldur q16, [x0, #4]", 3),
            ("fmul v0.4s, v16.4s, v24.s[0]", 4),
            ("fmla v0.4s, v16.4s, v24.s[1]", 4),
        ):
            inst = parse(text)
            self.assertEqual(target.get_inverse_throughput(inst), 1)
            self.assertEqual(target.get_latency(inst, 0, dst), latency)
            self.assertEqual(len(target.get_units(inst)), 2)

    def test_complete_example(self):
        source = (
            Path(__file__).resolve().parents[2]
            / "examples/naive/aarch64/fp32_fir/fp32_fir_ca520.s"
        ).read_text()
        body = source.split("start:\n", 1)[1].split("    subs ", 1)[0]
        instructions = [parse(line) for line in body.splitlines() if line.strip()]
        counts = Counter(type(i) for i in instructions)
        self.assertEqual(len(instructions), 322)
        self.assertEqual(counts[arch.q_ldur], 60)
        self.assertEqual(counts[arch.vmulf_lane], 8)
        self.assertEqual(counts[arch.vfmla_lane], 248)
        for inst in instructions:
            target.get_units(inst)
            target.get_inverse_throughput(inst)
            target.get_latency(inst, 0, instructions[0])

    def test_fixed_order_estimation_keeps_instruction_order(self):
        source = SourceLine.read_multiline(
            "ldur q16, [x0, #4]\n"
            "fmul v0.4s, v16.4s, v24.s[0]\n"
            "fmla v0.4s, v16.4s, v24.s[1]\n"
            "fmla v0.4s, v16.4s, v24.s[2]\n"
        )
        core = SlothyBase(arch, target)
        core.config.outputs = {"v0"}
        core.config.constraints.allow_reordering = False
        core.config.constraints.allow_renaming = False
        core.config.variable_size = True
        core.config.constraints.stalls_allowed = 24
        core.config.selftest = False
        core.config.timeout = 10
        self.assertTrue(core.optimize(source))
        expected = [parse(line.text).write() for line in source if line.text.strip()]
        actual = [
            parse(line.text).write() for line in core.result.code if line.text.strip()
        ]
        self.assertEqual(actual, expected)

    def test_paired_load_example(self):
        source = (
            Path(__file__).resolve().parents[2]
            / "examples/naive/aarch64/fp32_fir/fp32_fir_ca520_ldp.s"
        ).read_text()
        body = source.split("start:\n", 1)[1].split("    subs ", 1)[0]
        instructions = [parse(line) for line in body.splitlines() if line.strip()]
        counts = Counter(type(i) for i in instructions)
        self.assertEqual(len(instructions), 292)
        self.assertEqual(counts[arch.q_ldp_with_postinc], 28)
        self.assertEqual(counts[arch.q_ldr_with_postinc], 4)
        self.assertEqual(counts[arch.q_stp_with_postinc], 4)
        self.assertEqual(counts[arch.vmulf_lane], 8)
        self.assertEqual(counts[arch.vfmla_lane], 248)
        for inst in instructions:
            target.get_units(inst)
            target.get_inverse_throughput(inst)
            target.get_latency(inst, 0, instructions[0])

    @unittest.skipUnless(
        shutil.which("clang-19") and shutil.which("llvm-objcopy-19"),
        "AArch64-capable Clang 19 and llvm-objcopy-19 required",
    )
    def test_variants_match_original_execution(self):
        root = Path(__file__).resolve().parents[2]
        paths = [
            root / "examples/naive/aarch64/fp32_fir/fp32_fir_ca520.s",
            root / "examples/opt/aarch64/fp32_fir/fp32_fir_ca520_opt.s",
            root / "examples/naive/aarch64/fp32_fir/fp32_fir_ca520_ldp.s",
            root / "examples/opt/aarch64/fp32_fir/fp32_fir_ca520_ldp_baseline.s",
            root / "examples/opt/aarch64/fp32_fir/fp32_fir_ca520_ldp_opt.s",
            root / "examples/opt/aarch64/fp32_fir/fp32_fir_ca520_ldp_swpipe_eval.s",
            root / "examples/opt/aarch64/fp32_fir/fp32_fir_ca520_ldp_swpipe.s",
            root / "examples/opt/aarch64/fp32_fir/fp32_fir_ca520_swpipe.s",
        ]
        binaries = []
        with tempfile.TemporaryDirectory() as tmp:
            obj, binary = Path(tmp) / "loop.o", Path(tmp) / "loop.bin"
            for path in paths:
                subprocess.run(
                    [
                        "clang-19",
                        "--target=aarch64-none-elf",
                        "-c",
                        str(path),
                        "-o",
                        str(obj),
                    ],
                    check=True,
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
                )
                binaries.append(binary.read_bytes())

        rng = random.Random(520)
        memory = b"".join(struct.pack("<f", rng.uniform(-2, 2)) for _ in range(16384))
        coefficients = [
            int.from_bytes(
                b"".join(struct.pack("<f", rng.uniform(-1, 1)) for _ in range(4)),
                "little",
            )
            for _ in range(8)
        ]

        def run(code, tiles, offset):
            emu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
            emu.mem_map(0x100000, 0x10000)
            emu.mem_write(0x100000, code)
            emu.mem_map(0x200000, 0x10000)
            emu.mem_write(0x200000, memory)
            emu.reg_write(UC_ARM64_REG_CPACR_EL1, 3 << 20)
            for reg, value in (
                (UC_ARM64_REG_X0, 0x201000),
                (UC_ARM64_REG_X1, 0x201000 + offset),
                (UC_ARM64_REG_X2, tiles),
            ):
                emu.reg_write(reg, value)
            for i, value in enumerate(coefficients):
                emu.reg_write(UC_ARM64_REG_Q0 + 24 + i, value)
            emu.emu_start(0x100000, 0x100000 + len(code), count=10000)
            self.assertEqual(emu.reg_read(UC_ARM64_REG_X2), 0)
            pointers = tuple(
                emu.reg_read(reg)
                for reg in (UC_ARM64_REG_X0, UC_ARM64_REG_X1, UC_ARM64_REG_X2)
            )
            weights = tuple(emu.reg_read(UC_ARM64_REG_Q0 + 24 + i) for i in range(8))
            return bytes(emu.mem_read(0x200000, 0x10000)), pointers, weights

        for tiles in (1, 2, 3, 5, 8):
            for offset in (-4096, 0, 4, 128, 8192):
                expected = run(binaries[0], tiles, offset)
                for path, binary in zip(paths[1:], binaries[1:]):
                    # Both actual SWP schedules require disjoint buffers.
                    # Partial overlaps were checked and change results; the
                    # LDUR schedule also reorders stores within the preamble.
                    disjoint_only = path.name in {
                        "fp32_fir_ca520_ldp_swpipe.s",
                        "fp32_fir_ca520_swpipe.s",
                    }
                    if disjoint_only and offset not in (-4096, 8192):
                        continue
                    with self.subTest(
                        variant=path.name, tiles=tiles, destination_offset=offset
                    ):
                        self.assertEqual(expected, run(binary, tiles, offset))


if __name__ == "__main__":
    unittest.main()
