"""Ordered FP32 min/max, including result-bit semantics under FPCR.AH=1."""

import logging
import shutil
import struct
import unittest

from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM
from unicorn import arm64_const as regs

from slothy.core.config import Config
from slothy.core.core import SlothyBase
from slothy.helper import LLVM_Mc, SourceLine, lookup_multidict
from slothy.targets.aarch64 import aarch64_neon as arch
from slothy.targets.aarch64 import cortex_a320, cortex_a520
from slothy.targets.aarch64.isa import (
    UnsupportedISA,
    instruction_features,
    validate_instruction_features,
)
from slothy.targets.exceptions import FatalParsingException, ParsingException

LOGGER = logging.getLogger(__name__)
TARGETS = (cortex_a320, cortex_a520)
HAS_TOOLS = shutil.which("llvm-mc") and shutil.which("clang")
MASK = 0xFFFFFFFF
CASES = (
    (0x00000000, 0x80000000),  # signed-zero ties, both source orders
    (0x80000000, 0x00000000),
    (0x7FC12345, 0x3F800000),  # quiet NaNs, distinct payloads and signs
    (0x3F800000, 0x7FC12345),
    (0x7FC12345, 0xFFC54321),
    (0xFFC54321, 0x7FC12345),
    (0x3F800000, 0x40000000),
    (0xC0000000, 0x3F800000),
    (0x7F800000, 0x3F800000),  # infinities
    (0xFF800000, 0x3F800000),
    (0x7F800000, 0xFF800000),
    (0xFF800000, 0x7F800000),
    (0x00000001, 0x80000001),  # subnormals, FZ/FIZ disabled
    (0x80000000, 0x00000001),
    (0x40800000, 0x40800000),
    (0xC0800000, 0xC0000000),
)


def parse(text):
    return arch.Instruction.parser(SourceLine(text))[0]


def minmax_bits(left, right, minimum, ah, dn):
    """Result bits only: fixed FPCR, FZ/FIZ=0, exceptions nontrapping.

    AH selects the second operand for either NaN or a zero tie (Arm ARM
    102105_I.a_06, section 2.175). This is not an FPSR/trap model.
    """
    nan_l = (left & 0x7FFFFFFF) > 0x7F800000
    nan_r = (right & 0x7FFFFFFF) > 0x7F800000
    zeros = (left & 0x7FFFFFFF) == 0 and (right & 0x7FFFFFFF) == 0
    if ah and (nan_l or nan_r or zeros):
        return right
    if nan_l or nan_r:
        if dn:
            return 0x7FC00000
        # With AH=0, signaling NaNs take priority, then source order.
        for value, is_nan in ((left, nan_l), (right, nan_r)):
            if is_nan and not value & 0x00400000:
                return value | 0x00400000
        return (left if nan_l else right) | 0x00400000
    if zeros:
        return (left | right) if minimum else (left & right)
    a, b = (struct.unpack("<f", struct.pack("<I", value))[0] for value in (left, right))
    return left if (a < b if minimum else a > b) else right


def vector_bits(left, right, count, minimum, ah, dn):
    return sum(
        minmax_bits(
            (left >> (32 * i)) & MASK, (right >> (32 * i)) & MASK, minimum, ah, dn
        )
        << (32 * i)
        for i in range(count)
    )


def assemble(lines):
    return LLVM_Mc.assemble(
        lines, arch.llvm_mc_arch, arch.llvm_mc_attr, LOGGER, preprocessor="clang"
    )


def emulator(code):
    uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    arch.unicorn_setup(uc)
    uc.mem_map(0x10000, 0x4000)
    uc.mem_write(0x10000, code)
    return uc


class FPMinMaxTests(unittest.TestCase):
    def optimize(self, target, text, pipeline=False):
        core = SlothyBase(arch, target)
        core.config.inputs_are_outputs = True
        core.config.isa_check = "strict"
        core.config.selftest = False  # independent execution checks below
        core.config.variable_size = True
        core.config.constraints.stalls_allowed = 32
        core.config.sw_pipelining.enabled = pipeline
        if pipeline:
            core.config.sw_pipelining.min_overlapping = 1
        core.config.timeout = 10
        self.assertTrue(core.optimize(SourceLine.read_multiline(text)))
        return core.result

    def test_json_roles_roundtrip_renaming_and_isa(self):
        for op, cls in (("fmax", arch.vmaxf), ("fmin", arch.vminf)):
            spec = next(s for s in arch._NEON_SPECS if s["name"] == cls.__name__)
            self.assertEqual(spec["inputs"], ["Vb", "Vc"])
            for shape in ("2s", "4s", "2S", "4S"):
                for dest in (0, 1, 2):
                    inst = parse(f"{op} v{dest}.{shape}, v1.{shape}, v2.{shape}")
                    self.assertIs(type(inst), cls)
                    self.assertEqual(inst.args_in, ["v1", "v2"])
                    self.assertEqual(inst.args_out, [f"v{dest}"])
                    self.assertEqual(inst.args_in_out, [])
                    self.assertEqual(parse(inst.write()).args_in, ["v1", "v2"])
                    self.assertEqual(
                        instruction_features(inst), {"FEAT_FP", "FEAT_AdvSIMD"}
                    )
                    for target in TARGETS:
                        config = Config(arch, target, LOGGER)
                        config.isa_check = "strict"
                        config.isa_features = {"FEAT_FP16": False}
                        validate_instruction_features([inst], config, LOGGER)
                        config.isa_features = {"FEAT_AdvSIMD": False}
                        with self.assertRaises(UnsupportedISA):
                            validate_instruction_features([inst], config, LOGGER)
            inst = parse(f"{op} V<out>.4s, V<first>.4s, V<second>.4s")
            self.assertEqual(inst.args_in, ["first", "second"])
            inst.args_in = ["v27", "v3"]  # deliberately not register-number order
            inst.args_out = ["v9"]
            self.assertEqual(parse(inst.write()).args_in, ["v27", "v3"])
            inst.args_in.reverse()
            self.assertEqual(parse(inst.write()).args_in, ["v3", "v27"])

    def test_reject_other_forms_and_revalidate_writer(self):
        for op, cls in (("fmax", arch.vmaxf), ("fmin", arch.vminf)):
            for shape in ("4h", "8h", "2d", "16b", "s", "8s"):
                with self.assertRaises(ParsingException):
                    cls.make(f"{op} v0.{shape}, v1.{shape}, v2.{shape}")
            for text in (
                f"{op} v0.4s, v1.2s, v2.4s",
                f"{op} s0, s1, s2",
                f"{op} v0.4s, v1.4s, v2.s[0]",
            ):
                with self.assertRaises((ParsingException, FatalParsingException)):
                    cls.make(text)
            inst = parse(f"{op} v0.4s, v1.4s, v2.4s")
            inst.datatype = ["2d"] * 3
            with self.assertRaises(ParsingException):
                inst.write()

    def test_guide_timings_and_dependency_paths(self):
        for target in TARGETS:
            for op in ("fmax", "fmin"):
                for shape in ("2s", "4s"):
                    inst = parse(f"{op} v0.{shape}, v1.{shape}, v2.{shape}")
                    self.assertEqual(target.get_inverse_throughput(inst), 1)
                    units = [target.ExecutionUnit.VEC0]
                    if target is cortex_a520:
                        units.append(target.ExecutionUnit.VEC1)
                    self.assertEqual(target.get_units(inst), units)
                    self.assertEqual(
                        lookup_multidict(target.default_latencies, inst, type(inst)), 4
                    )
                    for consumer in (
                        f"{op} v3.{shape}, v0.{shape}, v2.{shape}",
                        f"{op} v3.{shape}, v1.{shape}, v0.{shape}",
                    ):
                        self.assertEqual(
                            target.get_latency(inst, 0, parse(consumer)), 4
                        )

    def test_dependent_and_independent_schedules(self):
        for target in TARGETS:
            for op in ("fmax", "fmin"):
                for shape in ("2s", "4s"):
                    for operands in ((0, 30), (30, 0)):
                        text = (
                            f"{op} v0.{shape}, "
                            f"v{operands[0]}.{shape}, v{operands[1]}.{shape}"
                        )
                        result = self.optimize(target, "\n".join([text] * 3))
                        cycles = result.cycle_position_with_bubbles
                        self.assertEqual(
                            [cycles[i + 1] - cycles[i] for i in (0, 1)], [4, 4]
                        )
                    text = "\n".join(
                        f"{op} v{i}.{shape}, v{i}.{shape}, v31.{shape}"
                        for i in range(8)
                    )
                    cycles = self.optimize(
                        target, text
                    ).cycle_position_with_bubbles.values()
                    self.assertEqual(
                        max(cycles) - min(cycles) + 1, 8 if target is cortex_a320 else 4
                    )

    def test_ah_reference_cases_detect_source_swaps(self):
        for minimum in (False, True):
            for dn in (False, True):
                for left, right in CASES[:6]:
                    self.assertEqual(minmax_bits(left, right, minimum, True, dn), right)
                self.assertEqual(
                    minmax_bits(0, 0x80000000, minimum, False, dn),
                    0x80000000 if minimum else 0,
                )
                self.assertNotEqual(
                    minmax_bits(0x7FC12345, 0x3F800000, minimum, True, dn),
                    minmax_bits(0x3F800000, 0x7FC12345, minimum, True, dn),
                )

    def check_unicorn_lanes(self, ah):
        for op in ("fmax", "fmin"):
            for count in (2, 4):
                code, offset = assemble(
                    SourceLine.read_multiline(
                        f"{op} v0.{count}s, v1.{count}s, v2.{count}s"
                    )
                )
                for dn in (False, True):
                    for start in range(0, len(CASES), count):
                        pairs = CASES[start : start + count]
                        left = sum(a << (32 * i) for i, (a, _) in enumerate(pairs))
                        right = sum(b << (32 * i) for i, (_, b) in enumerate(pairs))
                        uc = emulator(code)
                        uc.reg_write(
                            regs.UC_ARM64_REG_FPCR, (int(ah) << 1) | (int(dn) << 25)
                        )
                        self.assertEqual(
                            uc.reg_read(regs.UC_ARM64_REG_FPCR),
                            (int(ah) << 1) | (int(dn) << 25),
                        )
                        uc.reg_write(regs.UC_ARM64_REG_Q0, (1 << 128) - 1)
                        uc.reg_write(regs.UC_ARM64_REG_Q1, left)
                        uc.reg_write(regs.UC_ARM64_REG_Q2, right)
                        uc.emu_start(0x10000 + offset, 0x10000 + len(code))
                        self.assertEqual(
                            uc.reg_read(regs.UC_ARM64_REG_Q0),
                            vector_bits(left, right, count, op == "fmin", ah, dn),
                        )

    @unittest.skipUnless(HAS_TOOLS, "Requires LLVM assembler and Clang")
    def test_unicorn_ah0_result_bits(self):
        self.check_unicorn_lanes(False)

    @unittest.skipUnless(HAS_TOOLS, "Requires LLVM assembler and Clang")
    def test_unicorn_ah1_result_bits_if_supported(self):
        uc = emulator(b"\x1f\x20\x03\xd5")
        uc.reg_write(regs.UC_ARM64_REG_FPCR, 2)
        if not uc.reg_read(regs.UC_ARM64_REG_FPCR) & 2:
            self.skipTest(
                "Installed Unicorn does not implement FPCR.AH; "
                "reference-model tests still run"
            )
        self.check_unicorn_lanes(True)

    def run_model(self, lines, data, ah, dn):
        """Interpret only pair loads, Q stores and ordered min/max."""
        pointers = {"x0": 0x20000, "x1": 0x21000}
        vectors = {f"v{i}": 0 for i in range(32)}
        output = bytearray([0xA5] * (len(data) + 32))
        for line in lines:
            if not line.text.strip():
                continue
            inst = arch.Instruction.parser(line)[0]
            if isinstance(inst, (arch.vmaxf, arch.vminf)):
                left, right = (vectors[reg] for reg in inst.args_in)
                vectors[inst.args_out[0]] = vector_bits(
                    left,
                    right,
                    int(inst.datatype[0][0]),
                    isinstance(inst, arch.vminf),
                    ah,
                    dn,
                )
            else:
                self.assertIsInstance(inst, (arch.Ldp_Q, arch.Str_Q))
                address = pointers[inst.addr] + int(inst.pre_index or 0)
                if isinstance(inst, arch.Ldp_Q):
                    offset = address - 0x20000
                    self.assertTrue(0 <= offset <= len(data) - 32)
                    for i, reg in enumerate(inst.args_out):
                        vectors[reg] = int.from_bytes(
                            data[offset + 16 * i : offset + 16 * i + 16], "little"
                        )
                else:
                    offset = address - 0x21000
                    self.assertTrue(0 <= offset <= len(data) - 16)
                    output[offset : offset + 16] = vectors[inst.args_in[0]].to_bytes(
                        16, "little"
                    )
                pointers[inst.addr] += int(inst.increment or 0)
        self.assertEqual(
            pointers, {"x0": 0x20000 + len(data), "x1": 0x21000 + len(data)}
        )
        self.assertEqual(output[-32:], bytes([0xA5]) * 32)
        return bytes(output[:-32])

    @unittest.skipUnless(HAS_TOOLS, "Requires LLVM assembler and Clang")
    def test_reordered_and_pipelined_order_with_ah_reference(self):
        for target in TARGETS:
            for count in (2, 4):
                body = (
                    "ldp q0, q1, [x0], #32\n"
                    f"fmax v2.{count}s, v0.{count}s, v1.{count}s\n"
                    f"fmin v3.{count}s, v1.{count}s, v0.{count}s\n"
                    "str q2, [x1], #16\n"
                    "str q3, [x1], #16\n"
                )
                data = b""
                for i in range(8):
                    pairs = [CASES[(i * count + j) % len(CASES)] for j in range(4)]
                    data += struct.pack(
                        "<8I", *(a for a, _ in pairs), *(b for _, b in pairs)
                    )
                for pipeline in (False, True):
                    result = self.optimize(target, body, pipeline)
                    if pipeline:
                        self.assertGreater(result.num_exceptional_iterations, 0)
                        original, optimized = result.get_fully_unrolled_loop(8)
                    else:
                        original = SourceLine.read_multiline(body) * 8
                        optimized = result.code * 8
                    for ah in (False, True):
                        for dn in (False, True):
                            expected = b""
                            for i in range(8):
                                left = int.from_bytes(
                                    data[32 * i : 32 * i + 16], "little"
                                )
                                right = int.from_bytes(
                                    data[32 * i + 16 : 32 * i + 32], "little"
                                )
                                expected += vector_bits(
                                    left, right, count, False, ah, dn
                                ).to_bytes(16, "little")
                                expected += vector_bits(
                                    right, left, count, True, ah, dn
                                ).to_bytes(16, "little")
                            for lines in (original, optimized):
                                self.assertEqual(
                                    self.run_model(lines, data, ah, dn), expected
                                )
                                if ah:
                                    continue  # AH=1 execution is capability-gated above
                                code, offset = assemble(lines)
                                uc = emulator(code)
                                uc.mem_map(0x20000, 0x2000)
                                uc.mem_write(0x20000, data)
                                uc.mem_write(0x21000, bytes([0xA5]) * (len(data) + 32))
                                uc.reg_write(regs.UC_ARM64_REG_X0, 0x20000)
                                uc.reg_write(regs.UC_ARM64_REG_X1, 0x21000)
                                uc.reg_write(regs.UC_ARM64_REG_FPCR, int(dn) << 25)
                                uc.emu_start(0x10000 + offset, 0x10000 + len(code))
                                self.assertEqual(
                                    bytes(uc.mem_read(0x21000, len(data))), expected
                                )
                                self.assertEqual(
                                    bytes(uc.mem_read(0x20000, len(data))), data
                                )
                                self.assertEqual(
                                    bytes(uc.mem_read(0x21000 + len(data), 32)),
                                    bytes([0xA5]) * 32,
                                )
                                for reg, address in (
                                    (regs.UC_ARM64_REG_X0, 0x20000),
                                    (regs.UC_ARM64_REG_X1, 0x21000),
                                ):
                                    self.assertEqual(
                                        uc.reg_read(reg), address + len(data)
                                    )


if __name__ == "__main__":
    unittest.main()
