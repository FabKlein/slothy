"""Architectural feature checks must not be inferred from timing-table coverage."""

import json
import logging
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from slothy.core.config import Config, InvalidConfig
from slothy.core.core import SlothyBase
from slothy.core.dataflow import Config as DFGConfig, DataFlowGraph
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as arch
from slothy.targets.aarch64 import cortex_a55, cortex_a320, cortex_a520
from slothy.targets.aarch64.instruction_loader import read_instruction_specs
from slothy.targets.aarch64.isa import (
    FEATURES,
    UnknownISA,
    UnsupportedISA,
    instruction_features,
    target_features,
    validate_instruction_features,
)
from slothy.targets.exceptions import UnknownInstruction

LOGGER = logging.getLogger("test.aarch64.isa")


def parse(text):
    return arch.Instruction.parser(SourceLine(text))[0]


class ISATests(unittest.TestCase):
    def config(self, target=cortex_a520):
        config = Config(arch, target, LOGGER)
        config.isa_check = "strict"
        config.inputs_are_outputs = True
        config.selftest = False
        return config

    def validate(self, text, config=None):
        validate_instruction_features([parse(text)], config or self.config(), LOGGER)

    def graph(self, source, config):
        return DataFlowGraph(
            SourceLine.read_multiline(source), LOGGER, DFGConfig(config)
        )

    def test_profiles_are_explicit_not_version_or_timing_inferences(self):
        self.assertEqual(cortex_a55.isa.architecture, "armv8.2-a")
        for target in (cortex_a320, cortex_a520):
            self.assertEqual(target.isa.architecture, "armv9.2-a")
            self.assertTrue(target_features(target, {})["FEAT_I8MM"])
            self.assertTrue(target_features(target, {})["FEAT_SHA3"])
        self.assertFalse(target_features(cortex_a55, {})["FEAT_I8MM"])
        self.assertFalse(target_features(cortex_a55, {})["FEAT_SHA3"])
        self.assertEqual(FEATURES["FEAT_I8MM"].available_from, "armv8.2-a")
        self.assertEqual(FEATURES["FEAT_I8MM"].default_from, "armv8.6-a")
        self.assertEqual(FEATURES["FEAT_DotProd"].default_from, "armv8.4-a")
        self.assertEqual(FEATURES["FEAT_RDM"].available_from, "armv8.1-a")

    def test_sha3_rejected_on_a55_but_accepted_on_a320_a520(self):
        for text in (
            "eor3 v0.16b, v1.16b, v2.16b, v3.16b",
            "bcax v0.16b, v1.16b, v2.16b, v3.16b",
            "rax1 v0.2d, v1.2d, v2.2d",
            "xar v0.2d, v1.2d, v2.2d, #5",
        ):
            for target in (cortex_a320, cortex_a520):
                self.validate(text, self.config(target))
            for mode in ("warn", "strict"):
                config = self.config(cortex_a55)
                config.isa_check = mode
                with self.assertRaisesRegex(UnsupportedISA, "FEAT_SHA3.*cortex-a55"):
                    self.validate(text, config)

    def test_fp16_conditions_do_not_apply_to_fp32_or_integer_halfwords(self):
        config = self.config()
        config.isa_features = {"FEAT_FP16": False, "FEAT_RDM": False}
        for text in (
            "fadd v0.4H, v1.4H, v2.4H",
            "fmul v0.8h, v1.8h, v2.8h",
            "fmla v0.8h, v1.8h, v2.8h",
            "fmls v0.4h, v1.4h, v2.4h",
            "fmul v0.8h, v1.8h, v2.h[1]",
            "fmla v0.8h, v1.8h, v2.h[1]",
        ):
            with self.subTest(text=text):
                with self.assertRaisesRegex(UnsupportedISA, "FEAT_FP16"):
                    self.validate(text, config)
        for text in (
            "fadd v0.4s, v1.4s, v2.4s",
            "fmul v0.2d, v1.2d, v2.d[1]",
            "add v0.8h, v1.8h, v2.8h",
            "sqrdmulh v0.8h, v1.8h, v2.8h",
            "sqrdmulh v0.8h, v1.8h, v2.h[1]",
        ):
            self.validate(text, config)

    def test_crypto_and_crc_requirements(self):
        cases = (
            ("aese v0.16b, v1.16b", "FEAT_AES"),
            ("aesr v0.16b, v1.16b", "FEAT_AES"),
            ("pmull v0.1q, v1.1d, v2.1d", "FEAT_PMULL"),
            ("pmull2 v0.1q, v1.2d, v2.2d", "FEAT_PMULL"),
            ("crc32x w0, w1, x2", "FEAT_CRC32"),
        )
        for target in (cortex_a55, cortex_a320, cortex_a520):
            for text, feature in cases:
                with self.subTest(target=target.__name__, text=text):
                    config = self.config(target)
                    self.validate(text, config)
                    config.isa_features = {feature: False}
                    with self.assertRaisesRegex(UnsupportedISA, feature):
                        self.validate(text, config)
        # PMULL classes inherit from AESInstruction for timing, not ISA requirements.
        self.assertNotIn("FEAT_AES", instruction_features(parse(cases[2][0])))

    def test_dependencies_and_invalid_overrides(self):
        config = self.config()
        config.isa_features = {"FEAT_FP": False}
        with self.assertRaisesRegex(UnsupportedISA, "FEAT_FP"):
            self.validate("add v0.4s, v1.4s, v2.4s", config)
        for overrides in ({"FEAT_typo": True}, {"FEAT_FP": 1}):
            with self.assertRaises(ValueError):
                target_features(cortex_a520, overrides)
        with self.assertRaisesRegex(ValueError, "Cannot enable"):
            target_features(cortex_a55, {"FEAT_I8MM": True})
        with self.assertRaises(InvalidConfig):
            config.isa_check = "typo"
        with self.assertRaises(InvalidConfig):
            config.isa_features = {"FEAT_FP": "False"}

    def test_unknown_metadata_warn_strict_off(self):
        config = self.config()
        # This memory form has intentionally not been audited in the first increment.
        source = "ldr x0, [x1]"
        with self.assertRaisesRegex(UnknownISA, "unclassified instruction"):
            self.validate(source, config)
        config.isa_check = "warn"
        with self.assertLogs(LOGGER, level="WARNING") as log:
            self.validate(source, config)
        self.assertIn("Incomplete ISA validation", log.output[0])
        config = self.config(cortex_a55)
        config.isa_check = "off"
        self.validate("eor3 v0.16b, v1.16b, v2.16b, v3.16b", config)

    def test_unprofiled_target_and_explicit_assertions(self):
        config = self.config(SimpleNamespace(llvm_mca_target="custom"))
        with self.assertRaisesRegex(UnknownISA, "unknown FEAT_AdvSIMD"):
            self.validate("add v0.4s, v1.4s, v2.4s", config)
        config.isa_features = {"FEAT_FP": True, "FEAT_AdvSIMD": True}
        self.validate("add v0.4s, v1.4s, v2.4s", config)

    def test_concrete_subclasses_do_not_silently_inherit_requirements(self):
        parent = type("Parent", (), {"required_features": []})
        child = type("Child", (parent,), {})
        self.assertIsNone(instruction_features(child()))
        # Actual FP subclasses of integer MLA must have their own FP16 conditions.
        self.assertIn(
            "FEAT_FP16", instruction_features(parse("fmla v0.4h, v1.4h, v2.4h"))
        )

    def test_schema_validation(self):
        entry = {"name": "example", "base": "Base", "pattern": "op <Va>.<dt>"}
        invalid = (
            {"required_features": "FEAT_FP"},
            {"required_features": ["FEAT_typo"]},
            {"required_features": ["FEAT_FP", "FEAT_FP"]},
            {"conditional_features": [{"when": {"dt": ["4h"]}, "requires": []}]},
            {"required_features": [], "conditional_features": None},
            {
                "required_features": [],
                "conditional_features": [
                    {"when": {"dt2": ["4h"]}, "requires": ["FEAT_FP16"]}
                ],
            },
            {
                "required_features": [],
                "conditional_features": [
                    {"when": {"dt": ["4h"]}, "requires": ["FEAT_typo"]}
                ],
            },
        )
        for fields in invalid:
            with self.subTest(fields=fields):
                with patch.object(
                    Path,
                    "read_text",
                    return_value=json.dumps({"instructions": [{**entry, **fields}]}),
                ):
                    with self.assertRaises(ValueError):
                        read_instruction_specs("test.json")

    def test_fusion_cannot_introduce_unsupported_sha3(self):
        source = "eor v4.16b, v1.16b, v2.16b\neor v0.16b, v4.16b, v3.16b"
        for target in (cortex_a55, cortex_a520):
            config = self.config(target)
            config.inputs_are_outputs = False
            config.outputs = {"v0"}
            tree = self.graph(source, config)
            if target is cortex_a55:
                with self.assertRaisesRegex(UnsupportedISA, "FEAT_SHA3"):
                    tree.apply_fusion_cbs()
            else:
                tree.apply_fusion_cbs()
                self.assertEqual(type(tree.nodes[0].inst).__name__, "veor3")

    def test_reject_before_solver_or_timing_lookup(self):
        core = SlothyBase(arch, cortex_a55)
        core.config = self.config(cortex_a55)
        core.config.constraints.functional_only = True
        with patch.object(core, "_init_external_model_and_solver") as solver:
            with patch.object(cortex_a55, "get_units") as units:
                with self.assertRaises(UnsupportedISA):
                    core.optimize(
                        SourceLine.read_multiline("eor3 v0.16b, v1.16b, v2.16b, v3.16b")
                    )
                solver.assert_not_called()
                units.assert_not_called()

    def test_supported_instruction_without_timing_has_distinct_error(self):
        core = SlothyBase(arch, cortex_a520)
        core.config = self.config()
        with patch.object(
            cortex_a520, "get_inverse_throughput", side_effect=UnknownInstruction("gap")
        ):
            with self.assertRaisesRegex(UnknownInstruction, "scheduling-model gap"):
                core.optimize(SourceLine.read_multiline("add v0.4s, v0.4s, v2.4s"))

    def test_missing_latency_has_distinct_error(self):
        core = SlothyBase(arch, cortex_a520)
        core.config = self.config()
        with patch.object(
            cortex_a520, "get_latency", side_effect=UnknownInstruction("gap")
        ):
            with self.assertRaisesRegex(UnknownInstruction, "Missing latency model"):
                core.optimize(
                    SourceLine.read_multiline(
                        "add v0.4s, v0.4s, v2.4s\nadd v0.4s, v0.4s, v2.4s"
                    )
                )

    def test_repeated_unknown_warning_is_suppressed_but_still_checked(self):
        config = self.config()
        config.isa_check = "warn"
        with self.assertLogs(LOGGER, level="WARNING") as logs:
            self.validate("ldr x0, [x1]", config)
            self.validate("ldr x0, [x1]", config)
        self.assertEqual(len(logs.output), 1)
        config.isa_check = "strict"
        with self.assertRaises(UnknownISA):
            self.validate("ldr x0, [x1]", config)

    def test_strict_optimization_and_software_pipelining(self):
        for pipelining in (False, True):
            core = SlothyBase(arch, cortex_a520)
            core.config = self.config()
            core.config.sw_pipelining.enabled = pipelining
            core.config.variable_size = True
            core.config.constraints.stalls_allowed = 16
            core.config.timeout = 5
            self.assertTrue(
                core.optimize(
                    SourceLine.read_multiline(
                        "eor v0.16b, v0.16b, v1.16b\neor v2.16b, v2.16b, v3.16b"
                    )
                )
            )


if __name__ == "__main__":
    unittest.main()
