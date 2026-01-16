

state_ptr   .req x3

in_ptr   .req x0
out_ptr      .req x1

count .req x2

b0   .req v17
b1   .req v16
b2  .req v7


mov count, #16


        ldr     q1, [state_ptr], #16
        ldr     q2, [state_ptr], #16

start:
        ldr     q0, [in_ptr], #16
        fmla    v1.4s, v0.4s, b0.4s
        str     q1, [out_ptr], #16
        fmla    v2.4s, v0.4s, b1.4s
        fmls    v2.4s, v1.4s, v6.4s
        fmul    v3.4s, v0.4s, b2.4s
        fmls    v3.4s, v1.4s, v5.4s
        ldr     q0, [in_ptr], #16
        fmla    v2.4s, v0.4s, b0.4s
        str     q2, [out_ptr], #16
        fmla    v3.4s, v0.4s, b1.4s
        fmls    v3.4s, v2.4s, v6.4s
        fmul    v4.4s, v0.4s, b2.4s
        fmls    v4.4s, v2.4s, v5.4s
        ldr     q0, [in_ptr], #16
        fmla    v3.4s, v0.4s, b0.4s
        str     q3, [out_ptr], #16
        fmla    v4.4s, v0.4s, b1.4s
        fmls    v4.4s, v3.4s, v6.4s
        fmul    v1.4s, v0.4s, b2.4s
        fmls    v1.4s, v3.4s, v5.4s
        ldr     q0, [in_ptr], #16
        fmla    v4.4s, v0.4s, b0.4s
        str     q4, [out_ptr], #16
        fmla    v1.4s, v0.4s, b1.4s
        fmls    v1.4s, v4.4s, v6.4s
        fmul    v2.4s, v0.4s, b2.4s
        fmls    v2.4s, v4.4s, v5.4s
    subs count, count, #1
    cbnz count, start


        mov     v19.16b, v1.16b
        mov     v18.16b, v2.16b
