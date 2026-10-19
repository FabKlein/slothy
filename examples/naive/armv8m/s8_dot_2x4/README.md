# Signed-byte 2x4 dot products on Cortex-M55

`s8_dot_2x4_cm55.s` preserves the supplied body and uses `subs`/`cmp`/`bhs`,
not LE/LETP. This frees `r14` (`lr`) for the eighth accumulator. VMLADAVA
requires an even-numbered scalar accumulator; the parser now enforces this
for both concrete operands and register allocation.

| Operand | Register |
| --- | --- |
| `ip_row_0`, `ip_row_1`, `col_base` | `r1`, `r3`, `r5` |
| unsigned byte count | `r7` |
| `a00`, `a10`, `a01`, `a11` | `r0`, `r2`, `r4`, `r6` |
| `a02`, `a12`, `a03`, `a13` | `r8`, `r10`, `r12`, `r14` |

Accumulators must be initialized by the caller; additions wrap modulo 2^32.
Each original iteration reads 16 bytes from each row and four 16-byte column
vectors, advancing the row pointers by 16 and the column pointer by 64.
Only full blocks are processed: this is **not** a tail-predicated loop.

These are register-contract snippets, **not AAPCS-callable functions**.
In particular, LR contains `a13`, not a return address: the caller must save
its return address elsewhere and preserve any ABI-required registers.
The optimized schedule clobbers `q0`–`q7` and NZCV. `r9`, `r11` and SP are
reserved; the byte counter is also excluded from SLOTHY's register allocation.
An inline-assembly integration must honor the even-register constraint, not
assume that unconstrained `"r"` operands will produce this allocation.

## Result

| Schedule | Model cycles per original 16-byte block |
| --- | ---: |
| Original instruction order | 20 |
| Software-pipelined, unroll x2 | 16 (32 per pair) |

Both runs returned OPTIMAL in this model. The pipelined solve took 0.98 seconds
with register renaming enabled, 26 early instructions and no spills. It has a
26-instruction preamble, 28-instruction kernel and two-instruction postamble.
This is a **20% reduction in modeled body cycles**, not a hardware speedup
measurement. Estimates exclude scalar loop control, entry checks,
preamble/postamble, remainder handling and memory penalties.

VMLADAVA uses the model's F/multiply unit with a two-cycle issue interval
and conservative three-cycle scalar-result latency, based on table 3-16 of
the [Cortex-M55 Software Optimization Guide](https://documentation-service.arm.com/static/63ac5ce1396e6135830ba9fe).
The existing M55 model is approximate, including its treatment of hazards.

## Saved output and count handling

[Optimized assembly](../../../opt/armv8m/s8_dot_2x4/s8_dot_2x4_cm55_swpipe_u2.s)
uses the pipelined pair loop for counts >=64. Smaller inputs use the original
body, and an odd remaining full block is handled after the pipeline drains.
For any unsigned input count, it processes `floor(count / 16)` blocks and
returns `count % 16` in `r7`. Counts below 16 execute no vector loads.
The naive do/while snippet requires an initial count >=16.

The current M55 loop extractor recognizes only LE/LETP. The driver therefore
uses SLOTHY's core scheduling API on two copies of the body, then explicitly
generates the scalar loop, counter adjustment and cleanup path. It does not
modify the generic loop parser or silently substitute a low-overhead loop.

From the repository root:

```sh
PYTHONPATH=. venv/bin/python examples/naive/armv8m/s8_dot_2x4/optimize.py \
  --timeout 600 --output /tmp/s8_dot_2x4_cm55_swpipe_u2.s

clang-19 --target=arm-none-eabi -mcpu=cortex-m55 -mfloat-abi=hard -mthumb \
  -c /tmp/s8_dot_2x4_cm55_swpipe_u2.s -o /tmp/s8_dot_2x4_cm55_swpipe_u2.o
```

## Validation

SLOTHY's dataflow self-check passes, and Clang accepts both source and output.
An independent instruction-level Python semantic model checks the saved output
against the mathematical dot products for 510 randomized count/seed cases:
counts 0–160 plus boundaries through 513, including short/odd block counts and
remainders. It checks all scalar registers, accumulator overflow, pointer
advances, byte-count residue and exact bounds on every load.
This is **not hardware execution or an architectural MVE emulator**; target
correctness/performance measurements remain to be done.

```sh
venv/bin/python -m unittest discover -s tests/unit -v
```
