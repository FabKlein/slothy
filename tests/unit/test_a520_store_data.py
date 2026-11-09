"""Scoped A520 store-data scheduling approximation and exclusions."""

import unittest

from slothy.core.core import SlothyBase
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as arch
from slothy.targets.aarch64 import cortex_a55, cortex_a320, cortex_a520


def parse(text):
    return arch.Instruction.parser(SourceLine(text))[0]


PRODUCERS = (
    "bic v0.4s, #0x80, lsl #24",
    "bic v0.8h, #0x80, lsl #8",
    "bic v0.16b, v1.16b, v2.16b",
    "and v0.16b, v1.16b, v2.16b",
    "orr v0.16b, v1.16b, v2.16b",
    "eor v0.16b, v1.16b, v2.16b",
    "add v0.16b, v1.16b, v2.16b",
    "add v0.8h, v1.8h, v2.8h",
    "add v0.4s, v1.4s, v2.4s",
    "add v0.2d, v1.2d, v2.2d",
    "sub v0.4s, v1.4s, v2.4s",
    "sub v0.16b, v1.16b, v2.16b",
    "sub v0.8h, v1.8h, v2.8h",
    "sub v0.2d, v1.2d, v2.2d",
)
STORES = tuple(
    f"st1 {{v0.{width}}}, [x2], #16" for width in ("16b", "8h", "4s", "2d")
) + ("str q0, [x2], #16",)


class A520StoreDataTests(unittest.TestCase):
    def test_full_width_producer_and_store_arrangements(self):
        for producer in PRODUCERS:
            for consumer in STORES:
                with self.subTest(producer=producer, consumer=consumer):
                    src, dst = parse(producer), parse(consumer)
                    self.assertEqual(cortex_a520.get_latency(src, 0, dst), 4)
                    for idx in (-1, 1):
                        self.assertEqual(cortex_a520.get_latency(src, idx, dst), 3)
                    for target in (cortex_a55, cortex_a320):
                        self.assertEqual(
                            target.get_latency(src, 0, dst),
                            target.get_latency(src, 0, src),
                        )
            for consumer in (
                "st1 {v1.16b}, [x2], #16",
                "str q1, [x2], #16",
                "str q0, [x2]",
                "str q0, [x2, #16]!",
                "st1 {v0.b}[0], [x2], #1",
                "st1 {v0.s}[0], [x2], #4",
                "st1 {v0.8b}, [x2], #8",
                "st1 {v0.4h}, [x2], #8",
                "st1 {v0.2s}, [x2], #8",
                "stp q0, q1, [x2], #32",
                "add v3.16b, v0.16b, v2.16b",
            ):
                with self.subTest(producer=producer, excluded_consumer=consumer):
                    self.assertEqual(
                        cortex_a520.get_latency(parse(producer), 0, parse(consumer)), 3
                    )

    def test_store_data_path_and_exclusions(self):
        for producer, consumer, expected in (
            ("bic v0.4s, #0x80, lsl #24", "st1 {v0.4s}, [x2], #16", 4),
            ("bic v0.4S, #0x80, LSL #24", "st1 {v0.4S}, [x2], #16", 4),
            ("bic v0.4s, #1, lsl #0", "str q0, [x2], #16", 4),
            ("bic v0.4s, #0x80, lsl #24", "st1 {v1.4s}, [x2], #16", 3),
            ("bic v0.4s, #0x80, lsl #24", "str q1, [x2], #16", 3),
            ("bic v0.4s, #0x80, lsl #24", "bic v0.4s, #0x80, lsl #24", 3),
            ("bic v0.4s, #0x80, lsl #24", "add v1.4s, v0.4s, v2.4s", 3),
            ("bic v0.4s, #0x80, lsl #24", "str q0, [x2]", 3),
            ("bic v0.4s, #0x80, lsl #24", "str q0, [x2, #16]!", 3),
            ("bic v0.4s, #0x80, lsl #24", "st1 {v0.s}[0], [x2], #4", 3),
            ("bic v0.4s, #0x80, lsl #24", "st1 {v0.2s}, [x2], #8", 3),
            ("bic v0.4s, #0x80, lsl #24", "stp q0, q1, [x2], #32", 3),
            ("bic v0.2s, #0x80, lsl #24", "st1 {v0.2s}, [x2], #8", 1),
            ("bic v0.4h, #0x80, lsl #8", "str q0, [x2], #16", 1),
            ("bic v0.8b, v1.8b, v2.8b", "str q0, [x2], #16", 1),
            ("and v0.16b, v1.16b, v2.16b", "str q0, [x2], #16", 4),
            ("orr v0.16B, v1.16B, v2.16B", "st1 {v0.8H}, [x2], #16", 4),
            ("add v0.8H, v1.8H, v2.8H", "st1 {v0.16B}, [x2], #16", 4),
            ("sub v0.4S, v1.4S, v2.4S", "str q0, [x2], #16", 4),
            (
                "add v<dst>.4s, v<lhs>.4s, v<rhs>.4s",
                "st1 {v<dst>.8h}, [x<base>], #16",
                4,
            ),
            (
                "add v<dst>.4s, v<lhs>.4s, v<rhs>.4s",
                "st1 {v<other>.8h}, [x<base>], #16",
                3,
            ),
            ("orr v0.8b, v1.8b, v2.8b", "str q0, [x2], #16", 1),
            ("orr v0.4s, #0x80", "str q0, [x2], #16", 1),
            ("add v0.8b, v1.8b, v2.8b", "str q0, [x2], #16", 2),
            ("add v0.4h, v1.4h, v2.4h", "str q0, [x2], #16", 2),
            ("add v0.2s, v1.2s, v2.2s", "str q0, [x2], #16", 2),
            ("sub v0.8b, v1.8b, v2.8b", "str q0, [x2], #16", 2),
            ("sub v0.4h, v1.4h, v2.4h", "str q0, [x2], #16", 2),
            ("sub v0.2s, v1.2s, v2.2s", "str q0, [x2], #16", 2),
            ("fadd v0.4s, v1.4s, v2.4s", "str q0, [x2], #16", 4),
            ("mul v0.4s, v1.4s, v2.4s", "str q0, [x2], #16", 4),
            ("mla v0.4s, v1.4s, v2.4s", "str q0, [x2], #16", 4),
            ("dup v0.4s, w0", "str q0, [x2], #16", 3),
            ("ldr q0, [x0], #16", "str q0, [x2], #16", 3),
            ("add x2, x2, #16", "str q0, [x2], #16", 1),
            ("ldp q0, q1, [x0], #32", "str q0, [x2], #16", 3),
        ):
            with self.subTest(producer=producer, consumer=consumer):
                self.assertEqual(
                    cortex_a520.get_latency(parse(producer), 0, parse(consumer)),
                    expected,
                )
        producer = parse("bic v0.4s, #0x80, lsl #24")
        consumer = parse("st1 {v0.4s}, [x2], #16")
        for idx in (-1, 1):
            self.assertEqual(cortex_a520.get_latency(producer, idx, consumer), 3)
        for target in (cortex_a55, cortex_a320):
            self.assertEqual(target.get_latency(producer, 0, consumer), 1)
        self.assertEqual(cortex_a520.get_inverse_throughput(producer), 1)
        self.assertEqual(
            cortex_a520.get_units(producer),
            [cortex_a520.ExecutionUnit.VEC0, cortex_a520.ExecutionUnit.VEC1],
        )

    @staticmethod
    def schedule(lines, *, rename=False, pipeline=False):
        core = SlothyBase(arch, cortex_a520)
        core.config.inputs_are_outputs = True
        core.config.outputs = {
            reg
            for inst in map(parse, lines)
            for reg in inst.args_out + inst.args_in_out
        }
        core.config.constraints.allow_renaming = rename
        core.config.constraints.allow_reordering = False
        core.config.sw_pipelining.enabled = pipeline
        core.config.variable_size = True
        core.config.constraints.stalls_allowed = 40
        core.config.selftest = False
        core.config.timeout = 10
        if not core.optimize(SourceLine.read_multiline("\n".join(lines))):
            raise AssertionError("Optimization failed")
        return core.result

    def test_add_sub_full_width_symmetry(self):
        for width in ("16b", "8h", "4s", "2d", "16B", "8H", "4S", "2D"):
            add = parse(f"add v0.{width}, v1.{width}, v2.{width}")
            sub = parse(f"sub v0.{width}, v1.{width}, v2.{width}")
            with self.subTest(width=width):
                self.assertEqual(cortex_a520.get_units(add), cortex_a520.get_units(sub))
                self.assertEqual(
                    cortex_a520.get_inverse_throughput(add),
                    cortex_a520.get_inverse_throughput(sub),
                )
                for inst in (add, sub):
                    self.assertEqual(cortex_a520.get_latency(inst, 0, inst), 3)
                    for store in STORES:
                        self.assertEqual(
                            cortex_a520.get_latency(inst, 0, parse(store)), 4
                        )

    def test_dependent_and_independent_store_schedules(self):
        for producer in PRODUCERS:
            for rename in (False, True):
                for store in STORES:
                    with self.subTest(producer=producer, rename=rename, store=store):
                        result = self.schedule([producer, store], rename=rename)
                        positions = result.cycle_position_with_bubbles
                        self.assertEqual(positions[1] - positions[0], 4)
                result = self.schedule(
                    [producer, "st1 {v3.4s}, [x2], #16"], rename=rename
                )
                self.assertEqual(result.cycles, 1)
            inst = parse(producer)
            if inst.args_out:
                # Make register ALU chains consume the preceding result.
                inst.args_in[0] = inst.args_out[0]
            result = self.schedule([inst.write()] * 2)
            positions = result.cycle_position_with_bubbles
            self.assertEqual(positions[1] - positions[0], 3)

    def test_software_pipeline_store_data_dependency(self):
        for producer in PRODUCERS:
            for store in STORES:
                with self.subTest(producer=producer, store=store):
                    result = self.schedule(
                        [producer, store], rename=True, pipeline=True
                    )
                    # Preserve the store-data gap each trip, including with renaming.
                    self.assertEqual(result.cycles, 5)


if __name__ == "__main__":
    unittest.main()
