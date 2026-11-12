# AArch64 vector store comparison

Two C routines clear the sign bit of FP32 bit patterns, using the same
software-pipelined instruction schedule. `vector_abs_st1()` uses
`st1 {vN.4s}, [dst], #16`; `vector_abs_str()` uses `str qN, [dst], #16`.
Loads, integer vector operations, registers, pointer increments, loop control
and instruction order are otherwise identical. Each repeated body contains
8 paired loads, 16 BICs, 16 stores and 2 loop-control instructions.

This synthetic tests whether younger vector operations can make progress
behind pending stores in this particular interleaved schedule. It is designed
to expose a potential STR advantage, not to guarantee one on every processor
or for every schedule. Measure both on the same Cortex-A520 core.

## Build and run

From this directory, cross-compile a static Linux executable:

```sh
/usr/bin/aarch64-linux-gnu-gcc -O3 -std=gnu11 -march=armv8-a \
  -Wall -Wextra -Werror -static \
  vector_abs_store_kernels.c vector_abs_store_bench.c \
  -o /tmp/vector_abs_store_bench
```

Copy the executable to the target. Pin it to an A520 CPU (CPU 0 is only an
example; choose the correct CPU on your system):

```sh
taskset -c 0 ./vector_abs_store_bench
taskset -c 0 ./vector_abs_store_bench 32 1000 21 32
```

Arguments are `blocks repetitions samples clock_mhz`, defaulting to
`32 1000 21 0`. A block contains 64 floats / 256 bytes; the default is
2048 floats / 8192 bytes per buffer. The optional fourth argument converts
nanoseconds to **estimated** cycles using the supplied fixed clock, e.g.
32 MHz. This is not a PMU reading and is invalid if the clock assumption is
wrong. No privileged counter access or kernel driver is required.

The Linux harness uses `CLOCK_MONOTONIC_RAW`, warms each routine before timing,
alternates ST1/STR and STR/ST1 run order, checks output and buffer guards outside
the timed region, and prints min/average/median/max time plus a paired median
ST1/STR time ratio. A ratio greater than one means STR was faster.
Every invocation receives the original pointers and count. It does not let
post-incremented pointers drift across repetitions.

Prefer an idle pinned CPU and a fixed CPU clock. Increase repetitions if batches
are too short or results fluctuate. Start with the default warmed, small working
set; larger buffers can hide scheduling differences behind cache or memory
bandwidth. Repeat the whole command and inspect the distribution. The benchmark
does not subtract an empty loop. Timings include calls, ABI saves/restores,
pipeline preload/drain, loop control and a store-completion barrier per batch.
They are not steady-state body-only cycle counts.

## Routine contract and inspection

- Both buffers contain at least `blocks * 64` `uint32_t` words and do not overlap.
  Each word is an FP32 **bit pattern**; the exact result is `src[i] & 0x7fffffff`,
  including NaNs and signed zeros. There is no floating-point conversion.
- `blocks >= 2`. For smaller values the routines return without accessing data.
  There is no tail handling. Counts are blocks, not bytes or floats.
- Each routine initializes its own vector state, advances only local copies
  of pointers/count, and declares all register, flag and memory clobbers.
  The compiler handles ABI-required preservation. They are callable C functions,
  not standalone assembly fragments with a custom register contract.
- The harness uses disjoint page-aligned buffers and identical addresses for
  both variants. Kernels require only normal `uint32_t` alignment.
- Both hot loops start at offset 60 modulo 64. Padding is skipped by a branch;
  it is not timed as a sequence of NOPs. Instruction alignment is deliberately
  fixed to keep fetch effects comparable between the two variants.

Inspect the linked binary you actually deploy:

```sh
aarch64-linux-gnu-objdump -d --disassemble=vector_abs_st1 /tmp/vector_abs_store_bench
aarch64-linux-gnu-objdump -d --disassemble=vector_abs_str /tmp/vector_abs_store_bench
```

The kernel source/header can also be reused with a platform-specific timer
without the Linux harness. Functional emulation cannot establish a real CPU
speedup; only measurements on the target can do that.
