"""Compatibility of upstream instructions with the fork's scalar generator."""

import unittest

from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as arch
from slothy.targets.aarch64 import cortex_a55, cortex_a320, cortex_a520


def parse(text):
    return arch.Instruction.parser(SourceLine(text))[0]


class MainMergeCompatibilityTests(unittest.TestCase):
    def test_upstream_scalar_forms_and_a55_timings(self):
        for text, cls in (
            ("lsr x0, x1, #3", arch.lsr_imm),
            ("lsr x0, x1, x2", arch.lsr),
            ("asr x0, x1, #3", arch.asr_imm),
            ("asr x0, x1, x2", arch.asr),
            ("sxtb x0, w1", arch.sxtb),
            ("uxtb w0, w1", arch.uxtb),
            ("ldr x0, =123", arch.ldr_const),
            ("movk x0, #1, lsl #16", arch.movk_imm_lsl),
            ("ldrb w0, [x1]", arch.w_ldrb),
            ("ldp w0, w1, [x2]", arch.w_ldp),
            ("stp w0, w1, [x2]", arch.w_stp),
            ("crc32x w0, w1, x2", arch.crc32x),
        ):
            with self.subTest(text=text):
                inst = parse(text)
                self.assertIsInstance(inst, cls)
                self.assertIsInstance(parse(inst.write()), cls)
                cortex_a55.get_units(inst)
                cortex_a55.get_inverse_throughput(inst)
                cortex_a55.get_latency(inst, 0, inst)

    def test_generated_flag_dependencies(self):
        self.assertIn("flags", parse("cmp x0, #1").args_out)
        self.assertIn("flags", parse("subs w0, w1, #1").args_out)
        self.assertIn("flags", parse("csel x0, x1, x2, eq").args_in)
        self.assertIn("flags", parse("fcsel d0, d1, d2, eq").args_in)

    def test_integer_mac_still_parses_with_fp_subclasses(self):
        for mnemonic, cls in (
            ("mla", arch.vmla),
            ("mls", arch.vmls),
            ("fmla", arch.vfmla),
            ("fmls", arch.vfmls),
        ):
            inst = parse(f"{mnemonic} v0.4s, v1.4s, v2.4s")
            self.assertIs(type(inst), cls)
            self.assertIs(arch.find_class(inst), cls)
            self.assertEqual(inst.args_in_out, ["v0"])

    def test_a55_family_entries_do_not_overlap(self):
        for text, interval, latency in (
            ("ldp q0, q1, [x2, #32]", 4, 6),
            ("ldp q0, q1, [x2], #32", 2, 4),
            ("ld2 {v0.s, v1.s}[1], [x2], #8", 1, 3),
            ("uxtl v0.8h, v1.8b", 1, 2),
        ):
            inst = parse(text)
            cortex_a55.get_units(inst)
            self.assertEqual(cortex_a55.get_inverse_throughput(inst), interval)
            self.assertEqual(cortex_a55.get_latency(inst, 0, inst), latency)

    def test_fork_targets_use_upstream_scalar_names(self):
        for target in (cortex_a320, cortex_a520):
            for text in ("lsr x0, x1, #3", "fcsel d0, d1, d2, eq"):
                inst = parse(text)
                target.get_units(inst)
                target.get_inverse_throughput(inst)
                target.get_latency(inst, 0, inst)


if __name__ == "__main__":
    unittest.main()
