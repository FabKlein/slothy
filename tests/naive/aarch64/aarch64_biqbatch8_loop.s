

state_ptr   .req x3

in_ptr      .req x0
out_ptr     .req in_ptr

count .req x2

b0   .req v17
b1   .req v16
b2   .req v7


mov count, #16


        ldr     q1, [state_ptr], #16
        ldr     q2, [state_ptr], #16

start:
         ld1r    { v16.4s }, [in_ptr], #4
        ext     v17.16b, v16.16b, v25.16b, #12
        fmla    v21.4s, v7.4s, v17.4s
        fmla    v24.4s, v6.4s, v17.4s
        fmul    v0.4s, v5.4s, v17.4s
        fmls    v24.4s, v4.4s, v21.4s
        fmls    v0.4s, v20.4s, v21.4s
        ext     v17.16b, v21.16b, v23.16b, #12
        fmla    v19.4s, v3.4s, v17.4s
        fmla    v22.4s, v2.4s, v17.4s
        fmul    v1.4s, v1.4s, v17.4s
        fmls    v22.4s, v0.4s, v19.4s
        fmls    v1.4s, v18.4s, v19.4s
        st1     { v19.s }[3], [out_ptr], #4
        ld1r    { v16.4s }, [in_ptr], #4
        ext     v17.16b, v16.16b, v21.16b, #12
        fmla    v24.4s, v7.4s, v17.4s
        fmla    v0.4s, v6.4s, v17.4s
        fmul    v25.4s, v5.4s, v17.4s
        fmls    v0.4s, v4.4s, v24.4s
        fmls    v25.4s, v20.4s, v24.4s
        ext     v17.16b, v24.16b, v19.16b, #12
        fmla    v22.4s, v3.4s, v17.4s
        fmla    v1.4s, v2.4s, v17.4s
        fmul    v23.4s, v1.4s, v17.4s
        fmls    v1.4s, v0.4s, v22.4s
        fmls    v23.4s, v18.4s, v22.4s
        st1     { v22.s }[3], [out_ptr], #4
        ld1r    { v16.4s }, [in_ptr], #4
        ext     v17.16b, v16.16b, v24.16b, #12
        fmla    v0.4s, v7.4s, v17.4s
        fmla    v25.4s, v6.4s, v17.4s
        fmul    v21.4s, v5.4s, v17.4s
        fmls    v25.4s, v4.4s, v0.4s
        fmls    v21.4s, v20.4s, v0.4s
        ext     v17.16b, v0.16b, v22.16b, #12
        fmla    v1.4s, v3.4s, v17.4s
        fmla    v23.4s, v2.4s, v17.4s
        fmul    v19.4s, v1.4s, v17.4s
        fmls    v23.4s, v0.4s, v1.4s
        fmls    v19.4s, v18.4s, v1.4s
        st1     { v1.s }[3], [out_ptr], #4
        ld1r    { v16.4s }, [in_ptr], #4
        ext     v17.16b, v16.16b, v0.16b, #12
        fmla    v25.4s, v7.4s, v17.4s
        fmla    v21.4s, v6.4s, v17.4s
        fmul    v24.4s, v5.4s, v17.4s
        fmls    v21.4s, v4.4s, v25.4s
        fmls    v24.4s, v20.4s, v25.4s
        ext     v17.16b, v25.16b, v1.16b, #12
        fmla    v23.4s, v3.4s, v17.4s
        fmla    v19.4s, v2.4s, v17.4s
        fmul    v22.4s, v1.4s, v17.4s
        fmls    v19.4s, v0.4s, v23.4s
        fmls    v22.4s, v18.4s, v23.4s
        st1     { v23.s }[3], [out_ptr], #4


    subs count, count, #1
    cbnz count, start


        mov     v19.16b, v1.16b
        mov     v18.16b, v2.16b
