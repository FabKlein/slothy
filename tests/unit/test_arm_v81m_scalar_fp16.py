"""Regression tests for scalar halfword loads and MVE scalar VFMA."""

from pathlib import Path
import unittest

from slothy.helper import SourceLine
from slothy.targets.arm_v81m import arch_v81m as arch
from slothy.targets.arm_v81m import cortex_m55r1 as target


def parse(text):
    return arch.Instruction.parser(SourceLine(text))[0]


class ScalarFP16Tests(unittest.TestCase):
    def test_scalar_vfma_dependencies(self):
        for datatype in ("f16", "f32"):
            with self.subTest(datatype=datatype):
                inst = parse(f"vfma.{datatype} q1, q0, r4")
                self.assertIsInstance(inst, arch.vfma_scalar)
                self.assertEqual(inst.args_in, ["q0", "r4"])
                self.assertEqual(inst.args_in_out, ["q1"])
                self.assertEqual(inst.args_out, [])
                self.assertEqual(
                    inst.arg_types_in, [arch.RegisterType.MVE, arch.RegisterType.GPR]
                )
                self.assertNotIn("r13", inst.args_in_restrictions[1])
                self.assertNotIn("r15", inst.args_in_restrictions[1])
                self.assertEqual(parse(inst.write()).args_in, inst.args_in)

    def test_symbolic_scalar_vfma(self):
        inst = parse("vfma.f16 q<acc>, q<weight>, r<sample>")
        self.assertEqual(inst.args_in, ["weight", "sample"])
        self.assertEqual(inst.args_in_out, ["acc"])
        self.assertEqual(parse(inst.write()).args_in, inst.args_in)

    def test_existing_vector_vfma(self):
        inst = parse("vfma.f16 q1, q0, q7")
        self.assertIsInstance(inst, arch.vfma)
        self.assertEqual(inst.args_in, ["q0", "q7"])

    def test_scalar_vfma_rejects_unsupported_precision(self):
        with self.assertRaises(arch.ParsingException):
            arch.vfma_scalar.make("vfma.f8 q1, q0, r4")

    def test_halfword_load_metadata_and_roundtrip(self):
        for text, offset in (
            ("ldrh r4, [r10]", 0),
            ("ldrh r4, [r10, #6]", 6),
            ("ldrh r4, [r10, #-2]", -2),
        ):
            with self.subTest(text=text):
                inst = parse(text)
                self.assertEqual(inst.args_in, ["r10"])
                self.assertEqual(inst.args_out, ["r4"])
                self.assertEqual(inst.addr, "r10")
                self.assertEqual(int(inst.pre_index), offset)
                self.assertIsNone(inst.increment)
                self.assertTrue(inst.is_scalar_load())
                self.assertTrue(inst.is_load())
                self.assertTrue(inst.is_load_store_instruction())
                self.assertFalse(inst.is_vector_load())
                self.assertEqual(int(parse(inst.write()).pre_index), offset)

    def test_offset_fixup_on_load_without_immediate(self):
        inst = parse("ldrh r4, [r10]")
        inst.pre_index = 6
        rewritten = parse(inst.write())
        self.assertIsInstance(rewritten, arch.ldrh)
        self.assertEqual(int(rewritten.pre_index), 6)

    def test_m55_scheduling(self):
        dst = parse("vfma.f16 q1, q0, r4")
        for text, unit, interval in (
            ("ldrh r4, [r10]", target.ExecutionUnit.LOAD, 1),
            ("ldrh r4, [r10, #2]", target.ExecutionUnit.LOAD, 1),
            ("vfma.f16 q1, q0, r4", target.ExecutionUnit.VEC_FPU, 2),
            ("vfma.f32 q1, q0, r4", target.ExecutionUnit.VEC_FPU, 2),
        ):
            with self.subTest(text=text):
                inst = parse(text)
                self.assertEqual(target.get_units(inst), [unit])
                self.assertEqual(target.get_inverse_throughput(inst), interval)
                self.assertEqual(target.get_latency(inst, 0, dst), 2)

    def test_complete_example_has_target_coverage(self):
        source = (
            Path(__file__).resolve().parents[2]
            / "examples/naive/armv8m"
            / "fp16_mac_6acc/fp16_mac_6acc_cm55.s"
        ).read_text()
        body = source.split("start:\n", 1)[1].rsplit("    le ", 1)[0]
        instructions = [parse(line) for line in body.splitlines() if line.strip()]
        self.assertEqual(len(instructions), 102)
        self.assertEqual(sum(isinstance(i, arch.vfma_scalar) for i in instructions), 54)
        self.assertEqual(sum(isinstance(i, arch.ldrh_no_imm) for i in instructions), 14)
        for inst in instructions:
            target.get_units(inst)
            target.get_inverse_throughput(inst)
            target.get_latency(inst, 0, instructions[0])


if __name__ == "__main__":
    unittest.main()
