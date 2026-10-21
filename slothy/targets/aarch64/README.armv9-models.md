# A320/A520 model coverage follow-up

The October 2026 update ports instruction **coverage**, not Cortex-A55 timings.
Sources:

- [A320 SWOG, 110285 Issue 01](https://documentation-service.arm.com/static/680122175b1a8c5a27aa1aa7)
- [A520 SWOG, PJDOC-1505342170-671342 Issue 1.2, r0p1](https://documentation-service.arm.com/static/65fddf771bc22b03bca907cb)

Use sections 3.3/3.6 for scalar operations, 3.4 for integer multiply,
3.7/3.8 for scalar memory, 3.12 for scalar FP arithmetic,
3.13 for FMOV, 3.14 for vector pairs, 3.16/3.19 for vector operations,
3.17 for vector FP arithmetic including FCMLA,
3.20/3.21 for structure memory, and 3.23 for CRC.

## Scope

Both models now cover scalar ASR/LSR, CMP with XZR, CSEL, register MOV,
shifted MOVK, SXTB/UXTB, CRC32/CRC32C, the missing SIMD transfers,
register USHL, two-table TBL, W-register pairs, two-register LD1,
four-register post-increment ST1, and lane LD2. A320 also gains Q-pair loads;
A520's existing Q-pair entries are retained.

FP16/FP32 vector FCMLA is supported for `.4h`, `.8h`, `.2s`, and `.4s`, with
rotations 0, 90, 180, and 270 degrees. Both cores use four-cycle latency for
accumulator and either source-operand dependencies, without a shorter MAC bypass.
Following SWOG section 3.17 (A320 page 29; A520 page 34), A320 models one FCMLA
per cycle and A520 (2x128) two per cycle: one-cycle occupancy on VEC0 for A320,
or on either VEC0 or VEC1 for A520. Do not reserve both A520 resources together
or encode fractional resource occupancy. These abstract resources approximate
VMAC scheduling; they do not establish all mixed-instruction contention behavior.
The rates count individual FCMLA instructions, not pairs of rotations making up
a complete complex multiply-accumulate. Indexed forms and FP64 are not included.

A subsequent fix adds A520's missing `vmul_lane` execution-unit entry for
integer MUL by element, using either VEC0 or VEC1 like vector MUL. Existing
resource occupancy 1 and latency 4 are retained. This maps the SWOG section
3.16 ASIMD multiply rate of two instructions/cycle (2x128 configuration) onto
the model's two abstract vector resources; it does not reserve both at once.

Duplicate matches for stack LDR/STR, lane LD2, and UXTL are removed. Stack
accesses use the existing Ldr_X/Str_X family entries; UXTL uses its existing
shift-family latency. Lane LD2 now has a single explicit LSU entry.
This is not a complete retiming of the older models. Older instruction variants,
forwarding rules, and hazard rules remain unless noted.

The shared architecture now classifies the new memory forms correctly, so
they participate in memory handling and existing target hazard predicates.
Non-post-increment lane LD2 preserves its untouched lanes through read/write
vector operands. Two-table TBL accepts both 8B and 16B results with 16B tables.

## Timing and resource caveats

The A520 target continues to assume **2x128-bit vector datapaths**, as confirmed
for the user's target. There is no selectable 2x64-bit configuration yet; do not
use these estimates for that configuration. Adding it requires auditing existing
vector entries as well as the new ones, not just changing an issue-rate constant.

Examples of CPU-specific choices:

| Operation | A320 | A520 (2x128) |
| --- | --- | --- |
| CRC | MAC, latency 2 | MAC, latency 2 |
| USHL | latency 3 | latency 3 |
| Two-table TBL, general path | latency 5 | latency 8 |
| Two-register LD1, Q form | latency 4, interval 2 | latency 3, interval 1 |
| Lane LD2 | latency 4, interval 6 | latency 4, interval 2 |

`get_inverse_throughput()` means integer **resource occupancy**, not necessarily
the reciprocal of whole-core throughput. A520 two-table TBL occupies either
VEC resource for five cycles, modeling two instructions per five cycles. A320
uses two-cycle occupancy on its single abstract VEC resource, modeling one
instruction per two cycles. These entries reflect the targeted checks below;
they supersede the earlier conservative A320 three-cycle occupancy.

A520 `dup Vd.4s, Wn`, `mov Vd.s[0], Wn`, and GPR-to-vector FMOV can use
either abstract VEC resource, allowing two instructions per cycle.
Vector-to-GPR FMOV (`Xd,Dn` and `Wd,Sn`) and uncharacterized
DUP/insertion variants still conservatively occupy both resources to enforce
one transfer per cycle. This can overconstrain mixed vector workloads; it is not
a claim that hardware uses both physical pipes. New A320 memory entries
reserve both scalar memory resources to represent its single LSU. A520 W-pair
loads use the scalar load/store resource alternatives. Existing scalar/vector
memory-resource pools are not fully unified; cross-pool contention remains an
approximation. Existing A520 vector-memory hazard rules are retained.

Store data has no register result. The new store entries use a one-cycle
base-update convention, not a claim about memory visibility/completion. Lane
LD2 conservatively uses its vector-data latency for base dependencies too.

The formerly provisional A320 `fmov Xd,Dn` three-cycle latency is now supported
for the checked arithmetic consumers. Its vector-return path takes four cycles;
see the operand-specific rules below. Untested consumers remain approximations.

## Operand-specific timing refinements

Targeted dependency-chain and independent-stream checks give the following
model refinements. These are not silicon measurements or a complete
characterization of arbitrary producer/consumer pairs. Changes are restricted
to the listed forms; untested arrangements retain their previous entries.

| Form / dependency | A320 latency | A520 latency | A320 / A520 independent instructions per cycle |
| --- | ---: | ---: | ---: |
| Integer MLA/MLS `.4s`, same-opcode accumulator-only chain | 2 | 2 | 1 / 2 |
| Integer MLA/MLS `.4s`, result also feeds a multiplicand | 4 | 4 | 1 / 2 |
| AND/EOR `.16b` | 3 | 3 | 1 / 2 |
| FADD/FMUL `.4s` | 4 | 4 | 1 / 2 |
| Two-table TBL `.8b`/`.16b`, index or first-table chain | 5 | 8 | 0.5 / 0.4 |
| Two-table TBL `.8b`/`.16b`, second-table-only chain | 4 | 4 | 0.5 / 0.4 |

FADD/FMUL `.4s` gain previously missing A320 model entries. ADD/SUB `.4s`,
vector MUL `.4s`, and accumulator-chain FMLA `.4s` already matched the checks
and are unchanged. The integer MAC bypass does **not** apply to FP subclasses,
lane/widening forms, mixed MLA/MLS chains, or a result also used as a multiplicand.
TBL's shorter path applies only to same-arrangement two-table TBL pairs whose
result feeds exclusively the second table operand; an additional index or
first-table dependency keeps the general latency. Checks used in-range indices
(index 17 for the second-table chain); other index patterns remain unverified.
Using these isolated-stream results for mixed-stream scheduling remains a model
assumption, not a measured resource-contention guarantee.

For GPR/vector transfers, independent-stream rates are:

| Form | A320 instructions/cycle | A520 instructions/cycle |
| --- | ---: | ---: |
| `fmov Xd, Dn` | 1 | 1 |
| `fmov Dd, Xn` | 1 | 2 |
| `dup Vd.4s, Wn` | 1 | 2 |
| `mov Vd.s[0], Wn` | 1 | 2 |

The DUP/insert resource changes implement these rates without changing their
three-cycle latency entries. Both FMOV directions are now supported, with
three-cycle default latency and the exceptions below. The W/S forms use the
same directional throughput entries from SWOG section 3.13; independent-stream
throughput checks were performed for X/D, not W/S. A520 `fmov Wd,Sn` therefore
now uses the one-transfer/cycle resource model rather than its old two/cycle entry.

### FMOV dependency paths

Consumer-specific checks distinguish these paths in cycles:

| Producer -> dependent consumer | A320 | A520 |
| --- | ---: | ---: |
| `fmov Dd,Xn` -> `fmov Xd,Dn`, vector ADD `.2d`, scalar FADD D | 3 | 3 |
| `fmov Xd,Dn` -> scalar ADD/ADDS immediate or MUL X | 3 | 3 |
| `fmov Xd,Dn` -> `fmov Dd,Xn` | 4 | 4 |
| ADD/ADDS X immediate -> `fmov Dd,Xn` | 3 | 5 |
| MUL X -> `fmov Dd,Xn` | 5 | 5 |
| `fmov Sd,Wn` -> `fmov Wd,Sn` | 3 | 3 |
| `fmov Wd,Sn` -> ADD W immediate | 3 | 3 |
| `fmov Wd,Sn` -> `fmov Sd,Wn` | 4 | 4 |
| ADD W immediate -> `fmov Sd,Wn` | 3 | 5 |

These replace the earlier unresolved FMOV paths, including the old one-cycle
`fmov Wd,Sn` latency. The direct round trip is **3 + 4 = 7 cycles**, not two
identical transfer latencies. Adding scalar ADD gives 9 cycles on A320 and 11
on A520; inserting vector ADD instead gives 10 on both. Scalar FADD gives 11
on both, and inserting both vector and scalar ADD gives 12/14. These are steady
dependency-cycle periods, not complete function timings.

The rules check the producer's result index and the matching consumer register.
ADDS flag dependencies retain their ordinary latency. Only same-width transfer
pairs and the listed arithmetic forms are specialized: no extension is made to
mixed widths, high-lane FMOV, register/shifted ADD, W-form MUL, or other transfers.
The three-cycle baseline for other consumers remains an approximation. No
individual latency is inferred by halving a round trip or subtracting an
uncalibrated helper. The checks cover dependency paths rather than claiming a
universal latency for every use of the instruction.

To schedule the complete checked chains, the architecture adds simple JSON
definitions for `fmov Sd,Wn` and scalar `fadd Dd,Da,Db`. Target coverage also adds
ADD W immediate, ADDS X immediate, and MUL X. Ordinary timing/resource entries
come from the CPU's SWOG: ADD/ADDS latency 1, MUL X latency 4 and MAC occupancy 2,
scalar FADD latency 4 and throughput 1/cycle on A320 or 2/cycle on A520.
These are distinct from the measured consumer-specific exceptions. The existing
conservative read/write operand model for `fmov Dd,Xn` is retained, including its
force-output callback variant; high-lane FMOV support is not added by this update.

### Data still needed

- Other FMOV producer/consumer combinations, mixed widths, high-lane and
  half-precision forms, W/S independent throughput checks, and UMOV paths.
- Mixed MLA/MLS chains, integer lane/widening accumulates, and other vector
  widths; the accumulator bypass is currently limited to `.4s` same-opcode pairs.
- Other logical opcodes and 64-bit arrangements; other DUP arrangements and
  insertion lane indices.
- TBL with other table sizes, mixed-width chains, other producers/consumers,
  and different or out-of-range index values.
- Mixed-stream execution-resource contention, load/store contention and
  base-update dependencies; homogeneous throughput does not determine these.
- A520 2x64 datapath characterization before adding a separate configuration.

## Validation

```sh
venv/bin/python -m unittest discover -s tests/unit -v
venv/bin/python test.py --tests instructions_a55,instructions_m55 --dry-run --silent
```

`test_armv9_models.py` covers model lookups, both vector widths, CRC resources,
memory classification, hazard predicates, lane/flag dependencies, real optimizer
runs, assembly acceptance, and Unicorn execution of lane LD2. These are software
regressions, not hardware timing measurements. `test_armv9_timing.py` additionally
checks operand-sensitive bypasses and exclusions, lookup disjointness, scoped
FP support, independent-stream schedules, register renaming, and software-pipeline
recurrences. It verifies all nine FMOV closed chains above, including flags and
width exclusions. The JSON migration regression retains parser/A55 observations;
intentional A520 coverage changes and MLA/MLS accumulator timings are checked
against their updated contracts rather than the old timing snapshot.
