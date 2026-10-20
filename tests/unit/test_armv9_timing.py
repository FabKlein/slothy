"""Operand-sensitive timing and resource regressions for A320/A520."""

import unittest

from slothy.core.core import SlothyBase
from slothy.helper import SourceLine, lookup_multidict
from slothy.targets.aarch64 import aarch64_neon as arch
from slothy.targets.aarch64 import cortex_a320, cortex_a520
from slothy.targets.exceptions import UnknownInstruction


def parse(text):
    return arch.Instruction.parser(SourceLine(text))[0]


TARGETS = (cortex_a320, cortex_a520)


class Armv9TimingTests(unittest.TestCase):
    def test_integer_mac_forwarding_and_exclusions(self):
        for target in TARGETS:
            for op in ("mla", "mls"):
                source = parse(f"{op} v0.4s, v1.4s, v2.4s")
                cases = (
                    (f"{op} v0.4s, v1.4s, v2.4s", 2),
                    (f"{op} v0.4S, v1.4S, v2.4S", 2),
                    (f"{op} v0.4s, v0.4s, v2.4s", 4),
                    (f"{op} v0.4s, v1.4s, v0.4s", 4),
                    (f"{op} v3.4s, v0.4s, v2.4s", 4),
                    (f"{op} v0.2s, v1.2s, v2.2s", 4),
                    ("add v3.4s, v0.4s, v2.4s", 4),
                    ("fmla v0.4s, v1.4s, v2.4s", 4),
                    (f"{op} v0.4s, v1.4s, v2.s[0]", 4),
                    (f"{'mls' if op == 'mla' else 'mla'} v0.4s, v1.4s, v2.4s", 4),
                )
                for text, expected in cases:
                    with self.subTest(target=target.__name__, op=op, consumer=text):
                        self.assertEqual(
                            target.get_latency(source, 0, parse(text)), expected
                        )
            for text in (
                "mla v0.2s, v1.2s, v2.2s",
                "mla v0.8h, v1.8h, v2.8h",
                "mla v0.4s, v1.4s, v2.s[0]",
                "fmla v0.4s, v1.4s, v2.4s",
                "fmls v0.4s, v1.4s, v2.4s",
            ):
                inst = parse(text)
                self.assertEqual(target.get_latency(inst, 0, inst), 4)

    def test_tbl_operand_paths(self):
        for target, normal, occupancy in ((cortex_a320, 5, 2), (cortex_a520, 8, 5)):
            for width in ("8b", "16b"):
                for register, expected in (("v0", normal), ("v1", 4), ("v3", normal)):
                    text = f"tbl {register}.{width}, {{v0.16b, v1.16b}}, v3.{width}"
                    inst = parse(text)
                    with self.subTest(target=target.__name__, instruction=text):
                        self.assertEqual(target.get_latency(inst, 0, inst), expected)
                        self.assertEqual(target.get_inverse_throughput(inst), occupancy)
                source = parse(f"tbl v1.{width}, {{v0.16b, v1.16b}}, v3.{width}")
                # Second-table and index dependencies together use the longer path.
                consumer = parse(f"tbl v2.{width}, {{v0.16b, v1.16b}}, v1.{width}")
                self.assertEqual(target.get_latency(source, 0, consumer), normal)
                consumer = parse("add v2.4s, v1.4s, v3.4s")
                self.assertEqual(target.get_latency(source, 0, consumer), normal)
            source = parse("tbl v1.8b, {v0.16b, v1.16b}, v3.8b")
            consumer = parse("tbl v1.16b, {v0.16b, v1.16b}, v3.16b")
            self.assertEqual(target.get_latency(source, 0, consumer), normal)

    def test_logical_forms_and_lookup_disjointness(self):
        for target in TARGETS:
            for op, width, expected in (
                ("and", "16b", 3),
                ("eor", "16b", 3),
                ("and", "8b", 1),
                ("eor", "8b", 1),
                ("orr", "16b", 1),
                ("bic", "16b", 1),
            ):
                inst = parse(f"{op} v0.{width}, v1.{width}, v2.{width}")
                with self.subTest(target=target.__name__, instruction=inst.write()):
                    self.assertEqual(target.get_latency(inst, 0, inst), expected)
                    self.assertEqual(target.get_inverse_throughput(inst), 1)
                    # Query the tables directly too: no hidden overlapping entries.
                    self.assertEqual(
                        lookup_multidict(target.default_latencies, inst, type(inst)),
                        expected,
                    )
                    units = target.get_units(inst)
                    if target is cortex_a520:
                        both = [target.ExecutionUnit.VEC0, target.ExecutionUnit.VEC1]
                        self.assertEqual(units, both if expected == 3 else [both])

    def test_a320_fp32_support_is_scoped(self):
        for op in ("fadd", "fmul"):
            inst = parse(f"{op} v0.4s, v1.4s, v2.4s")
            self.assertEqual(
                cortex_a320.get_units(inst), [cortex_a320.ExecutionUnit.VEC0]
            )
            self.assertEqual(cortex_a320.get_inverse_throughput(inst), 1)
            self.assertEqual(cortex_a320.get_latency(inst, 0, inst), 4)
            other = parse(f"{op} v0.2s, v1.2s, v2.2s")
            with self.assertRaises(UnknownInstruction):
                cortex_a320.get_latency(other, 0, other)

    def test_transfer_resources(self):
        for text, dual in (
            ("dup v0.4s, w1", True),
            ("dup v0.2s, w1", False),
            ("mov v0.s[0], w1", True),
            ("mov v0.s[1], w1", False),
            ("fmov x0, d1", False),
            ("fmov w0, s1", False),
            ("fmov d0, x1", True),
            ("fmov s0, w1", True),
        ):
            inst = parse(text)
            for target in TARGETS:
                with self.subTest(target=target.__name__, instruction=text):
                    self.assertEqual(target.get_inverse_throughput(inst), 1)
                    self.assertEqual(target.get_latency(inst, 0, inst), 3)
                    if target is cortex_a320:
                        self.assertEqual(
                            target.get_units(inst), [target.ExecutionUnit.VEC0]
                        )
                    else:
                        both = [target.ExecutionUnit.VEC0, target.ExecutionUnit.VEC1]
                        self.assertEqual(
                            target.get_units(inst), both if dual else [both]
                        )

    def test_fmov_dependency_paths_and_exclusions(self):
        for target in TARGETS:
            add_gap = 3 if target is cortex_a320 else 5
            cases = (
                ("fmov d0, x0", "fmov x1, d0", 3),
                ("fmov d0, x0", "add v1.2d, v0.2d, v2.2d", 3),
                ("fmov d0, x0", "fadd d1, d0, d2", 3),
                ("fmov x0, d0", "add x1, x0, #1", 3),
                ("fmov x0, d0", "adds x1, x0, #1", 3),
                ("fmov x0, d0", "mul x1, x0, x2", 3),
                ("fmov x0, d0", "fmov d1, x0", 4),
                ("add x0, x1, #1", "fmov d1, x0", add_gap),
                ("adds x0, x1, #1", "fmov d1, x0", add_gap),
                ("mul x0, x1, x2", "fmov d1, x0", 5),
                ("fmov s0, w0", "fmov w1, s0", 3),
                ("fmov w0, s0", "add w1, w0, #1", 3),
                ("fmov w0, s0", "fmov s1, w0", 4),
                ("add w0, w1, #1", "fmov s1, w0", add_gap),
                # No extension to unrelated registers, mixed widths, lane moves,
                # register ADD, or unmeasured 32-bit multiply consumers.
                ("fmov x0, d0", "fmov d1, x2", 3),
                ("fmov x0, d0", "fmov s1, w0", 3),
                ("fmov w0, s0", "fmov d1, x0", 3),
                ("fmov x0, d0", "fmov v1.d[1], x0", 3),
                ("add x0, x1, x2", "fmov d1, x0", 1),
                ("add x0, x1, #1", "fmov s1, w0", 1),
                ("mul w0, w1, w2", "fmov s1, w0", 3),
                ("mul x0, x1, x2", "add x1, x0, #1", 4),
            )
            for producer, consumer, expected in cases:
                with self.subTest(
                    target=target.__name__, producer=producer, consumer=consumer
                ):
                    self.assertEqual(
                        target.get_latency(parse(producer), 0, parse(consumer)),
                        expected,
                    )
            adds = parse("adds x0, x1, #1")
            self.assertEqual(adds.args_out, ["x0", "flags"])
            self.assertEqual(
                target.get_latency(adds, 1, parse("csel x2, x3, x4, eq")), 1
            )
            # Even a queried flag index cannot acquire a GPR transfer penalty.
            self.assertEqual(target.get_latency(adds, 1, parse("fmov d1, x0")), 1)
            forced = arch.fmov_0_force_output.make("fmov d1, x0", force=True)
            self.assertEqual(target.get_inverse_throughput(forced), 1)
            self.assertTrue(target.get_units(forced))
            self.assertEqual(target.get_latency(parse("fmov x0, d0"), 0, forced), 4)
            self.assertEqual(target.get_latency(forced, 0, parse("fmov x1, d1")), 3)

    def test_fmov_parser_outputs(self):
        inst = parse("fmov s0, w1")
        self.assertEqual(inst.args_in, ["x1"])
        self.assertEqual(inst.args_out, ["v0"])
        self.assertEqual(inst.args_in_out, [])
        self.assertIs(type(parse(inst.write())), arch.fmov_w_to_s)
        inst = parse("fadd d0, d1, d2")
        self.assertEqual(inst.args_in, ["v1", "v2"])
        self.assertEqual(inst.args_out, ["v0"])

    def test_fmov_scheduler_roundtrips(self):
        for target in TARGETS:
            add_gap = 3 if target is cortex_a320 else 5
            cases = (
                (["fmov d0, x0", "fmov x0, d0"], [3, 4]),
                (["fmov d0, x0", "fmov x0, d0", "add x0, x0, #1"], [3, 3, add_gap]),
                (["fmov d0, x0", "fmov x0, d0", "adds x0, x0, #1"], [3, 3, add_gap]),
                (["fmov d0, x0", "fmov x0, d0", "mul x0, x0, x1"], [3, 3, 5]),
                (["fmov d0, x0", "add v0.2d, v0.2d, v1.2d", "fmov x0, d0"], [3, 3, 4]),
                (["fmov d0, x0", "fadd d0, d0, d1", "fmov x0, d0"], [3, 4, 4]),
                (
                    [
                        "fmov d0, x0",
                        "add v0.2d, v0.2d, v1.2d",
                        "fmov x0, d0",
                        "add x0, x0, #1",
                    ],
                    [3, 3, 3, add_gap],
                ),
                (["fmov s0, w0", "fmov w0, s0"], [3, 4]),
                (["fmov s0, w0", "fmov w0, s0", "add w0, w0, #1"], [3, 3, add_gap]),
            )
            for body, gaps in cases:
                for rename in (False, True):
                    with self.subTest(target=target.__name__, body=body, rename=rename):
                        result = self.optimize(target, body * 3, rename=rename)
                        cycles = result.cycle_position_with_bubbles
                        self.assertEqual(
                            [
                                cycles[i + 1] - cycles[i]
                                for i in range(3 * len(body) - 1)
                            ],
                            (gaps * 3)[:-1],
                        )
                with self.subTest(target=target.__name__, body=body, pipeline=True):
                    result = self.optimize(target, body, rename=True, pipeline=True)
                    self.assertEqual(result.cycles, sum(gaps))

    def test_fmov_scheduler_throughput(self):
        for target in TARGETS:
            for template, expected in (
                ("fmov d{}, x20", 8 if target is cortex_a320 else 4),
                ("fmov x{}, d31", 8),
                ("fmov s{}, w20", 8 if target is cortex_a320 else 4),
                ("fmov w{}, s31", 8),
            ):
                with self.subTest(target=target.__name__, instruction=template):
                    result = self.optimize(
                        target, [template.format(i) for i in range(8)]
                    )
                    cycles = result.cycle_position_with_bubbles.values()
                    self.assertEqual(max(cycles) - min(cycles) + 1, expected)

    @staticmethod
    def optimize(target, lines, rename=False, pipeline=False):
        core = SlothyBase(arch, target)
        core.config.inputs_are_outputs = True
        core.config.outputs = {
            reg
            for inst in map(parse, lines)
            for reg in inst.args_out + inst.args_in_out
        }
        core.config.constraints.allow_renaming = rename
        core.config.variable_size = True
        core.config.constraints.stalls_allowed = 40
        core.config.sw_pipelining.enabled = pipeline
        core.config.selftest = False
        core.config.timeout = 10
        if not core.optimize(SourceLine.read_multiline("\n".join(lines))):
            raise AssertionError("Optimization failed")
        return core.result

    def test_scheduler_dependency_gaps(self):
        for target in TARGETS:
            for rename in (False, True):
                for text, gap in (
                    ("mla v0.4s, v1.4s, v2.4s", 2),
                    ("mls v0.4s, v1.4s, v2.4s", 2),
                    ("mla v0.4s, v0.4s, v2.4s", 4),
                    ("fmla v0.4s, v1.4s, v2.4s", 4),
                    ("and v0.16b, v0.16b, v1.16b", 3),
                    ("tbl v1.16b, {v0.16b, v1.16b}, v3.16b", 4),
                    (
                        "tbl v3.8b, {v0.16b, v1.16b}, v3.8b",
                        5 if target is cortex_a320 else 8,
                    ),
                ):
                    with self.subTest(
                        target=target.__name__, rename=rename, instruction=text
                    ):
                        result = self.optimize(target, [text] * 3, rename)
                        cycles = result.cycle_position_with_bubbles
                        self.assertEqual(
                            [cycles[i + 1] - cycles[i] for i in range(2)], [gap] * 2
                        )

    def test_scheduler_independent_stream_rates(self):
        for target in TARGETS:
            for template in (
                "and v{}.16b, v30.16b, v31.16b",
                "eor v{}.16b, v30.16b, v31.16b",
                "dup v{}.4s, w0",
                "mov v{}.s[0], w0",
                "fadd v{}.4s, v30.4s, v31.4s",
                "fmul v{}.4s, v30.4s, v31.4s",
                "mla v{}.4s, v30.4s, v31.4s",
                "mls v{}.4s, v30.4s, v31.4s",
            ):
                with self.subTest(target=target.__name__, instruction=template):
                    result = self.optimize(
                        target, [template.format(i) for i in range(8)]
                    )
                    cycles = result.cycle_position_with_bubbles.values()
                    self.assertEqual(
                        max(cycles) - min(cycles) + 1, 8 if target is cortex_a320 else 4
                    )

    def test_scheduler_tbl_resource_occupancy(self):
        for target in TARGETS:
            lines = [f"tbl v{i}.16b, {{v28.16b, v29.16b}}, v30.16b" for i in range(8)]
            result = self.optimize(target, lines)
            cycles = sorted(result.cycle_position_with_bubbles.values())
            expected = (
                list(range(0, 16, 2))
                if target is cortex_a320
                else [0, 0, 5, 5, 10, 10, 15, 15]
            )
            self.assertEqual([cycle - cycles[0] for cycle in cycles], expected)

    def test_software_pipeline_accumulator_recurrence(self):
        for target in TARGETS:
            for text, gap in (
                ("mla v0.4s, v1.4s, v2.4s", 2),
                ("mla v0.4s, v0.4s, v2.4s", 4),
            ):
                with self.subTest(target=target.__name__, instruction=text):
                    result = self.optimize(
                        target, [text] * 2, rename=True, pipeline=True
                    )
                    self.assertEqual(result.cycles, 2 * gap)


if __name__ == "__main__":
    unittest.main()
