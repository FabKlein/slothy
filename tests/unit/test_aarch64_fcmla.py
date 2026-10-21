"""FP16/FP32 vector FCMLA parsing, legality, scheduling, and execution."""

import logging
import shutil
import struct
import unittest

from sympy import simplify
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM
from unicorn.arm64_const import UC_ARM64_REG_Q0, UC_ARM64_REG_Q1, UC_ARM64_REG_Q2

from slothy.core.config import Config
from slothy.core.core import SlothyBase
from slothy.helper import LLVM_Mc, SourceLine, lookup_multidict
from slothy.targets.aarch64 import aarch64_neon as arch
from slothy.targets.aarch64 import cortex_a320, cortex_a520, cortex_a55
from slothy.targets.aarch64.isa import (
    FEATURES,
    UnsupportedISA,
    instruction_features,
    validate_instruction_features,
)
from slothy.targets.exceptions import FatalParsingException, ParsingException

LOGGER = logging.getLogger(__name__)
SHAPES = ("4h", "8h", "2s", "4s")
ROTATIONS = (0, 90, 180, 270)
TARGETS = (cortex_a320, cortex_a520)
HAS_TOOLS = shutil.which("llvm-mc") and shutil.which("clang")


def parse(text):
    return arch.Instruction.parser(SourceLine(text))[0]


def instruction(shape, rotation=90, dest=0, left=1, right=2):
    return f"fcmla v{dest}.{shape}, v{left}.{shape}, v{right}.{shape}, #{rotation}"


def assemble(lines):
    code, offset = LLVM_Mc.assemble(
        SourceLine.read_multiline("\n".join(lines)),
        arch.llvm_mc_arch,
        arch.llvm_mc_attr,
        LOGGER,
        preprocessor="clang",
    )
    return code, offset


class FcmlaTests(unittest.TestCase):
    def test_json_definition_and_roundtrip(self):
        spec = next(s for s in arch._NEON_SPECS if s["name"] == "vfcmla")
        self.assertEqual(spec["operand_values"]["imm"], list(ROTATIONS))
        for shape in SHAPES:
            for rotation in ROTATIONS:
                for spelling in (shape, shape.upper()):
                    inst = parse(instruction(spelling, rotation))
                    self.assertIs(type(inst), arch.vfcmla)
                    self.assertEqual(inst.args_in, ["v1", "v2"])
                    self.assertEqual(inst.args_in_out, ["v0"])
                    self.assertEqual(inst.args_out, [])
                    self.assertEqual(inst.datatype, [shape] * 3)
                    rewritten = parse(inst.write())
                    self.assertEqual(int(rewritten.immediate), rotation)
                    self.assertEqual(rewritten.args_in_out, ["v0"])
        inst = parse("fcmla V<acc>.4s, V<a>.4s, V<b>.4s, #90")
        self.assertEqual(inst.args_in, ["a", "b"])
        self.assertEqual(inst.args_in_out, ["acc"])
        self.assertEqual(parse(inst.write()).args_in_out, ["acc"])

    def test_reject_unsupported_shapes_rotations_and_indexed_forms(self):
        for shape in ("2h", "16h", "8s", "2d", "16b", "h"):
            with self.subTest(shape=shape), self.assertRaises(ParsingException):
                arch.vfcmla.make(instruction(shape))
        for rotation in (-90, 1, 45, 360, "rotation", "90/2"):
            with self.subTest(rotation=rotation), self.assertRaises(ParsingException):
                arch.vfcmla.make(instruction("8h", rotation))
        for text in (
            "fcmla v0.4h, v1.4h, v2.8h, #90",
            "fcmla v0.4s, v1.2s, v2.4s, #90",
            "fcmla v0.4s, v1.4s, v2.s[0], #90",
        ):
            with self.assertRaises((ParsingException, FatalParsingException)):
                arch.vfcmla.make(text)
        for expression in ("180-90", "0x5a", "(45+45)"):
            inst = parse(instruction("4s", expression))
            self.assertEqual(simplify(parse(inst.write()).immediate), 90)

    def test_writer_revalidates_changed_operands(self):
        for immediate in (45, "unknown", "45/2"):
            inst = parse(instruction("4s"))
            inst.immediate = immediate
            with self.assertRaises(ParsingException):
                inst.write()
        for datatype in (["8h", "4h", "8h"], ["2d"] * 3):
            inst = parse(instruction("8h"))
            inst.datatype = datatype
            with self.assertRaises(ParsingException):
                inst.write()

    def test_isa_features_and_a55_rejection(self):
        self.assertEqual(FEATURES["FEAT_FCMA"].available_from, "armv8.3-a")
        for shape in SHAPES:
            inst = parse(instruction(shape))
            expected = {"FEAT_FP", "FEAT_AdvSIMD", "FEAT_FCMA"}
            if shape.endswith("h"):
                expected.add("FEAT_FP16")
            self.assertEqual(instruction_features(inst), expected)
            for target in TARGETS:
                config = Config(arch, target, LOGGER)
                config.isa_check = "strict"
                validate_instruction_features([inst], config, LOGGER)
                config.isa_features = {"FEAT_FCMA": False}
                with self.assertRaisesRegex(UnsupportedISA, "FEAT_FCMA"):
                    validate_instruction_features([inst], config, LOGGER)
                config.isa_features = {"FEAT_FP16": False}
                if shape.endswith("h"):
                    with self.assertRaisesRegex(UnsupportedISA, "FEAT_FP16"):
                        validate_instruction_features([inst], config, LOGGER)
                else:
                    validate_instruction_features([inst], config, LOGGER)
            config = Config(arch, cortex_a55, LOGGER)
            with self.assertRaisesRegex(UnsupportedISA, "FEAT_FCMA"):
                validate_instruction_features([inst], config, LOGGER)

    def test_timing_tables_and_dependency_paths(self):
        for target in TARGETS:
            for shape in SHAPES:
                for rotation in ROTATIONS:
                    inst = parse(instruction(shape, rotation))
                    self.assertEqual(target.get_inverse_throughput(inst), 1)
                    units = [target.ExecutionUnit.VEC0]
                    if target is cortex_a520:
                        units.append(target.ExecutionUnit.VEC1)
                    self.assertEqual(target.get_units(inst), units)
                    self.assertEqual(
                        lookup_multidict(target.default_latencies, inst, type(inst)), 4
                    )
                    for operands in ((0, 1, 2), (3, 0, 2), (3, 1, 0)):
                        consumer = parse(instruction(shape, rotation, *operands))
                        self.assertEqual(target.get_latency(inst, 0, consumer), 4)

    def optimize(self, target, lines, pipeline=False, selftest=False):
        core = SlothyBase(arch, target)
        core.config.inputs_are_outputs = True
        core.config.isa_check = "strict"
        core.config.selftest = selftest
        core.config.compiler_binary = "clang"
        core.config.variable_size = True
        core.config.constraints.stalls_allowed = 32
        core.config.sw_pipelining.enabled = pipeline
        core.config.timeout = 10
        self.assertTrue(core.optimize(SourceLine.read_multiline("\n".join(lines))))
        return core.result

    def test_scheduler_latency_and_throughput(self):
        for target in TARGETS:
            for shape in SHAPES:
                with self.subTest(target=target.__name__, shape=shape):
                    result = self.optimize(target, [instruction(shape)] * 3)
                    cycles = result.cycle_position_with_bubbles
                    self.assertEqual(
                        [cycles[i + 1] - cycles[i] for i in range(2)], [4, 4]
                    )
                    result = self.optimize(
                        target, [instruction(shape, 90, i, 30, 31) for i in range(8)]
                    )
                    cycles = result.cycle_position_with_bubbles.values()
                    self.assertEqual(
                        max(cycles) - min(cycles) + 1, 8 if target is cortex_a320 else 4
                    )
                    result = self.optimize(target, [instruction(shape)], pipeline=True)
                    self.assertEqual(result.cycles, 4)

    @unittest.skipUnless(HAS_TOOLS, "Requires LLVM assembler and Clang")
    def test_execution_against_complex_arithmetic(self):
        # Small exact binary values avoid FMA-rounding ambiguities in this oracle.
        for shape in SHAPES:
            count, fmt = int(shape[0]), "e" if shape.endswith("h") else "f"
            a = [1.0, 2.0] * (count // 2)
            b = [3.0, 4.0] * (count // 2)
            acc = [5.0, 6.0] * (count // 2)
            for rotation in ROTATIONS:
                with self.subTest(shape=shape, rotation=rotation):
                    code, offset = assemble([instruction(shape, rotation)])
                    uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
                    arch.unicorn_setup(uc)
                    uc.mem_map(0x10000, 0x1000)
                    uc.mem_write(0x10000, code)
                    for register, values in (
                        (UC_ARM64_REG_Q0, acc),
                        (UC_ARM64_REG_Q1, a),
                        (UC_ARM64_REG_Q2, b),
                    ):
                        data = struct.pack("<" + fmt * count, *values)
                        uc.reg_write(register, int.from_bytes(data, "little"))
                    uc.emu_start(0x10000 + offset, 0x10000 + len(code))
                    # Rotations select real/imaginary a and a signed/rotated b.
                    pair = {
                        0: (8.0, 10.0),
                        90: (-3.0, 12.0),
                        180: (2.0, 2.0),
                        270: (13.0, 0.0),
                    }[rotation]
                    expected = struct.pack("<" + fmt * count, *(pair * (count // 2)))
                    self.assertEqual(
                        uc.reg_read(UC_ARM64_REG_Q0), int.from_bytes(expected, "little")
                    )

    @unittest.skipUnless(HAS_TOOLS, "Requires LLVM assembler and Clang")
    def test_builtin_selftest_with_optimized_and_pipelined_code(self):
        for target in TARGETS:
            for shape in ("8h", "4s"):
                for pipeline in (False, True):
                    with self.subTest(
                        target=target.__name__, shape=shape, pipeline=pipeline
                    ):
                        self.optimize(
                            target,
                            [instruction(shape, r) for r in (0, 90)],
                            pipeline=pipeline,
                            selftest=True,
                        )


if __name__ == "__main__":
    unittest.main()
