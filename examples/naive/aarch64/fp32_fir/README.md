# FP32 sliding-window loop for Cortex-A520

`fp32_fir_ca520.s` converts the supplied GCC inline assembly without changing
instruction order. Operands `s`, `y`, and `tiles` map to `x0`, `x1`, and `x2`.
The caller supplies a positive tile count and coefficients in `v24` through
`v31`. This is a register-contract snippet, not an AAPCS-callable function.

Each iteration produces eight four-lane FP32 vectors (32 samples, 128 bytes),
advances both pointers by 128 bytes, and reads source bytes 0 through 251.
The surrounding caller must provide those buffers and preserve any registers
required by its calling convention. Ordering annotations keep all loads before
the stores and retain store order, including when source and destination alias.
Software pipelining is disabled except in the explicit pipelining evaluation below.

## Paired-load variant

`fp32_fir_ca520_ldp.s` preserves the FP operation order and memory footprint,
replacing 60 `ldur` instructions with 28 `ldp` and four final `ldr` instructions.
A Q-register pair reads addresses 16 bytes apart: the original loads at offsets
0 and 4 cannot be paired together. Instead, the first pair is `q16, q20`
(offsets 0 and 16), followed by `q17, q21`, `q18, q22`, and `q19, q23`.

Three extra scratch registers, `x3`–`x5`, are initialized **before** `start`
to source +4, +8, and +12. Execute that setup once when entering the snippet;
the loop backedge targets `start`. Each of the four input streams uses seven
post-indexed `ldp` instructions advancing by 32 bytes, then one post-indexed
`ldr` adjusting by -96 bytes: net advancement is 128 bytes per tile.
The final four loads remain single loads to avoid reading beyond byte 251.
Four post-indexed `stp` instructions advance the output pointer by 32 bytes
each. Neither explicit `add ..., #128` remains in the loop.

The body has 292 instructions, excluding `subs`/`b.ne` and the three setup
instructions. This is an instruction-count reduction, not a measured speedup;
the cycle estimates below include both load variants and their reordered schedules.
The existing parser and Cortex-A520 model already support these load/store forms.
Execution regression tests compare the paired-load variant against the original
for the same 25 cases described below, including overlapping buffers.

## Results

| Schedule | Estimated cycles per tile | Cycles per output sample |
| --- | ---: | ---: |
| Original order | 278 | 8.6875 |
| Reordered, fixed registers | 215 | 6.71875 |
| Original `ldur`, software-pipelined, disjoint buffers only | 198 | 6.1875 |
| Paired loads, original FP order | 269 | 8.40625 |
| Paired loads, reordered, fixed registers | 231 | 7.21875 |
| Paired loads, software-pipelined, disjoint buffers only | 214 | 6.6875 |

Reordering the original `ldur` version gives a 22.7% reduction in model cycles
(approximately 1.29x throughput). Reordering the paired-load version gives a
14.1% reduction (269 to 231 cycles), but remains 16 cycles slower than the
optimized `ldur` version. Fewer instructions do not necessarily mean fewer cycles.
All six runs returned OPTIMAL within the current model and their constraints; this is
not a hardware performance guarantee or a claim about all possible rewrites.
The original `ldur` body contains 322 instructions: 60 `ldur`, 8 `fmul`, 248 `fmla`,
4 `stp`, and 2 pointer increments. The trailing `subs` and `b.ne` are outside
the scheduled body, so their cost is not included in the estimates.

The estimates retain this checkout's experimental Cortex-A520 model, including
its existing load/load and load/store hazard constraints. FP lane operations
use its two alternative vector units (the 2x128-bit vector configuration),
latency 4, and a one-cycle issue interval per unit. `ldur q` uses the existing
vector-load model (latency 3). These base timings follow the
[Cortex-A520 Software Optimization Guide](https://documentation-service.arm.com/static/65fddf771bc22b03bca907cb),
sections 3.1, 3.14, and 3.17. L1 cache hits are assumed. Cache misses, unaligned
access penalties, branch effects, and contention with another core sharing
the vector unit are not fully captured. A 2x64-bit implementation needs a
different vector-throughput model.

## Commands

From the repository root, activate the virtual environment. Estimate the
original order with reordering and register renaming disabled:

```sh
source venv/bin/activate
./slothy-cli Arm_AArch64 Arm_Cortex_A520 \
  examples/naive/aarch64/fp32_fir/fp32_fir_ca520.s \
  -l start \
  -c inputs_are_outputs=True \
  -c selftest=False \
  -c variable_size=True \
  -c constraints.allow_reordering=False \
  -c constraints.allow_renaming=False \
  -c constraints.stalls_first_attempt=120 \
  -c constraints.stalls_maximum_attempt=120 \
  -c timeout=60 \
  -o /tmp/fp32_fir_ca520_baseline.s
```

Optimize by enabling instruction reordering while retaining fixed registers:

```sh
./slothy-cli Arm_AArch64 Arm_Cortex_A520 \
  examples/naive/aarch64/fp32_fir/fp32_fir_ca520.s \
  -l start \
  -c inputs_are_outputs=True \
  -c selftest=False \
  -c variable_size=True \
  -c constraints.allow_renaming=False \
  -c constraints.stalls_first_attempt=128 \
  -c timeout=60 \
  -o /tmp/fp32_fir_ca520_opt.s
```

The baseline run took 57.74 solver seconds and the optimization 43.72 seconds.
Timeouts apply per solver invocation; slower machines may need a higher limit.
Saved assembly (without the large timeline comments) is in
[`examples/opt/aarch64/fp32_fir`](../../../opt/aarch64/fp32_fir).

### Paired-load evaluation and optimization

Optimize the paired-load loop with the same fixed-register, non-pipelined policy:

```sh
venv/bin/python ./slothy-cli Arm_AArch64 Arm_Cortex_A520 \
  examples/naive/aarch64/fp32_fir/fp32_fir_ca520_ldp.s \
  -l start \
  -c inputs_are_outputs=True \
  -c selftest=False \
  -c variable_size=True \
  -c constraints.allow_renaming=False \
  -c constraints.stalls_first_attempt=192 \
  -c constraints.stalls_maximum_attempt=192 \
  -c timeout=120 \
  -c visualize_reordering=False \
  -o /tmp/fp32_fir_ca520_ldp_opt.s
```

For the fixed-order cycle estimate, add
`-c constraints.allow_reordering=False` and change the output path to
`/tmp/fp32_fir_ca520_ldp_baseline.s`. The fixed-order run took 8.76 solver
seconds and optimization took 30.79 seconds. Both passed the dataflow self-check.
The estimates cover the 292-instruction body only, excluding the three pointer
setup instructions and the trailing `subs`/`b.ne`. Saved schedules are
`fp32_fir_ca520_ldp_baseline.s` and `fp32_fir_ca520_ldp_opt.s` in the optimized
examples directory linked above. Both are assembled and compared against the
original `ldur` source in the execution regression test (25 cases per variant).

## Software-pipelining evaluation

Software pipelining was evaluated on the paired-load source with fixed
registers, an unroll factor of one, and no late instructions. An unrestricted
early-instruction search with a 192-stall budget returned UNKNOWN after
120.64 solver seconds without finding a schedule. This is a timeout, not
proof that software pipelining is impossible.

A restricted retry allowing only the first 5% of instructions to move early
returned OPTIMAL after 88.36 solver seconds at **231 cycles per tile**. However,
it selected **zero early/late instructions**: there is no cross-iteration
overlap and no preamble/postamble work. Thus it does not improve the existing
231-cycle non-pipelined schedule. Optimality applies only to this restricted
search. The longer unrestricted early-instruction run below subsequently
found a better schedule. Register renaming and unrolling remain unevaluated.

```sh
venv/bin/python ./slothy-cli Arm_AArch64 Arm_Cortex_A520 \
  examples/naive/aarch64/fp32_fir/fp32_fir_ca520_ldp.s \
  -l start \
  -c inputs_are_outputs=True \
  -c selftest=False \
  -c variable_size=True \
  -c constraints.allow_renaming=False \
  -c constraints.stalls_first_attempt=90 \
  -c constraints.stalls_maximum_attempt=90 \
  -c timeout=120 \
  -c sw_pipelining.enabled=True \
  -c sw_pipelining.unroll=1 \
  -c sw_pipelining.max_pre=0.05 \
  -c sw_pipelining.minimize_overlapping=False \
  -c sw_pipelining.optimize_preamble=False \
  -c sw_pipelining.optimize_postamble=False \
  -c sw_pipelining.unknown_iteration_count=True \
  -c visualize_reordering=False \
  -o /tmp/fp32_fir_ca520_ldp_swpipe_eval.s
```

The saved evaluation output is
[`fp32_fir_ca520_ldp_swpipe_eval.s`](../../../opt/aarch64/fp32_fir/fp32_fir_ca520_ldp_swpipe_eval.s).
It retains a loop-entry zero-count guard from `unknown_iteration_count=True`;
positive counts, including one tile, are tested against the original.
It passes the dataflow self-check and the same 25 execution cases, including
overlapping buffers. A future schedule with actual cross-iteration loads must
recheck aliasing: the source annotations order loads/stores within an iteration,
but are not a general cross-iteration memory-dependence analysis.

For a longer, unrestricted early-instruction search, omit
`-c sw_pipelining.max_pre=0.05`, set both stall-budget options to `192`, and
increase `-c timeout=600` (10 minutes per solver invocation). Use a separate
output path, such as `/tmp/fp32_fir_ca520_ldp_swpipe.s`, to retain the restricted
evaluation result. Register renaming and unrolling remain disabled; late
instructions remain disabled by the default `sw_pipelining.allow_post=False`.

### Extended-timeout result: disjoint buffers only

The 600-second rerun completed in **479.07 solver seconds**, returning OPTIMAL
at **214 steady-state cycles per tile** (6.6875 cycles/sample). Its first
feasible solution appeared at 221.89 seconds, beyond the original timeout.
This is 7.36% fewer model cycles than the non-pipelined paired-load schedule's
231 cycles, and one cycle below the optimized `ldur` schedule's 215 cycles.
Optimality is limited to this model, fixed registers, unroll=1, and early-only
pipelining; it is not a hardware measurement or a global optimum over rewrites.

The saved [software-pipelined output](../../../opt/aarch64/fp32_fir/fp32_fir_ca520_ldp_swpipe.s)
has 281 early instructions, a 281-instruction preamble, a 292-instruction
steady-state kernel, and an 11-instruction postamble. Enter before the preamble
with a positive tile count. The generated code subtracts one from `x2` and
skips the kernel for one tile; larger counts execute the kernel `tiles - 1`
times. Zero tiles are **not supported**. The 214-cycle figure excludes the
preamble/postamble, pointer setup and loop control, so it does not establish
a whole-call speedup for short inputs.

**This variant requires disjoint source and destination buffers.** Execution
checks found differing output for destination offsets +4 and +128 with 2 or
5 tiles: next-iteration loads can precede current-iteration stores. The earlier
alias-preserving non-pipelined files remain unchanged. Do not replace those
with this schedule if buffers may overlap. The dataflow self-check passes,
but does not prove memory-alias equivalence across iterations.

The saved SWP assembly is assembled and execution-tested against the original
for 1, 2, 3, 5 and 8 tiles, with disjoint destination offsets -4096 and +8192
(10 cases). The test compares all buffer bytes, final pointers/count and
coefficient registers. Existing alias-safe variants retain overlap checks.

### Original LDUR software-pipelining result

The same early-only software-pipelining search on `fp32_fir_ca520.s` completed
in **346.22 solver seconds** (600-second timeout), returning OPTIMAL at
**198 steady-state cycles per tile**, or 6.1875 cycles per output sample.
This saves 17 cycles (7.91%) against the 215-cycle non-pipelined `ldur` schedule,
and 16 cycles (7.48%) against the 214-cycle pipelined `ldp` schedule.
These are model estimates with fixed registers, no unrolling and no late
instructions; setup/cleanup, loop control and memory penalties are excluded.

Saved output:
[`fp32_fir_ca520_swpipe.s`](../../../opt/aarch64/fp32_fir/fp32_fir_ca520_swpipe.s).
It has a 315-instruction preamble, 322-instruction kernel and 7-instruction
postamble. As with the paired-load variant, enter before the preamble with
`x2 >= 1`; one tile skips the kernel, while larger counts run the kernel
`tiles - 1` times. No extra scratch GPRs are introduced. Short-call performance
must include the preamble/postamble, not just the steady-state estimate.

**Use disjoint source and destination buffers only.** The assembly and SLOTHY
dataflow self-check pass, and execution matches the original for all 10
disjoint-buffer cases described above. Partial-overlap checks fail: offset
+4 differs for multiple tiles, and offset +128 differs even for one tile.
In particular, this generated preamble can store before all source loads have
finished; its retained memory annotations are not a guarantee of alias safety.
The original and non-pipelined files are unchanged.

Reproduce from the repository root:

```sh
venv/bin/python ./slothy-cli Arm_AArch64 Arm_Cortex_A520 \
  examples/naive/aarch64/fp32_fir/fp32_fir_ca520.s \
  -l start \
  -c inputs_are_outputs=True \
  -c selftest=False \
  -c variable_size=True \
  -c constraints.allow_renaming=False \
  -c constraints.stalls_first_attempt=192 \
  -c constraints.stalls_maximum_attempt=192 \
  -c timeout=600 \
  -c sw_pipelining.enabled=True \
  -c sw_pipelining.unroll=1 \
  -c sw_pipelining.minimize_overlapping=False \
  -c sw_pipelining.optimize_preamble=False \
  -c sw_pipelining.optimize_postamble=False \
  -c sw_pipelining.unknown_iteration_count=True \
  -c visualize_reordering=False \
  -o /tmp/fp32_fir_ca520_swpipe.s
```

## Support added and validation

The parser now supports explicit-offset `ldur q` with signed byte offsets,
and vector-by-element `fmul` and `fmla`. The Cortex-A520 model includes the FP
lane forms; `ldur q` inherits the existing vector-load entries. FP lane
arrangements and indices are checked, and LDUR offset fixups retain its
signed nine-bit range. Accumulator dependencies preserve the original FP
operation order for each result lane.

Fixed-order evaluation now expresses non-pipelined instruction order using
adjacent constraints instead of every instruction pair. These are equivalent
by transitivity and avoid quadratic redundant ordering constraints on long
blocks; software-pipelined ordering is unchanged.

All saved schedules passed SLOTHY's dataflow self-check. Original and optimized
assembly compile with Clang. A regression test compares their execution in
Unicorn for 1, 2, 3, 5 and 8 tiles, with destination offsets of -4096, 0, 4,
128 and 8192 bytes from the source (25 cases per alias-safe variant). The
actual SWP variants are each restricted to the 10 disjoint-buffer cases above.
It checks all buffer bytes, updated
pointers/count, and preserved coefficient registers with deterministic random
FP32 inputs. Hardware timing and broader numerical testing remain outstanding.

```sh
venv/bin/python -m unittest discover -s tests/unit -v
```

The execution test requires `clang-19` and `llvm-objcopy-19`; it is skipped if
they are unavailable. `selftest=False` in the commands disables SLOTHY's
automatic emulator test; the regression test supplies the snippet's register
and memory setup explicitly.
