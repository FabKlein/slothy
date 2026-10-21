"""Expand JSON instruction templates without importing the architecture or solver.

Both the runtime loader and standalone documentation generator use this step.
Templates are field defaults, not Python bases or a general macro language.
"""

from copy import deepcopy
import re

OPERAND_FIELDS = ("inputs", "outputs", "in_outs")
FLAG_FIELDS = ("dependsOnFlags", "modifiesFlags")
MEMORY_FIELDS = (
    "set_increment_from_immediate",
    "pre_index_from_immediate",
    "restore_immediate_from_pre_index",
)
INSTRUCTION_FIELDS = {
    "name",
    "base",
    "pattern",
    "addr_source",
    "register_restrictions",
    "required_features",
    "conditional_features",
    "operand_values",
    *OPERAND_FIELDS,
    *FLAG_FIELDS,
    *MEMORY_FIELDS,
}


def _expand_pattern(entry, mnemonic):
    pattern = entry.get("pattern")
    if not isinstance(pattern, str) or not pattern:
        raise ValueError("Template expansion requires a nonempty pattern")
    token = pattern.split()[0] if pattern.split() else ""
    if ("{" in token or "}" in token) and token != "{mnemonic}":
        raise ValueError("Only a leading {mnemonic} template parameter is supported")
    # Do not use str.format: braces also delimit assembly register lists.
    parameters = re.findall(r"\{[A-Za-z_]\w*\}", pattern)
    if parameters:
        if parameters != ["{mnemonic}"] or not pattern.startswith("{mnemonic} "):
            raise ValueError(
                "Only a leading {mnemonic} template parameter is supported"
            )
        if not isinstance(mnemonic, str) or not re.fullmatch(
            r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)*", mnemonic
        ):
            raise ValueError("A {mnemonic} pattern requires a valid mnemonic")
        entry["pattern"] = pattern.replace("{mnemonic}", mnemonic, 1)
    elif mnemonic is not None:
        raise ValueError("mnemonic requires a {mnemonic} parameter in the pattern")


def expand_instruction_templates(data):
    """Return independent concrete entries in source order for schema v1 or v2."""
    if not isinstance(data, dict):
        raise ValueError("Instruction specification must be an object")
    version = data.get("schema_version", 1)
    if type(version) is not int or version not in (1, 2):
        raise ValueError("Unsupported schema_version")
    allowed = {"schema_version", "instructions"}
    if version == 2:
        allowed.add("templates")
    if set(data) - allowed:
        raise ValueError("Unsupported instruction specification fields")
    entries = data.get("instructions")
    if not isinstance(entries, list):
        raise ValueError("instructions must be a list")
    templates = data.get("templates", {})
    if not isinstance(templates, dict):
        raise ValueError("templates must map names to field defaults")
    for name, template in templates.items():
        if not isinstance(name, str) or not name.isidentifier():
            raise ValueError(f"Invalid template name {name!r}")
        if not isinstance(template, dict) or set(template) - (
            INSTRUCTION_FIELDS - {"name"}
        ):
            raise ValueError(f"Invalid fields in template {name!r}")

    expanded = []
    for entry in entries:
        fields = INSTRUCTION_FIELDS | (
            {"template", "mnemonic"} if version == 2 else set()
        )
        if not isinstance(entry, dict) or set(entry) - fields:
            raise ValueError(f"Unknown instruction fields: {entry!r}")
        if "template" not in entry:
            if "mnemonic" in entry:
                raise ValueError("mnemonic requires an instruction template")
            concrete = deepcopy(entry)
        else:
            name = entry["template"]
            if not isinstance(name, str) or name not in templates:
                raise ValueError(f"Unknown instruction template {name!r}")
            # Replace entire fields, including lists and dictionaries; no deep merge.
            concrete = deepcopy({**templates[name], **entry})
            del concrete["template"]
            if "mnemonic" in concrete and not isinstance(concrete["mnemonic"], str):
                raise ValueError("mnemonic must be a string")
            mnemonic = concrete.pop("mnemonic", None)
            _expand_pattern(concrete, mnemonic)
        expanded.append(concrete)
    return expanded
