# AArch64 instruction specifications

Simple instruction definitions are generated from two JSON files:

- `aarch64_scalar_instructions.json`: scalar instructions (173 definitions).
- `aarch64_neon_instructions.json`: 91 definitions (89 migrated plus two new),
  including vector FADD/FMUL, arithmetic, logical, shuffle, shift forms,
  and 17 register-restricted integer by-element forms. The new definitions are
  `fmov_w_to_s` (`fmov Sd,Wn`) and `sfadd_d` (`fadd Dd,Da,Db`).

Both use `instruction_loader.py`. The NEON classes are generated inside
`aarch64_neon.py` before parser discovery and callback registration. Scalar
classes are generated inside `aarch64.py` and re-exported by `aarch64_neon.py`.
Existing class names, modules, inheritance, and aliases are preserved, including
`vfmul = vmulf`, `lsr_variable = lsr`, and `csel_ne = csel`.
Both JSON files are included in built packages.

## Generated reference tables

JSON is the source of truth. The readable tables
[aarch64_scalar_inst.md](aarch64_scalar_inst.md) and
[aarch64_neon_inst.md](aarch64_neon_inst.md) are generated documentation;
do not edit them by hand. They show only explicit JSON fields, not inherited
metadata, Python-only definitions, or CPU timings.

After changing either specification, regenerate both tables from the repository root:

```sh
python3 slothy/targets/aarch64/dump_instruction_tables.py
```

Check that the committed tables are up to date without modifying them:

```sh
python3 slothy/targets/aarch64/dump_instruction_tables.py --check
```

Unit tests also check that both tables match the generator. Generation is not
performed automatically when importing Slothy. The legacy `dump_scalar_inst.py`
still prints the scalar table to stdout. `load_scalar_table.py` remains a legacy
reverse-import utility, not the normal editing workflow; it overwrites the JSON
and should not be run against a stale table.

## Adding a simple instruction

Add an entry to the relevant JSON file; no matching Python class is needed:

```json
{
  "name": "vaddf",
  "base": "AArch64Instruction",
  "pattern": "fadd <Va>.<dt>, <Vb>.<dt>, <Vc>.<dt>",
  "inputs": ["Vb", "Vc"],
  "outputs": ["Va"]
}
```

The file contains `"schema_version": 1` and an `"instructions"` array. The
existing unversioned scalar file is also accepted as version 1. Unknown fields,
duplicate instruction names, invalid operand placeholders, and malformed
booleans are rejected. Class names must not overwrite existing Python names.

| Field | Meaning |
| --- | --- |
| `name` | Public Python class name, also referenced by CPU models |
| `base` | Existing Python instruction family or an earlier JSON entry |
| `pattern` | Existing `AArch64Instruction` parser/writer template |
| `inputs` / `outputs` / `in_outs` | Read-only, write-only, and read/write register placeholders |
| `dependsOnFlags` / `modifiesFlags` | Read/write dependencies on architectural flags |
| `register_restrictions` | Conditional or unconditional allocation rules for named operands; see below |
| `required_features` | Explicit ISA requirements for this concrete instruction; omitted means unclassified, `[]` means baseline A64 |
| `conditional_features` | Additional ISA requirements selected by datatype placeholders; see below |
| `addr_source` | Address operand: `{"type": "inputs", "index": 0}`, `in_outs`, or `{"type": "literal", "value": "sp"}` |
| `set_increment_from_immediate` | Model an immediate post-increment |
| `pre_index_from_immediate` | Model the immediate address offset |
| `restore_immediate_from_pre_index` | Write the adjusted address offset back into assembly |

Use JSON `true`/`false` for new boolean fields. Legacy scalar strings
`"True"`/`"False"` remain supported. Omitted operand and flag fields are inherited
from the base class. For example, `vfmla` inherits its read/write accumulator
from `vmla`. Define bases before subclasses. If adding a concrete instruction
subclass, ensure its concrete parent remains in parser discovery as well;
`iter_aarch64_instructions()` explicitly retains `vmla` and `vmls` for this reason.

## Conditional register restrictions

The by-element `vqrdmulh_lane` and `vqdmulh_lane` definitions use:

```json
"register_restrictions": [
  {
    "operand": "Vb",
    "when": {"dt1": ["h"]},
    "registers": {"prefix": "v", "first": 0, "last": 15}
  }
]
```

For the pattern `sqrdmulh <Vd>.<dt0>, <Va>.<dt0>, <Vb>.<dt1>[<index>]`,
this restricts the lane-source operand `Vb` to `v0`–`v15` whenever `dt1` is
`h`, covering both `4h` and `8h` vectors. With `dt1` equal to `s`, the rule
does not apply. This follows the halfword lane-source encoding restriction
in the [Arm Compiler armasm Reference Guide](https://documentation-service.arm.com/static/5f3fa899428f7a6b3328fd44).
It also fixes the former Python check, which covered only lowercase `8h`.

The same mechanism covers 15 more integer lane forms:

- `vmul_lane`, `vmla_lane`, `vmls_lane` use `when: {"dt1": ["h"]}`.
- `vumull_lane`, `vumull2_lane`, `vsmull_lane`, `vsmull2_lane`;
  `vumlal_lane`, `vumlal2_lane`, `vsmlal_lane`, `vsmlal2_lane`;
  `vumlsl_lane`, `vumlsl2_lane`, `vsmlsl_lane`, `vsmlsl2_lane`
  use `when: {"dt2": ["h"]}` because widening patterns have distinct
  destination, vector-source, and lane-source datatype placeholders.

For widening forms the condition follows the source element, not the widened
destination. Halfword lane sources use `v0`–`v15`; word lane sources may use
`v0`–`v31`. MUL/MLA/MLS now cover `4h` as well as `8h`, and every migrated
form handles uppercase datatype suffixes. Multiply destinations remain outputs;
accumulate/subtract destinations remain read/write operands. Existing class
names and instruction-family inheritance are preserved.

- `operand` names a pattern placeholder declared in exactly one of `inputs`,
  `outputs`, or `in_outs`. Reordering these lists does not change the rule's target.
- `when` maps datatype placeholders (`dt`, `dt0`, etc.) to accepted values.
  Comparisons are case-insensitive; all specified conditions must match.
  Repeated placeholders are resolved by name. Omit `when` for an unconditional rule.
- `registers` is either an inclusive range as above or an explicit list,
  such as `["v0", "v2", "v4"]`. Names use the allocator's canonical `v`/`x`
  spelling; ranges must fit `v0`–`v31` or `x0`–`x30` and match the operand family.
- Multiple matching rules intersect the permitted registers. Each instruction
  instance receives its own restriction lists.
- Omitted `register_restrictions` inherits the base class's rules, resolving
  names against the child's pattern and operands. An explicit list replaces
  inherited rules; `[]` clears them.

The loader validates rule structure and resolves names when generating classes.
These are **allocator constraints**, not parser rejection rules: a concrete
illegal register can still parse, but a fixed-register optimization cannot
satisfy its allocation constraints. No CPU timing table changes are needed
for the JSON migration itself. A subsequent A520 model fix adds the missing
`vmul_lane` execution-unit entry: either VEC0 or VEC1, retaining one-cycle
resource occupancy and four-cycle latency. All integer lane forms now have
allocator/scheduling tests on A320, A520, and A55.

## What stays in Python

This is an incremental migration, not a new assembler or a complete NEON ISA
description. `<dt>`, `<index>`, and immediate placeholders retain the existing
parser semantics; JSON does not yet add architectural arrangement/lane-range
validation or consecutive-register groups.

Instructions requiring custom `make`/`write` methods remain in Python, including
FP by-element lane validation, other custom register relationships, and multi-register
loads/stores and table lookups. Python parsing/fusion callbacks can still be
attached to generated classes; `vins_d` keeps its existing parsing callback.
Keep nontrivial semantics in Python until the shared schema can express them
and equivalent behavior is covered by tests.

Execution units, inverse throughput, latency, forwarding, and other scheduling
constraints remain in CPU-specific models (`cortex_a520.py`, `cortex_a55.py`,
etc.). Adding JSON syntax alone does **not** add timing support to every CPU.
This migration does not change CPU timing tables or fill their coverage gaps.

## ISA requirements and target capabilities

ISA support and scheduling support are independent. An instruction may parse
and be supported by the CPU, yet lack a latency or execution-unit entry in
Slothy. Conversely, a timing-table entry does not establish ISA availability.

`isa.py` holds a small feature registry with earliest architectural availability
and instruction-level prerequisites. These versions mean "permitted from",
not "implemented by every CPU of this version". Target capabilities are
explicit: no feature is enabled merely by comparing architecture version numbers,
and Armv9 is not treated as a numeric superset of all Armv8 extensions.
For future DotProd/I8MM definitions the registry also records the compiler
architecture defaults: Armv8.4-A and Armv8.6-A respectively, versus optional
availability from Armv8.2-A for both. These are reference metadata, not an
automatic target-feature expansion rule; an omitted default means unspecified.

The initial target profiles cover Cortex-A55 (`armv8.2-a`) and Cortex-A320/A520
(`armv9.2-a`). They are partial profiles, not exhaustive processor feature lists:

| Registered feature | A55 default | A320/A520 default |
| --- | --- | --- |
| FP, Advanced SIMD, FP16, RDM, CRC32 | Enabled | Enabled |
| AES, PMULL | Assumed enabled | Assumed enabled |
| SHA3 | Unsupported | Assumed enabled |
| DotProd | Assumed enabled | Enabled |
| I8MM | Unsupported | Enabled |

Optional FP/Advanced SIMD and cryptographic facilities are assumed available
where applicable. A55 dot-product support is also an implementation option.
These defaults describe the modeled configuration, not a probe of the host or
the deployment hardware. Override them for a reduced implementation or execution
environment. Other target models have unknown capabilities until annotated;
they do not silently inherit one of these profiles.

### Instruction metadata

For example, the existing vector FADD definition has:

```json
"required_features": ["FEAT_AdvSIMD"],
"conditional_features": [
  {"when": {"dt": ["4h", "8h"]}, "requires": ["FEAT_FP16"]}
]
```

All unconditional requirements and matching conditional requirements must be
satisfied. Dependencies are expanded, so Advanced SIMD also requires FP.
`when` keys name datatype placeholders in the instruction pattern; values are
case-insensitive exact matches. Multiple conditions in one rule are ANDed.
FP by-element forms use `dt1: ["h"]`. Integer halfword arithmetic does not
require FP16. Unknown feature names, duplicate requirements, and malformed
conditions are rejected when loading JSON.

Handwritten instruction classes use the same `required_features` and
`conditional_features` attributes. Requirements must be declared on each
concrete class: unlike operands, they are deliberately **not inherited**.
For example, FP MLA subclasses integer MLA for scheduling, and PMULL subclasses
an AES family, but neither relationship establishes the ISA requirements.
Missing requirements mean unclassified, even if the parent has metadata.

This increment annotates all 91 JSON NEON definitions, scalar CRC32 forms,
selected scalar arithmetic/FP forms, and handwritten AES/PMULL, FP-lane, TBL,
NOP, and forced-output INS forms. Other scalar and handwritten instructions
remain unclassified. SQ(R)DMULH is baseline Advanced SIMD, not FEAT_RDM;
RDM covers the later rounding multiply-accumulate/subtract forms, which are
not currently defined here. DotProd and I8MM are registered for future use:
**no SDOT/SMMLA parsers or timings are added by this change**.

### Validation and configuration

`config.isa_check` controls validation:

- `warn` (default): reject known unsupported/disabled features, but warn and
  continue for unclassified instructions or unknown target capabilities.
- `strict`: also reject incomplete ISA metadata. This does not make an
  unaudited instruction or target supported; additional annotations may be needed.
- `off`: disable ISA checking explicitly, retaining legacy behavior.

`config.isa_features` maps registered feature names to booleans. For example,
from Python: `config.isa_features = {"FEAT_FP16": False}`. Overrides can disable
features or explicitly assert support where a target's metadata is unknown.
They cannot enable features declared unsupported by that CPU (such as I8MM
on A55). Disabling a prerequisite also prevents instructions that require it.
Overrides describe the usable subset; they do not add instruction definitions,
timing entries, or change the processor architecture.

The corresponding CLI options are:

```sh
-c isa_check=strict
-c 'isa_features={FEAT_FP16:False}'
```

Checks run when constructing dataflow graphs, before scheduling and again when
parsing/fusion callbacks rebuild them. Thus EOR-to-EOR3 fusion cannot silently
introduce SHA3 on A55. `UnsupportedISA` reports a known incompatibility;
`UnknownISA` reports incomplete metadata in strict mode. Missing timing entries
remain separate `UnknownInstruction` scheduling-model errors. Checking is
independent of `selftest` and functional-only scheduling. Architectures without
the validation hook retain their existing behavior.

Only instructions processed by Slothy are checked, not untouched file regions,
external code, assembler architecture directives, or runtime OS enablement.
Feature validation does not replace assembler encoding checks or execution tests.

### Sources

- [Arm compiler feature options](https://documentation-service.arm.com/static/671fa191ad463325b23263ce)
  distinguish optional architectural availability from default enablement.
- [Arm's dot-product overview](https://developer.arm.com/community/arm-community-blogs/b/tools-software-ides-blog/posts/exploring-the-arm-dot-product-instructions)
  describes configurable A55 dot-product support.
- [Cortex-A55 cryptographic extension TRM](https://documentation-service.arm.com/static/649ac68e38511951cb79901e)
  describes the optional crypto facilities and identification registers.
- [Cortex-A520 supported standards](https://support.arm.com/documentation/102517/0004/The-Cortex-A520--core/Supported-standards-and-specifications)
  and [cryptographic extension TRM](https://documentation-service.arm.com/static/672e536f27eda361ad4da11a)
  describe implemented features and configurable crypto support.
- [Cortex-A320 introduction](https://newsroom.arm.com/blog/introducing-arm-cortex-a320-cpu)
  and [software optimization guide](https://documentation-service.arm.com/static/680122175b1a8c5a27aa1aa7)
  describe its architecture and instruction families.

When extending an instruction:

1. Add its definition, or retain a Python implementation for custom semantics.
2. Add the relevant CPU model entries and check for overlapping family matches.
3. Test parsing/writing, register and flag dependencies, and address fixups.
4. Test scheduling and assembler acceptance; use execution tests where available.
5. Regenerate both reference tables after changing either JSON specification.

## Regression checks

```sh
venv/bin/python -m unittest discover -s tests/unit -v
venv/bin/python test.py --tests instructions_a55,instructions_m55 --dry-run --silent
```

`test_aarch64_instruction_specs.py` compares all 72 migrated NEON definitions
against observations captured from the Python definitions at commit `dabafcd`.
These cover parser selection, inheritance, operands/restrictions, assembly
writing, and A55/A520 unit/throughput/latency lookup results (including existing
unsupported-instruction errors). Callback addresses are normalized; callback
semantics are not asserted by the snapshot. The snapshots are parser probes,
not proof that every probe is architecturally legal assembly. Existing FP-lane,
merge-compatibility, scheduling, and execution tests provide additional coverage.

The loader tests also check conditional rules, inheritance, intersections,
operand roles, and malformed specifications. `test_aarch64_lane_restrictions.py`
checks all 17 lane definitions, case-insensitive datatype round-trips,
symbolic operands, fixed-register allocator enforcement, and assembler acceptance
at the halfword/word register boundaries.

`test_aarch64_isa.py` checks feature requirements and datatype conditions,
configuration overrides, unknown-metadata policy, pre-scheduling rejection,
fusion output validation, and strict straightline/software-pipelined scheduling.

The later A320/A520 coverage update intentionally changes five migrated classes'
A520 lookup results. Those results are tested in `test_armv9_models.py` instead
of compared against the old snapshot; parser metadata and A55 comparisons remain.
The subsequent operand-specific timing update also changes the MLA/MLS `.4s`
accumulator-chain snapshot latency to two cycles, retaining its original
unit/occupancy comparisons. `test_armv9_timing.py` checks this bypass and its
exclusions, as well as the scoped logical and transfer resource refinements.
