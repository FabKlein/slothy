# AArch64 instruction specifications

Simple instruction definitions are generated from two JSON files:

- `aarch64_scalar_instructions.json`: scalar instructions (173 definitions).
- `aarch64_neon_instructions.json`: 146 definitions (143 migrated plus three new),
  including vector FADD/FMUL, arithmetic, logical, shuffle, shift forms,
  and 17 register-restricted integer by-element forms. The new definitions are
  `fmov_w_to_s` (`fmov Sd,Wn`), `sfadd_d` (`fadd Dd,Da,Db`), and `vfcmla`
  (FP16/FP32 vector FCMLA).
  The second migration batch adds 28 existing declarations: TRN1/TRN2,
  AES/PMULL and AES wrapper pseudo-instructions, comparisons, UADDLV,
  GPR/vector transfers, and NOP. No instruction timings change in this migration.
  A further 26 memory definitions use the existing address/writeback fields:
  single/pair Q loads and stores, LD1/ST1, LD1R, stack, hint, and prefetch forms.

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
do not edit them by hand. They show concrete JSON fields after template expansion,
not Python-inherited metadata, Python-only definitions, or CPU timings.

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

The file contains an `"instructions"` array. Version 1 contains explicit
definitions; version 2 additionally supports named templates (used by the NEON
file). The existing unversioned scalar file is also accepted as version 1. Unknown fields,
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
| `operand_values` | Finite legal values for named datatype placeholders and a single immediate, checked when parsing and writing |
| `required_features` | Explicit ISA requirements for this concrete instruction; omitted means unclassified, `[]` means baseline A64 |
| `conditional_features` | Additional ISA requirements selected by datatype placeholders; see below |
| `addr_source` | Address operand: `{"type": "inputs", "index": 0}`, `in_outs`, or `{"type": "literal", "value": "sp"}` |
| `set_increment_from_immediate` | Model immediate address writeback; the pattern retains pre-/post-index syntax |
| `pre_index_from_immediate` | Model the immediate address offset |
| `restore_immediate_from_pre_index` | Write the adjusted address offset back into assembly |

Use JSON `true`/`false` for new boolean fields. Legacy scalar strings
`"True"`/`"False"` remain supported. Omitted operand and flag fields are inherited
from the base class. For example, `vfmla` inherits its read/write accumulator
from `vmla`. Define bases before subclasses. If adding a concrete instruction
subclass, ensure its concrete parent remains in parser discovery as well;
`iter_aarch64_instructions()` explicitly retains `vmla` and `vmls` for this reason.

## Named templates (schema version 2)

Templates share JSON fields without introducing Python classes or changing
instruction-family inheritance. For example:

```json
{
  "schema_version": 2,
  "templates": {
    "neon_logical_binary": {
      "base": "AArch64NeonLogical",
      "pattern": "{mnemonic} <Vd>.<dt>, <Va>.<dt>, <Vb>.<dt>",
      "inputs": ["Va", "Vb"],
      "outputs": ["Vd"],
      "required_features": ["FEAT_AdvSIMD"]
    }
  },
  "instructions": [
    {"name": "vand", "template": "neon_logical_binary", "mnemonic": "and"},
    {"name": "veor", "template": "neon_logical_binary", "mnemonic": "eor"}
  ]
}
```

The loader expands each reference into an independent concrete definition before
ordinary validation and class generation. The documentation generator uses the
same expansion, so tables display full assembly patterns and operand roles,
not template references. The standalone generator remains standard-library-only.

- `templates` is an optional object mapping identifier names to field defaults.
  Templates may contain instruction fields other than `name`; they cannot
  contain `template` or `mnemonic`. There is no nested template inheritance.
- Each instruction supplies its own `name` and may select exactly one template.
  Its explicit fields override the template's fields. Lists and dictionaries
  replace whole fields; they are not concatenated or recursively merged.
  Use `[]` or `{}` to clear the corresponding defaults. When changing operand
  roles, explicitly clear the old role as well as supplying the new one.
- `{mnemonic}` is the only substitution parameter, allowed once as the leading
  token of a templated pattern. Supply `mnemonic` on that instruction; it must
  be a single mnemonic, not arbitrary assembly. Literal register-list braces
  such as `{<Va>.<dt>}` are preserved. This is not Python string formatting.
- A template can instead contain a fixed pattern, or the instruction can
  override the pattern entirely. Omit `mnemonic` when no substitution is needed.
  An explicit instruction without `template` retains the version-1 syntax.
- Names, definition order, bases, and operand placeholder spelling are preserved.
  Template defaults for ISA requirements become explicit metadata on each
  expanded instruction; this does not enable ISA inheritance from Python bases.
- Unknown templates/fields, nested template references, missing substitutions,
  duplicate instruction names, and invalid expanded definitions are rejected.
  Version 1 and unversioned files reject template syntax and retain their
  existing behavior.

The initial migration covers 12 definitions in four templates: ADD/FADD/SUB,
AND/BIC/ORR/ORN/EOR, MUL/FMUL, and MLA/MLS. FP16 conditions remain explicit
overrides on FADD/FMUL. FP accumulator subclasses retain their existing Python
inheritance. Lane, memory, and exceptional forms remain explicit for now.
This is a representation-only change: it adds no accepted operand forms, ISA
features, timing entries, or new inheritance relationships.

## Finite operand values and FCMLA

`vfcmla` models the destination as a read/write accumulator and the two source
vectors as inputs. Its pattern uses the same `<dt>` for all three operands,
requiring matching arrangements. It also declares:

```json
"operand_values": {
  "dt": ["4h", "8h", "2s", "4s"],
  "imm": [0, 90, 180, 270]
}
```

These are parser/writer legality checks, not allocator restrictions. Datatype
keys must name an existing `dt`/`dtN` placeholder; every occurrence of that name
must have the same allowed value, case-insensitively. `imm` requires exactly one
`<imm>` placeholder and a nonempty list of distinct JSON integers. Immediate
expressions must simplify to an allowed integer; unresolved symbols are rejected.
Empty, duplicate, or malformed value sets are rejected when loading the JSON.
Rules apply to the concrete definition and are not inherited from scheduling
families. Existing definitions without these rules retain their previous behavior.

FCMLA accepts `.4h`, `.8h`, `.2s`, and `.4s`, with rotations `#0`, `#90`, `#180`,
and `#270`. FP64 and indexed/by-element forms are not included in this increment.
For example: `fcmla v9.8h, v3.8h, v2.8h, #90`.
It requires `FEAT_FCMA` (Armv8.3-A), plus `FEAT_FP16` for the half-precision forms.
A320/A520 have explicit support and timings; the A55 profile rejects FCMA.

AArch64 functional self-tests enable LLVM's `complxnum` and `fullfp16` features
and use Unicorn's maximum-feature CPU with FP/SIMD access enabled. This is a
functional emulator configuration, not a performance model or evidence of target
ISA support; the separate target ISA validation still runs normally.

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
description. Except for explicit `operand_values` rules, `<dt>`, `<index>`, and
immediate placeholders retain the existing parser semantics. JSON does not yet
express lane-range relationships or consecutive-register groups.

The remaining concrete Python declarations have `make`/`write` methods, including
FP by-element lane validation, forced-output variants, and multi-register
relationships. LDUR retains signed-offset validation in both parsing and writing.
Grouped LD1/LD2/ST1 forms retain their consecutive-register constraints and lane
callbacks. Register-offset Q loads stay in Python pending an audit of their shift
versus address-offset metadata. Two-table TBL keeps its group-register constraints.
Family classes such as `Transpose`, `AESInstruction`, and `Fmov` remain in Python
to preserve the inheritance relationships used by CPU models.

Python parsing/fusion callbacks can still be attached to generated classes;
`vins_d`, `fmov_0`, and `fmov_1` keep their existing parsing callbacks. The FMOV
forced-output classes and their parsing guards remain handwritten, with explicit
FP requirements so callback-rewritten graphs also pass ISA validation.
Pseudo-instructions do not intrinsically require Python: `aesr` and the related
AES wrappers are now declared in JSON, preserving their existing operand roles
and grouping semantics. Their assembly macro definitions are unchanged.
Keep nontrivial semantics in Python until the shared schema can express them
and equivalent behavior is covered by tests.

Execution units, inverse throughput, latency, forwarding, and other scheduling
constraints remain in CPU-specific models (`cortex_a520.py`, `cortex_a55.py`,
etc.). Adding JSON syntax alone does **not** add timing support to every CPU.
This migration does not change CPU timing tables or fill their coverage gaps.

## Memory definitions and compatibility

The memory migration preserves class names, operand roles, address metadata,
writeback amounts, and existing offset rewriting. In particular:

- Offset-only forms use an input base and `pre_index_from_immediate`; their
  writers restore adjusted offsets with `restore_immediate_from_pre_index`.
- Writeback forms use a read/write base and `set_increment_from_immediate`.
  The assembly pattern distinguishes `[base, #imm]!` from `[base], #imm`.
  Existing pre-index writeback metadata is retained (`increment` set,
  `pre_index` unset); this is not a redesign of the address model.
- LD1R post-increments by the element size (for example, `.4s` uses `#4`),
  not by the full vector size. Q-pair loads/stores preserve both vector operands.
- Stack forms retain a literal `sp` address. TODO: model their SP register
  dependency explicitly; this limitation predates the migration.

Compatibility does not imply architectural validity. The `ldrh`/`strh` hint
forms are pseudo-instructions; the legacy `q_ld1_with_inc` immediate-offset
syntax and `prefetch` hint spelling `pld1lkeep` are also retained unchanged.
The architectural PRFM hint is `pldl1keep`; correcting the legacy parser form
is separate from this behavior-preserving migration. PRFM still lacks the
adjusted-offset writer used by the ordinary immediate-offset forms. Lane and
immediate-range legality is not newly validated by moving a definition into JSON.

The migrated memory forms explicitly require FP for SIMD/FP LDR/STR/LDP/STP,
Advanced SIMD for LD1/ST1/LD1R, and no extension for PRFM. Regression snapshots
compare parsing, writing, memory metadata, and model queries on all eight
AArch64 targets. Additional tests cover offset fixups, assembly of architectural
forms, pre-/post-index execution, and a software-pipelined pair-load/replicate/
pair-store loop executed with Unicorn on disjoint buffers.

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
| FCMA | Unsupported | Enabled |

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

All 146 JSON NEON definitions have explicit ISA requirements, as do scalar CRC32
forms, selected scalar arithmetic/FP forms, and handwritten FP-lane, TBL,
forced-output FMOV, and forced-output INS forms. Other scalar and handwritten instructions
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

- [Arm instruction reference, FCMLA vector](https://documentation-service.arm.com/static/6245c734b059dc5ff9a8bdab)
  specifies matching arrangements, rotations, and Armv8.3-A availability.
- [Cortex-A320 TRM, supported features](https://documentation-service.arm.com/static/67f03a3d98aa3c3b6eea9633)
  lists FEAT_FCMA support explicitly.
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

`test_aarch64_instruction_templates.py` checks version compatibility, expansion,
whole-field overrides, independent mutable fields, preserved class bases,
register-list braces, malformed templates, and validation after expansion.
The 12 migrated definitions are compared field-for-field against a pre-template
fixture, including their order and exact operand placeholders. Existing parser,
ISA, CPU-model, scheduling, and execution regressions continue to exercise the
same generated classes.

`test_aarch64_isa.py` checks feature requirements and datatype conditions,
configuration overrides, unknown-metadata policy, pre-scheduling rejection,
fusion output validation, and strict straightline/software-pipelined scheduling.

`test_aarch64_neon_declarative_migration.py` compares the second batch's 28
definitions against observations from commit `995e8b4`, covering parser/writer
behavior, operand metadata, inheritance, and all eight AArch64 CPU models
(including pre-existing unsupported timing lookups). It also checks assembler
acceptance of the real instructions, retained FMOV callbacks, and that plain
declarations do not drift back into Python. AES pseudo-instructions are parser
probes, not standalone architectural instructions, and are excluded from that
assembler check.

The later A320/A520 coverage update intentionally changes five migrated classes'
A520 lookup results. Those results are tested in `test_armv9_models.py` instead
of compared against the old snapshot; parser metadata and A55 comparisons remain.
The subsequent operand-specific timing update also changes the MLA/MLS `.4s`
accumulator-chain snapshot latency to two cycles, retaining its original
unit/occupancy comparisons. `test_armv9_timing.py` checks this bypass and its
exclusions, as well as the scoped logical and transfer resource refinements.
