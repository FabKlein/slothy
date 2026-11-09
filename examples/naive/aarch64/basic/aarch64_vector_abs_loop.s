// x0: input, x2: output (512 bytes each; disjoint for software pipelining).
// Keep the counter separate from the output pointer.
data0_ptr .req x0
out_ptr .req x2
count .req x3

mov count, #16
start:
    ldp q0, q1, [data0_ptr], #32
    bic v0.4s, #0x80, lsl #24
    bic v1.4s, #0x80, lsl #24
    st1 {v0.4s}, [out_ptr], #16
    st1 {v1.4s}, [out_ptr], #16
    subs count, count, #1
    cbnz count, start
