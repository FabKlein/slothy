"""Shared loader for declarative AArch64 instruction classes.

The caller supplies the architecture namespace to avoid circular imports and to
preserve public class identities used by target models and parser callbacks.
"""

import json
import re
from pathlib import Path

from sympy import simplify
from slothy.targets.aarch64.isa import validate_requirements
from slothy.targets.exceptions import ParsingException

_OPERANDS = ("inputs", "outputs", "in_outs")
_FLAGS = ("dependsOnFlags", "modifiesFlags")
_MEMORY = (
    "set_increment_from_immediate",
    "pre_index_from_immediate",
    "restore_immediate_from_pre_index",
)
_FIELDS = {
    "name",
    "base",
    "pattern",
    "addr_source",
    "register_restrictions",
    "required_features",
    "conditional_features",
    "operand_values",
    *_OPERANDS,
    *_FLAGS,
    *_MEMORY,
}
_RESTRICTION_FIELDS = {
    "inputs": "args_in_restrictions",
    "outputs": "args_out_restrictions",
    "in_outs": "args_in_out_restrictions",
}


def _validate_operand_values(rules, pattern):
    """Validate finite allowed-value sets for datatype and immediate placeholders."""
    if not isinstance(rules, dict):
        raise ValueError("operand_values must map placeholders to allowed values")
    for name, values in rules.items():
        if (
            not isinstance(name, str)
            or not re.fullmatch(r"dt\d*|imm", name)
            or f"<{name}>" not in pattern
            or not isinstance(values, list)
            or not values
        ):
            raise ValueError(f"Invalid operand_values rule: {name!r}: {values!r}")
        if name == "imm":
            valid = pattern.count("<imm>") == 1 and all(
                type(value) is int for value in values
            )
            normalized = values
        else:
            valid = all(isinstance(value, str) and value for value in values)
            normalized = [str(value).lower() for value in values]
        if not valid or len(set(normalized)) != len(values):
            raise ValueError(f"Invalid operand_values list for {name!r}")


def _check_operand_values(obj, rules, pattern):
    """Reject unsupported arrangements or unresolved/illegal finite immediates."""
    if not rules:
        return
    datatypes = re.findall(r"<(dt\d*)>", pattern)
    actual = obj.datatype if isinstance(obj.datatype, list) else [obj.datatype]
    for name, allowed in rules.items():
        if name == "imm":
            try:
                value = simplify(obj.immediate)
                valid = value.is_Integer is True and int(value) in allowed
            except (AttributeError, TypeError, ValueError, SyntaxError):
                valid = False
        else:
            values = [
                str(actual[i]).lower() for i, key in enumerate(datatypes) if key == name
            ]
            valid = len(set(values)) == 1 and values[0] in [
                value.lower() for value in allowed
            ]
        if not valid:
            raise ParsingException(
                f"{pattern.split()[0]}: {name} must be one of {allowed}"
            )


def _restriction_registers(rule):
    """Expand an inclusive canonical-register range, or an explicit register list."""
    registers = rule.get("registers")
    if isinstance(registers, dict):
        if set(registers) != {"prefix", "first", "last"}:
            raise ValueError("registers range requires prefix, first and last")
        prefix, first, last = (registers[k] for k in ("prefix", "first", "last"))
        if (
            prefix not in ("v", "x")
            or type(first) is not int
            or type(last) is not int
            or not 0 <= first <= last <= (31 if prefix == "v" else 30)
        ):
            raise ValueError("Invalid registers range")
        registers = [f"{prefix}{i}" for i in range(first, last + 1)]
    if not isinstance(registers, list) or not registers:
        raise ValueError("registers must be a nonempty list or inclusive range")
    operand = rule.get("operand", "")
    prefix = "v" if operand[:1] in ("V", "Q", "D", "S", "H", "B") else "x"
    for reg in registers:
        if (
            not isinstance(reg, str)
            or not re.fullmatch(r"[vx](0|[1-9][0-9]?)", reg)
            or reg[0] != prefix
            or int(reg[1:]) > (31 if prefix == "v" else 30)
        ):
            raise ValueError(f"Invalid register {reg!r} for operand {operand!r}")
    return tuple(dict.fromkeys(registers))


def _validate_restrictions(rules, pattern):
    if not isinstance(rules, list):
        raise ValueError("register_restrictions must be a list")
    datatypes = re.findall(r"<(dt\d*)>", pattern)
    for rule in rules:
        if not isinstance(rule, dict) or set(rule) - {"operand", "when", "registers"}:
            raise ValueError("Unknown register restriction fields")
        operand = rule.get("operand")
        if (
            not isinstance(operand, str)
            or not re.fullmatch(r"[VQDSHBXW]\w+", operand)
            or f"<{operand}>" not in pattern
        ):
            raise ValueError(f"Invalid restricted operand {operand!r}")
        when = rule.get("when", {})
        if not isinstance(when, dict):
            raise ValueError(
                "Restriction 'when' must map datatype placeholders to lists"
            )
        for name, values in when.items():
            if (
                name not in datatypes
                or not isinstance(values, list)
                or not values
                or not all(isinstance(v, str) and v for v in values)
            ):
                raise ValueError(f"Invalid restriction condition {name!r}: {values!r}")
        _restriction_registers(rule)


def _compile_restrictions(rules, pattern, operands):
    """Resolve named placeholders once, not on every parsed instruction."""
    _validate_restrictions(rules, pattern)
    datatypes = re.findall(r"<(dt\d*)>", pattern)
    compiled = []
    for rule in rules:
        locations = [
            (kind, i)
            for kind in _OPERANDS
            for i, operand in enumerate(operands[kind])
            if operand == rule["operand"]
        ]
        if len(locations) != 1:
            raise ValueError(
                f"Restricted operand {rule['operand']!r} must have exactly one role"
            )
        kind, index = locations[0]
        conditions = tuple(
            (datatypes.index(name), tuple(v.lower() for v in values))
            for name, values in rule.get("when", {}).items()
        )
        compiled.append(
            (conditions, _RESTRICTION_FIELDS[kind], index, _restriction_registers(rule))
        )
    return tuple(compiled)


def _apply_restrictions(obj, rules):
    datatypes = obj.datatype if isinstance(obj.datatype, list) else [obj.datatype]
    for conditions, field, index, registers in rules:
        if not all(str(datatypes[i]).lower() in values for i, values in conditions):
            continue
        restrictions = getattr(obj, field)
        previous = restrictions[index]
        # Multiple matching rules narrow the allocation set; never widen it.
        restrictions[index] = [
            r for r in registers if previous is None or r in previous
        ]


def _boolean(value):
    # The original scalar specification uses both JSON booleans and strings.
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in ("true", "false"):
        return value.lower() == "true"
    raise ValueError(f"Expected a boolean, got {value!r}")


def read_instruction_specs(path):
    """Read and validate a specification, accepting legacy unversioned files."""
    data = json.loads(Path(path).read_text(encoding="utf8"))
    if not isinstance(data, dict) or set(data) - {"schema_version", "instructions"}:
        raise ValueError(f"{path}: unsupported instruction specification")
    if data.get("schema_version", 1) != 1:
        raise ValueError(f"{path}: unsupported schema_version")
    entries = data.get("instructions")
    if not isinstance(entries, list):
        raise ValueError(f"{path}: instructions must be a list")
    names = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) - _FIELDS:
            raise ValueError(f"{path}: unknown instruction fields: {entry!r}")
        for key in ("name", "base", "pattern"):
            if not isinstance(entry.get(key), str) or not entry[key]:
                raise ValueError(f"{path}: missing or invalid {key}: {entry!r}")
        name = entry["name"]
        if not name.isidentifier() or name in names:
            raise ValueError(f"{path}: invalid or duplicate instruction name {name!r}")
        names.add(name)
        for field in _OPERANDS:
            if field not in entry:
                continue
            operands = entry[field]
            if not isinstance(operands, list) or not all(
                isinstance(op, str) and f"<{op}>" in entry["pattern"] for op in operands
            ):
                raise ValueError(f"{path}: {name}: invalid {field}")
        for field in (*_FLAGS, *_MEMORY):
            if field in entry:
                entry[field] = _boolean(entry[field])
        _validate_restrictions(entry.get("register_restrictions", []), entry["pattern"])
        _validate_operand_values(entry.get("operand_values", {}), entry["pattern"])
        validate_requirements(entry)
        addr = entry.get("addr_source")
        if addr is not None:
            if not isinstance(addr, dict):
                raise ValueError(f"{path}: {name}: invalid addr_source")
            kind = addr.get("type")
            if kind == "literal":
                valid = set(addr) == {"type", "value"} and isinstance(
                    addr["value"], str
                )
            else:
                valid = (
                    kind in ("inputs", "in_outs")
                    and set(addr) == {"type", "index"}
                    and type(addr["index"]) is int
                    and addr["index"] >= 0
                )
            if not valid:
                raise ValueError(f"{path}: {name}: invalid addr_source")
    return entries


def _make_factory(builder, spec, restrictions):
    def make(cls, src):
        obj = builder.build(cls, src)
        _check_operand_values(obj, spec.get("operand_values", {}), spec["pattern"])
        obj.increment = (
            obj.immediate if spec.get("set_increment_from_immediate") else None
        )
        obj.pre_index = obj.immediate if spec.get("pre_index_from_immediate") else None
        addr = spec.get("addr_source")
        if addr is not None:
            if addr["type"] == "literal":
                obj.addr = addr["value"]
            else:
                field = "args_in" if addr["type"] == "inputs" else "args_in_out"
                obj.addr = getattr(obj, field)[addr["index"]]
        if restrictions:
            _apply_restrictions(obj, restrictions)
        return obj

    return make


def _add_write(cls, restore_offset):
    def write(self):
        if restore_offset:
            self.immediate = simplify(self.pre_index)
        _check_operand_values(self, self.operand_values, self.pattern)
        return super(cls, self).write()

    cls.write = write


def generate_instruction_classes(specs, namespace, builder, register=None):
    """Generate classes in specification order; earlier entries may be bases.

    Omitted operand/flag fields are inherited. Architecture-specific hooks can
    be attached to the returned classes in Python, just as for handwritten ones.
    """
    exports = []
    for entry in specs:
        name = entry["name"]
        base = namespace.get(entry["base"])
        if not isinstance(base, type) or not issubclass(base, builder):
            raise ValueError(f"{name}: unknown instruction base {entry['base']!r}")
        if name in namespace:
            raise ValueError(f"{name}: instruction name already defined")
        attrs = {"pattern": entry["pattern"], "__module__": namespace["__name__"]}
        attrs["required_features"] = entry.get("required_features")
        attrs["conditional_features"] = entry.get("conditional_features", [])
        # Legality rules describe this concrete pattern, not its scheduling family.
        attrs["operand_values"] = entry.get("operand_values", {})
        attrs.update({key: entry[key] for key in (*_OPERANDS, *_FLAGS) if key in entry})
        rules = entry.get(
            "register_restrictions", getattr(base, "register_restrictions", [])
        )
        operands = {key: attrs.get(key, getattr(base, key, [])) for key in _OPERANDS}
        restrictions = _compile_restrictions(rules, entry["pattern"], operands)
        attrs["register_restrictions"] = rules
        cls = type(name, (base,), attrs)
        cls.make = classmethod(_make_factory(builder, entry, restrictions))
        if entry.get("restore_immediate_from_pre_index") or attrs["operand_values"]:
            _add_write(cls, entry.get("restore_immediate_from_pre_index", False))
        namespace[name] = cls
        if register is not None:
            register(cls)
        exports.append(name)
    return exports
