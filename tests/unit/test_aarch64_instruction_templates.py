"""Template expansion is a syntax refactor, not instruction-class inheritance."""

from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from slothy.targets.aarch64 import aarch64_neon as arch
from slothy.targets.aarch64.instruction_loader import (
    generate_instruction_classes,
    read_instruction_specs,
)
from slothy.targets.aarch64.instruction_templates import expand_instruction_templates


class InstructionTemplateTests(unittest.TestCase):
    def document(self):
        return {
            "schema_version": 2,
            "templates": {
                "binary": {
                    "base": "Base",
                    "pattern": "{mnemonic} <Vd>.<dt>, <Va>.<dt>, <Vb>.<dt>",
                    "inputs": ["Va", "Vb"],
                    "outputs": ["Vd"],
                    "required_features": ["FEAT_AdvSIMD"],
                }
            },
            "instructions": [
                {"name": "vadd", "template": "binary", "mnemonic": "add"},
                {"name": "vsub", "template": "binary", "mnemonic": "sub"},
            ],
        }

    def read(self, document):
        with patch.object(Path, "read_text", return_value=json.dumps(document)):
            return read_instruction_specs("test.json")

    def test_legacy_and_explicit_entries_are_unchanged(self):
        entry = {"name": "nop", "base": "Base", "pattern": "nop"}
        for options in ({}, {"schema_version": 1}, {"schema_version": 2}):
            with self.subTest(options=options):
                self.assertEqual(
                    self.read({"instructions": [entry], **options}), [entry]
                )

    def test_expansion_keeps_order_names_and_bases(self):
        specs = self.read(self.document())
        self.assertEqual([s["name"] for s in specs], ["vadd", "vsub"])
        for spec, mnemonic in zip(specs, ("add", "sub")):
            self.assertEqual(
                spec["pattern"], f"{mnemonic} <Vd>.<dt>, <Va>.<dt>, <Vb>.<dt>"
            )
            self.assertEqual(spec["base"], "Base")
            self.assertEqual(spec["required_features"], ["FEAT_AdvSIMD"])
            self.assertNotIn("template", spec)
            self.assertNotIn("mnemonic", spec)

        class Base:
            pass

        namespace = {"Base": Base, "__name__": "test_templates"}
        generate_instruction_classes(specs, namespace, Base)
        for name in ("vadd", "vsub"):
            cls = namespace[name]
            self.assertEqual(cls.__bases__, (Base,))
            self.assertEqual(cls.__dict__["required_features"], ["FEAT_AdvSIMD"])
        self.assertFalse(issubclass(namespace["vsub"], namespace["vadd"]))

    def test_field_overrides_replace_instead_of_merge(self):
        doc = self.document()
        doc["templates"]["binary"].update(
            operand_values={"dt": ["4s", "8h"]},
            conditional_features=[{"when": {"dt": ["8h"]}, "requires": ["FEAT_FP16"]}],
            modifiesFlags=True,
        )
        doc["instructions"][0].update(
            base="OtherBase",
            outputs=[],
            in_outs=["Vd"],
            operand_values={},
            required_features=[],
            conditional_features=[],
            modifiesFlags=False,
        )
        first, second = self.read(doc)
        self.assertEqual(first["base"], "OtherBase")
        self.assertEqual(first["outputs"], [])
        self.assertEqual(first["in_outs"], ["Vd"])
        self.assertEqual(first["operand_values"], {})
        self.assertEqual(first["required_features"], [])
        self.assertEqual(first["conditional_features"], [])
        self.assertFalse(first["modifiesFlags"])
        self.assertEqual(second["outputs"], ["Vd"])
        self.assertEqual(second["operand_values"], {"dt": ["4s", "8h"]})

    def test_nested_fields_are_not_shared_or_mutated(self):
        doc = self.document()
        doc["templates"]["binary"]["operand_values"] = {"dt": ["4s"]}
        before = deepcopy(doc)
        first, second = expand_instruction_templates(doc)
        first["inputs"].append("unexpected")
        first["operand_values"]["dt"].append("8h")
        self.assertEqual(second["inputs"], ["Va", "Vb"])
        self.assertEqual(second["operand_values"], {"dt": ["4s"]})
        self.assertEqual(doc, before)
        self.assertEqual(self.read(doc), expand_instruction_templates(doc))

    def test_patterns_can_be_fixed_overridden_or_contain_register_lists(self):
        doc = self.document()
        doc["templates"]["binary"][
            "pattern"
        ] = "{mnemonic} <Vd>.<dt>, {<Va>.<dt>}, <Vb>.<dt>"
        doc["instructions"][0]["mnemonic"] = "tbl"
        doc["instructions"][1].update(pattern="orr <Vd>.<dt>, <Va>.<dt>, <Vb>.<dt>")
        del doc["instructions"][1]["mnemonic"]
        first, second = self.read(doc)
        self.assertEqual(first["pattern"], "tbl <Vd>.<dt>, {<Va>.<dt>}, <Vb>.<dt>")
        self.assertEqual(second["pattern"], "orr <Vd>.<dt>, <Va>.<dt>, <Vb>.<dt>")
        doc["templates"]["binary"]["pattern"] = second["pattern"]
        del doc["instructions"][0]["mnemonic"]
        self.assertEqual(self.read(doc)[0]["pattern"], second["pattern"])

    def test_malformed_template_documents_fail(self):
        documents = []
        for version in (0, 3, True, 2.0, "2", None):
            documents.append({**self.document(), "schema_version": version})
        documents.append({**self.document(), "schema_version": 1})
        documents.append({**self.document(), "unknown": {}})
        for templates in ([], None, {"bad-name": {}}, {"binary": []}):
            documents.append({**self.document(), "templates": templates})
        for extra in (
            {"name": "hidden"},
            {"template": "binary"},
            {"mnemonic": "add"},
            {"typo": True},
        ):
            doc = self.document()
            doc["templates"]["binary"].update(extra)
            documents.append(doc)
        for template in ("missing", ["binary"], None):
            doc = self.document()
            doc["instructions"][0]["template"] = template
            documents.append(doc)
        for mnemonic in (None, 3, "", "add sub", "add\n", "{other}"):
            doc = self.document()
            doc["instructions"][0]["mnemonic"] = mnemonic
            documents.append(doc)
        for pattern in (
            "{opcode} <Vd>",
            "{mnemonic!r} <Vd>",
            "add {mnemonic} <Vd>",
            "{mnemonic} <Vd>, {mnemonic}",
            "{mnemonic} <Vd>, {unknown}",
            "add <Vd>",
        ):
            doc = self.document()
            doc["templates"]["binary"]["pattern"] = pattern
            documents.append(doc)
        for key in ("name", "mnemonic", "template"):
            doc = self.document()
            del doc["instructions"][0][key]
            documents.append(doc)
        for document in documents:
            with (
                self.subTest(document=document),
                self.assertRaisesRegex(ValueError, "test.json"),
            ):
                self.read(document)

    def test_expanded_entries_still_receive_concrete_validation(self):
        for fields in (
            {"inputs": ["Missing"]},
            {"required_features": ["NOT_A_FEATURE"]},
            {"operand_values": {"dt": []}},
            {"register_restrictions": "invalid"},
            {"dependsOnFlags": "invalid"},
            {"base": None},
        ):
            doc = self.document()
            doc["templates"]["binary"].update(fields)
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                self.read(doc)
        doc = self.document()
        doc["instructions"][1]["name"] = "vadd"
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.read(doc)

    def test_migrated_definitions_match_before_templates(self):
        root = Path(arch.__file__).parent
        document = json.loads((root / "aarch64_neon_instructions.json").read_text())
        fixture = (
            Path(__file__).with_name("data") / "aarch64_neon_before_templates.json"
        )
        expected = json.loads(fixture.read_text())["instructions"]
        names = {entry["name"] for entry in expected}
        self.assertEqual(
            {e["name"] for e in document["instructions"] if "template" in e}, names
        )
        actual = [e for e in arch._NEON_SPECS if e["name"] in names]
        self.assertEqual(actual, expected)
        for entry in expected:
            cls = getattr(arch, entry["name"])
            self.assertEqual(cls.__bases__[0].__name__, entry["base"])
            self.assertEqual(cls.pattern, entry["pattern"])


if __name__ == "__main__":
    unittest.main()
