"""Regression checks for the shared scalar/NEON instruction generator."""

import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from aarch64_model_snapshot import observe
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as arch
from slothy.targets.aarch64 import aarch64 as scalar
from slothy.targets.aarch64.instruction_loader import (
    generate_instruction_classes,
    read_instruction_specs,
)


class FakeInstruction:
    """Isolated builder so loader tests do not pollute parser discovery."""

    @staticmethod
    def build(cls, src):
        return SimpleNamespace(
            immediate=16,
            args_in=["x0"],
            args_in_out=["x1"],
            datatype=src,
            args_in_restrictions=[None] * len(getattr(cls, "inputs", [])),
            args_out_restrictions=[None] * len(getattr(cls, "outputs", [])),
            args_in_out_restrictions=[None] * len(getattr(cls, "in_outs", [])),
        )


class InstructionSpecTests(unittest.TestCase):
    def read(self, entries, **kwargs):
        with patch.object(
            Path,
            "read_text",
            return_value=json.dumps({"instructions": entries, **kwargs}),
        ):
            return read_instruction_specs("test.json")

    def entry(self, **kwargs):
        return {"name": "example", "base": "Base", "pattern": "op <Xa>", **kwargs}

    def generate(self, entries):
        namespace = {"__name__": "example_arch", "Base": FakeInstruction}
        registered = []
        names = generate_instruction_classes(
            entries, namespace, FakeInstruction, registered.append
        )
        self.assertEqual([namespace[n] for n in names], registered)
        return namespace

    def test_all_migrated_neon_definitions_match_python_baseline(self):
        fixture = Path(__file__).with_name("data") / "aarch64_neon_before_json.json"
        cases = json.loads(fixture.read_text())["cases"]
        second_batch = json.loads(
            fixture.with_name("aarch64_neon_declarative_before_json.json").read_text()
        )["cases"]
        memory_batch = json.loads(
            fixture.with_name("aarch64_neon_memory_before_json.json").read_text()
        )["cases"]
        self.assertEqual(
            {s["name"] for s in arch._NEON_SPECS},
            {c["definition"] for c in cases}
            | {c["definition"] for c in second_batch}
            | {c["definition"] for c in memory_batch}
            | {"fmov_w_to_s", "sfadd_d"}
            | {"vqrdmulh_lane", "vqdmulh_lane", "vmul_lane", "vmla_lane", "vmls_lane"}
            | {
                f"v{sign}{op}{upper}_lane"
                for sign in ("u", "s")
                for op in ("mull", "mlal", "mlsl")
                for upper in ("", "2")
            },
        )
        for case in cases:
            with self.subTest(instruction=case["definition"]):
                # Normalize tuple/list representations in JSON observations.
                actual = json.loads(json.dumps(observe(case["source"])))
                expected = dict(case["expected"])
                if case["definition"] in {"vmla", "vmls"}:
                    # Only the accumulator-chain latency deliberately changes;
                    # retain the old unit/occupancy and parser comparisons.
                    expected["cortex_a520"] = [*expected["cortex_a520"][:2], "2"]
                if case["definition"] in {
                    "mov_wtov_s",
                    "mov_vtov_d",
                    "vdup_w",
                    "vushl_reg",
                    "vuxtl",
                }:
                    # Deliberate post-migration A520 coverage/overlap fixes.
                    # Their new timing contracts are checked in test_armv9_models.
                    actual.pop("cortex_a520")
                    expected.pop("cortex_a520")
                self.assertEqual(actual, expected)

    def test_generated_names_and_inherited_operands(self):
        namespace = self.generate(
            self.read(
                [
                    self.entry(inputs=["Xa"], modifiesFlags="True"),
                    self.entry(name="child", base="example"),
                ]
            )
        )
        cls = namespace["child"]
        self.assertEqual(cls.__module__, "example_arch")
        self.assertEqual(cls.inputs, ["Xa"])
        self.assertTrue(cls.modifiesFlags)
        self.assertTrue(issubclass(cls, namespace["example"]))

    def test_legacy_boolean_strings(self):
        namespace = self.generate(
            self.read(
                [
                    self.entry(
                        dependsOnFlags="False",
                        modifiesFlags=True,
                        set_increment_from_immediate="False",
                    )
                ]
            )
        )
        cls = namespace["example"]
        self.assertFalse(cls.dependsOnFlags)
        self.assertTrue(cls.modifiesFlags)
        self.assertIsNone(cls.make("unused").increment)

    def test_address_metadata(self):
        for addr, expected in (
            ({"type": "inputs", "index": 0}, "x0"),
            ({"type": "in_outs", "index": 0}, "x1"),
            ({"type": "literal", "value": "sp"}, "sp"),
        ):
            cls = self.generate(
                self.read(
                    [
                        self.entry(
                            inputs=["Xa"],
                            in_outs=["Xa"],
                            addr_source=addr,
                            set_increment_from_immediate=True,
                            pre_index_from_immediate=True,
                        )
                    ]
                )
            )["example"]
            inst = cls.make("unused")
            self.assertEqual(
                (inst.addr, inst.increment, inst.pre_index), (expected, 16, 16)
            )

    def test_invalid_specifications_fail_early(self):
        for entries, options in (
            ([self.entry(unknown=True)], {}),
            ([self.entry(), self.entry()], {}),
            ([self.entry(dependsOnFlags="yes")], {}),
            ([self.entry(inputs=["Xmissing"])], {}),
            ([self.entry(addr_source={"type": "inputs", "index": -1})], {}),
            ([self.entry()], {"schema_version": 2}),
            ([self.entry()], {"unexpected": []}),
        ):
            with self.subTest(entries=entries, options=options):
                with self.assertRaises(ValueError):
                    self.read(entries, **options)

    def test_unknown_bases_and_name_collisions(self):
        for entry in (self.entry(base="Missing"), self.entry(name="Base")):
            with self.assertRaises(ValueError):
                self.generate(self.read([entry]))

    def test_named_conditional_restrictions_and_intersection(self):
        rule = {
            "operand": "Vb",
            "when": {"dt1": ["h"]},
            "registers": {"prefix": "v", "first": 0, "last": 15},
        }
        cls = self.generate(
            self.read(
                [
                    self.entry(
                        pattern="op <Vd>.<dt0>, <Va>.<dt0>, <Vb>.<dt1>",
                        inputs=["Vb", "Va"],
                        outputs=["Vd"],
                        register_restrictions=[
                            rule,
                            {**rule, "registers": ["v15", "v16"]},
                        ],
                    )
                ]
            )
        )["example"]
        inst = cls.make(["8H", "8H", "H"])
        self.assertEqual(inst.args_in_restrictions, [["v15"], None])
        self.assertEqual(cls.make(["4s", "4s", "s"]).args_in_restrictions, [None, None])
        inst.args_in_restrictions[0].append("v20")
        self.assertEqual(
            cls.make(["4h", "4h", "h"]).args_in_restrictions, [["v15"], None]
        )

    def test_unconditional_restrictions_all_roles(self):
        cls = self.generate(
            self.read(
                [
                    self.entry(
                        pattern="op <Xa>, <Vb>, <Vc>",
                        inputs=["Xa"],
                        outputs=["Vb"],
                        in_outs=["Vc"],
                        register_restrictions=[
                            {
                                "operand": "Xa",
                                "registers": {"prefix": "x", "first": 0, "last": 2},
                            },
                            {"operand": "Vb", "registers": ["v31"]},
                            {"operand": "Vc", "registers": ["v0", "v1"]},
                        ],
                    )
                ]
            )
        )["example"]
        inst = cls.make(None)
        self.assertEqual(inst.args_in_restrictions, [["x0", "x1", "x2"]])
        self.assertEqual(inst.args_out_restrictions, [["v31"]])
        self.assertEqual(inst.args_in_out_restrictions, [["v0", "v1"]])

    def test_inherited_restrictions_resolve_child_placeholders(self):
        namespace = self.generate(
            self.read(
                [
                    self.entry(
                        pattern="op <Va>.<dt0>, <Vb>.<dt1>",
                        inputs=["Va", "Vb"],
                        register_restrictions=[
                            {
                                "operand": "Vb",
                                "when": {"dt1": ["h"]},
                                "registers": ["v0"],
                            }
                        ],
                    ),
                    self.entry(
                        name="child",
                        base="example",
                        pattern="op <Vb>.<dt1>, <Va>.<dt0>",
                        inputs=["Vb", "Va"],
                    ),
                    self.entry(
                        name="cleared",
                        base="child",
                        pattern="op <Vb>.<dt1>, <Va>.<dt0>",
                        register_restrictions=[],
                    ),
                ]
            )
        )
        self.assertEqual(
            namespace["child"].make(["h", "8h"]).args_in_restrictions, [["v0"], None]
        )
        self.assertEqual(
            namespace["cleared"].make(["h", "8h"]).args_in_restrictions, [None, None]
        )

    def test_invalid_restrictions_fail_early(self):
        valid = {"operand": "Va", "when": {"dt": ["h"]}, "registers": ["v0"]}
        bad_rules = [
            None,
            {},
            [None],
            [{**valid, "unknown": True}],
            [{**valid, "operand": "Vmissing"}],
            [{**valid, "when": {"dt1": ["h"]}}],
            [{**valid, "when": {"dt": []}}],
            [{**valid, "when": {"dt": "h"}}],
        ]
        for registers in (
            None,
            [],
            ["x0"],
            ["v32"],
            ["v01"],
            [1],
            {"prefix": "v", "first": -1, "last": 15},
            {"prefix": "v", "first": 16, "last": 15},
            {"prefix": "v", "first": False, "last": 15},
            {"prefix": "v", "first": 0, "last": 32},
            {"prefix": "v", "first": 0},
        ):
            bad_rules.append([{**valid, "registers": registers}])
        for rules in bad_rules:
            with self.subTest(rules=rules), self.assertRaises(ValueError):
                self.read(
                    [self.entry(pattern="op <Va>.<dt>", register_restrictions=rules)]
                )
        for operands in ({}, {"inputs": ["Va"], "outputs": ["Va"]}):
            with self.subTest(operands=operands), self.assertRaises(ValueError):
                self.generate(
                    self.read(
                        [
                            self.entry(
                                pattern="op <Va>.<dt>",
                                register_restrictions=[valid],
                                **operands,
                            )
                        ]
                    )
                )

    def test_scalar_memory_fixup_and_registration(self):
        inst = arch.Instruction.parser(SourceLine("ldr x0, [x1, #16]"))[0]
        self.assertEqual(inst.addr, "x1")
        self.assertEqual(int(inst.pre_index), 16)
        inst.pre_index = 32
        self.assertIn("32", inst.write())
        for name in scalar.GENERATED_EXPORTS:
            cls = getattr(scalar, name)
            self.assertIs(getattr(arch, name), cls)
            self.assertIn(cls, arch.Instruction.all_subclass_leaves)
            self.assertEqual(cls.__module__, scalar.__name__)

    def test_neon_alias_callbacks_and_discovery(self):
        self.assertIs(arch.vfmul, arch.vmulf)
        self.assertIs(arch.vfmla.__base__, arch.vmla)
        self.assertIs(arch.vfmls.__base__, arch.vmls)
        self.assertTrue(callable(arch.vins_d.global_parsing_cb))
        for entry in arch._NEON_SPECS:
            cls = getattr(arch, entry["name"])
            self.assertEqual(cls.__module__, arch.__name__)
            self.assertIn(cls, arch.Instruction.all_subclass_leaves)


if __name__ == "__main__":
    unittest.main()
