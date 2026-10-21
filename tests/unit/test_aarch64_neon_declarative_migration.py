"""Regression coverage for the second batch of declarative NEON definitions."""

import ast
import json
import logging
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from aarch64_model_snapshot import observe
from slothy.core.config import Config
from slothy.core.dataflow import Config as DFGConfig, DataFlowGraph
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as arch
from slothy.targets.aarch64 import cortex_a520
from slothy.targets.aarch64.isa import instruction_features
from slothy.targets.query import Archery

TARGET_NAMES = (
    "Arm_Cortex_A55",
    "Arm_Cortex_A320",
    "Arm_Cortex_A520",
    "Arm_Cortex_A72_frontend",
    "Arm_Neoverse_N1_experimental",
    "Arm_Big_experimental",
    "Apple_M1_firestorm_experimental",
    "Apple_M1_icestorm_experimental",
)


def fixture():
    return json.loads(
        (
            Path(__file__).with_name("data")
            / "aarch64_neon_declarative_before_json.json"
        ).read_text(encoding="utf8")
    )


class DeclarativeMigrationTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("clang-19"), "Requires AArch64-capable Clang")
    def test_real_instructions_assemble(self):
        pseudo = {"aesr", "aesr_x2", "aesr_x4", "aese_x4", "aesdr"}
        sources = [
            arch.Instruction.parser(SourceLine(case["source"]))[0].write()
            for case in fixture()["cases"]
            if case["definition"] not in pseudo
        ]
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run(
                [
                    "clang-19",
                    "--target=aarch64-none-elf",
                    "-march=armv8-a+crypto",
                    "-x",
                    "assembler",
                    "-c",
                    "-",
                    "-o",
                    str(Path(temp) / "forms.o"),
                ],
                input=".text\n" + "\n".join(sources) + "\n",
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_parser_and_all_target_models_match_baseline(self):
        cases = fixture()["cases"]
        definitions = {entry["name"] for entry in arch._NEON_SPECS}
        self.assertEqual(len(cases), 28)
        for case in cases:
            with self.subTest(instruction=case["definition"]):
                self.assertIn(case["definition"], definitions)
                actual = observe(
                    case["source"],
                    targets=[Archery.get_target(n) for n in TARGET_NAMES],
                )
                self.assertEqual(json.loads(json.dumps(actual)), case["expected"])
                cls = getattr(arch, case["definition"])
                self.assertEqual(cls.__module__, arch.__name__)
                self.assertIn(cls, arch.Instruction.all_subclass_leaves)

    def test_no_plain_declarations_left_in_python(self):
        tree = ast.parse(Path(arch.__file__).read_text(encoding="utf8"))
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            has_pattern = any(
                isinstance(item, ast.Assign)
                and any(
                    isinstance(t, ast.Name) and t.id == "pattern" for t in item.targets
                )
                for item in node.body
            )
            has_methods = any(isinstance(item, ast.FunctionDef) for item in node.body)
            if has_pattern:
                self.assertTrue(has_methods, f"{node.name} belongs in JSON")

    def test_all_migrated_forms_have_explicit_isa_metadata(self):
        for case in fixture()["cases"]:
            inst = arch.Instruction.parser(SourceLine(case["source"]))[0]
            features = instruction_features(inst)
            self.assertIsNotNone(features, case["definition"])
            if case["definition"].startswith("fmov"):
                self.assertEqual(features, {"FEAT_FP"})
            elif case["definition"].startswith("pmull"):
                self.assertIn("FEAT_PMULL", features)
                self.assertNotIn("FEAT_AES", features)

    def test_fmov_callbacks_remain_attached_and_preserve_output_roles(self):
        logger = logging.getLogger("test.neon.migration")
        for source, expected_class in (
            ("fmov d0, x1\nfmov v0.d[1], x2", arch.fmov_0_force_output),
            ("fmov v0.d[1], x2\nfmov d0, x1", arch.fmov_1_force_output),
        ):
            with self.subTest(source=source):
                config = Config(arch, cortex_a520, logger)
                config.outputs = {"v0"}
                config.isa_check = "strict"
                tree = DataFlowGraph(
                    SourceLine.read_multiline(source), logger, DFGConfig(config)
                )
                first = tree.nodes[0].inst
                self.assertIs(type(first), expected_class)
                self.assertEqual(first.args_out, ["v0"])
                self.assertEqual(first.args_in_out, [])
                self.assertEqual(tree.nodes[1].inst.args_in_out, ["v0"])


if __name__ == "__main__":
    unittest.main()
