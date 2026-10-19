# Six-accumulator FP16 MAC loop for Cortex-M55

`fp16_mac_6acc_cm55.s` preserves the supplied inline assembly's instruction
order and converts GCC operands to concrete registers:

| Inline operand | Register |
| --- | --- |
| `%[x]`, `%[w]` | `r0`, `r1` |
| `%[xs]`, `%[ws]` | `r2`, `r3` |
| `%[count]` | `r12` |
| `%q[a0]` through `%q[a5]` | `q1` through `q6` |

The scratch registers remain `q0`, `q7`, and `r4` through `r11`; `lr` is the
low-overhead loop counter. `start` replaces the numeric label `1`.

This is a register-contract snippet, not an AAPCS-callable function. The caller
must initialize the six accumulators, supply valid buffers and byte strides,
and supply a positive count. Preserve any registers required by the surrounding
calling convention when integrating it. Each iteration advances `x` by two
bytes and `w` by 16 bytes, as in the original. All strided loads must be valid.

## Optimization

The Arm_v81M parser and Cortex-M55 model support the scalar `ldrh` and
vector-by-scalar `vfma.f16` forms used here. Start with this command from the
repository root (ordinary loop scheduling, without software pipelining):

```sh
source venv/bin/activate
./slothy-cli Arm_v81M Arm_Cortex_M55 \
  examples/naive/armv8m/fp16_mac_6acc/fp16_mac_6acc_cm55.s \
  -l start \
  -c inputs_are_outputs=True \
  -c selftest=False \
  -c variable_size=True \
  -c constraints.allow_renaming=False \
  -c timeout=20 \
  -c constraints.stalls_first_attempt=64 \
  -o fp16_mac_6acc_cm55_opt.s
```

`selftest=False` disables emulator testing; validate numerical results on the
target after optimization. Concrete input/output registers preserve this
snippet's boundary register contract.

This starting configuration permits instruction reordering while keeping the
register allocation fixed to reduce solver complexity. The timeout applies to
each solver invocation. Removing `constraints.allow_renaming=False` permits
register renaming but may require more solver time.

A checked output is saved in
[`examples/opt/armv8m/fp16_mac_6acc/fp16_mac_6acc_cm55_opt.s`](../../../opt/armv8m/fp16_mac_6acc/fp16_mac_6acc_cm55_opt.s).
The verification run found a feasible 113-cycle schedule within 20 seconds;
this is a model estimate, not a hardware measurement or a proven optimum.

The new scheduling entries follow Arm's
[Cortex-M55 Software Optimization Guide](https://documentation-service.arm.com/static/63ac5ce1396e6135830ba9fe),
tables 3-9/3-10 and 3-18: `ldrh` has latency 2 and issue interval 1;
vector-by-scalar `vfma` has latency 2 and issue interval 2 on the F pipeline.
The model remains approximate; measure performance on hardware.

## Software-pipelined variant

The following run enables inter-iteration scheduling, keeping the existing
register assignments and an unroll factor of one:

```sh
./slothy-cli Arm_v81M Arm_Cortex_M55 \
  examples/naive/armv8m/fp16_mac_6acc/fp16_mac_6acc_cm55.s \
  -l start \
  -c inputs_are_outputs=True \
  -c selftest=False \
  -c timeout=30 \
  -c variable_size=True \
  -c constraints.allow_renaming=False \
  -c constraints.stalls_first_attempt=64 \
  -c sw_pipelining.enabled=True \
  -c sw_pipelining.unroll=1 \
  -c sw_pipelining.minimize_overlapping=False \
  -c sw_pipelining.optimize_preamble=False \
  -c sw_pipelining.optimize_postamble=False \
  -o fp16_mac_6acc_cm55_swpipe.s
```

The saved [pipelined output](../../../opt/armv8m/fp16_mac_6acc/fp16_mac_6acc_cm55_swpipe.s)
has a feasible 111-cycle steady-state kernel, compared with 113 cycles for the
non-pipelined schedule and 125 for the original order. None of these are
hardware measurements. The pipelined estimate excludes the added preamble and
postamble, so it does not establish a speedup for short runs.

Five instructions execute early. One iteration is moved out of the kernel,
and the generated code subtracts one from `lr`. **This variant requires an
input count of at least two.** Use the non-pipelined loop for count one; no
small-count fallback is emitted by this command. SLOTHY's dataflow self-check
passes and Clang accepts the generated assembly; target execution remains to
be validated.

To assemble the input or optimized output with Clang:

```sh
clang --target=arm-none-eabi -mcpu=cortex-m55 -mfloat-abi=hard -mthumb \
  -c examples/naive/armv8m/fp16_mac_6acc/fp16_mac_6acc_cm55.s \
  -o /tmp/fp16_mac_6acc_cm55.o
```
