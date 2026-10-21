"""Partial AArch64 ISA requirements, independent of instruction timing models.

Availability versions describe the earliest architecture permitting a feature,
not a promise that every processor of that version implements it. See
README.instructions.md for sources, target assumptions, and migration policy.
"""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Feature:
    """An architectural feature and its prerequisite features."""

    available_from: str
    requires: tuple = ()
    default_from: str | None = None


FEATURES = {
    "FEAT_FP": Feature("armv8.0-a"),
    "FEAT_AdvSIMD": Feature("armv8.0-a", ("FEAT_FP",)),
    "FEAT_FP16": Feature("armv8.2-a", ("FEAT_FP",)),
    "FEAT_FCMA": Feature("armv8.3-a", ("FEAT_AdvSIMD",)),
    "FEAT_RDM": Feature("armv8.1-a", ("FEAT_AdvSIMD",)),
    "FEAT_CRC32": Feature("armv8.0-a"),
    "FEAT_AES": Feature("armv8.0-a", ("FEAT_AdvSIMD",)),
    "FEAT_PMULL": Feature("armv8.0-a", ("FEAT_AdvSIMD",)),
    "FEAT_SHA3": Feature("armv8.2-a", ("FEAT_AdvSIMD",)),
    # Reserved for future definitions; this does not add instruction support.
    "FEAT_DotProd": Feature("armv8.2-a", ("FEAT_AdvSIMD",), "armv8.4-a"),
    "FEAT_I8MM": Feature("armv8.2-a", ("FEAT_AdvSIMD",), "armv8.6-a"),
}


@dataclass(frozen=True)
class TargetISA:
    """Explicit target assumptions; absent features remain unknown, not unsupported."""

    architecture: str
    enabled: frozenset
    unsupported: frozenset = frozenset()

    def __post_init__(self):
        validate_feature_list(list(self.enabled))
        validate_feature_list(list(self.unsupported))
        if self.enabled & self.unsupported:
            raise ValueError("ISA features cannot be both enabled and unsupported")


class UnsupportedISA(Exception):
    """The selected target cannot execute an instruction's required ISA features."""


class UnknownISA(Exception):
    """Strict checking found incomplete instruction or target ISA metadata."""


def validate_feature_list(features):
    """Reject malformed lists, unknown feature names, and duplicates."""
    if not isinstance(features, list) or not all(
        isinstance(feature, str) and feature in FEATURES for feature in features
    ):
        raise ValueError(f"Expected a list of known ISA features, got {features!r}")
    if len(features) != len(set(features)):
        raise ValueError("Duplicate ISA feature")


def validate_requirements(entry):
    """Validate unconditional and datatype-dependent instruction requirements."""
    if "required_features" in entry:
        validate_feature_list(entry["required_features"])
    rules = entry.get("conditional_features", [])
    if not isinstance(rules, list):
        raise ValueError("conditional_features must be a list")
    if rules and "required_features" not in entry:
        raise ValueError("conditional_features requires explicit required_features")
    datatypes = re.findall(r"<(dt\d*)>", entry["pattern"])
    for rule in rules:
        if not isinstance(rule, dict) or set(rule) != {"when", "requires"}:
            raise ValueError("Conditional feature rules require when and requires")
        validate_feature_list(rule["requires"])
        when = rule["when"]
        if not isinstance(when, dict) or not when:
            raise ValueError("Conditional features need nonempty datatype conditions")
        for field, values in when.items():
            if (
                field not in datatypes
                or not isinstance(values, list)
                or not values
                or not all(isinstance(value, str) and value for value in values)
            ):
                raise ValueError(f"Invalid feature condition: {field!r}: {values!r}")


def instruction_features(inst):
    """Return resolved requirements, or None for an unaudited concrete class."""
    # Python inheritance expresses scheduling families, not necessarily ISA semantics.
    # Never silently inherit a concrete parent's requirements into a new instruction.
    attrs = type(inst).__dict__
    required = attrs.get("required_features")
    if required is None:
        return None
    rules = attrs.get("conditional_features", [])
    validate_requirements(
        dict(
            required_features=required, conditional_features=rules, pattern=inst.pattern
        )
    )
    result = set(required)
    names = re.findall(r"<(dt\d*)>", inst.pattern)
    values = inst.datatype if isinstance(inst.datatype, list) else [inst.datatype]
    for rule in rules:
        if all(
            str(values[names.index(name)]).lower() in [v.lower() for v in allowed]
            for name, allowed in rule["when"].items()
        ):
            result.update(rule["requires"])
    pending = list(result)
    while pending:
        for dependency in FEATURES[pending.pop()].requires:
            if dependency not in result:
                result.add(dependency)
                pending.append(dependency)
    return frozenset(result)


def target_features(target, overrides):
    """Resolve the target profile and explicit user configuration assertions."""
    profile = getattr(target, "isa", None)
    states = {}
    if profile is not None:
        states.update(dict.fromkeys(profile.enabled, True))
        states.update(dict.fromkeys(profile.unsupported, False))
    if not isinstance(overrides, dict):
        raise ValueError("isa_features must map feature names to booleans")
    validate_feature_list(list(overrides))
    for feature, enabled in overrides.items():
        if type(enabled) is not bool:
            raise ValueError(f"isa_features[{feature!r}] must be a boolean")
        if enabled and profile is not None and feature in profile.unsupported:
            raise ValueError(f"Cannot enable {feature}: unsupported by this target")
        states[feature] = enabled
    return states


def validate_instruction_features(instructions, config, logger):
    """Reject known incompatibilities; warn or fail on incomplete ISA metadata."""
    mode = config.isa_check
    if mode not in ("off", "warn", "strict"):
        raise ValueError("isa_check must be off, warn, or strict")
    if mode == "off":
        return
    states = target_features(config.target, config.isa_features)
    name = getattr(config.target, "llvm_mca_target", "selected target")
    unknown = set()
    for inst in instructions:
        required = instruction_features(inst)
        if required is None:
            unknown.add(f"unclassified instruction {type(inst).__name__}")
            continue
        missing = sorted(f for f in required if states.get(f) is False)
        if missing:
            raise UnsupportedISA(
                f"{inst}: requires {', '.join(missing)}, unavailable on {name} "
                "under the selected ISA configuration"
            )
        unknown.update(
            f"unknown {feature} support on {name}"
            for feature in required
            if states.get(feature) is None
        )
    if unknown:
        message = "Incomplete ISA validation: " + "; ".join(sorted(unknown))
        if mode == "strict":
            raise UnknownISA(message)
        # Self-checks and address fixups rebuild the same graphs. Avoid emitting
        # the same warning repeatedly for an unchanged configuration.
        cache = config._isa_warning_cache
        key = (name, tuple(sorted(states.items())), message)
        if key not in cache:
            logger.warning(message)
            cache.add(key)
