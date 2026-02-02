

state_ptr   .req x3

in_ptr      .req x0
out_ptr     .req x1

count .req x2


Vout0 .req v26
Vout1 .req v24


z01 .req v22
z02 .req v25

b00 .req v18
b01 .req v7
b02 .req v6
a01 .req v5
a02 .req v21


mov count, #16


        ldp     q1, q0, [state_ptr, #160]
        ldp     q18, q19, [state_ptr, #192]
        ldp     q20, q21, [state_ptr, #64]
        ldp     q22, q23, [state_ptr, #224]
        ldp     q24, q25, [state_ptr, #96]
        ldp     q3, q2, [state_ptr, #128]
        ldp     q5, q4, [state_ptr, #32]
        ldp     q7, q6, [state_ptr]

start:
        ld1r    { v16.4s }, [in_ptr], #4
        ext     v17.16b, v16.16b, Vout0.16b, #12
        fmla    z01.4s, b00.4s, v17.4s
        fmla    z02.4s, b01.4s, v17.4s
        fmul    v3.4s, b02.4s, v17.4s
        fmls    z02.4s, a01.4s, z01.4s
        fmls    v3.4s, a02.4s, z01.4s
        st1     { z01.s }[3], [out_ptr], #4

        ld1r    { v16.4s }, [in_ptr], #4
        ext     v17.16b, v16.16b, z01.16b, #12
        fmla    z02.4s, b00.4s, v17.4s
        fmla    v3.4s, b01.4s, v17.4s
        fmul    Vout0.4s, b02.4s, v17.4s
        fmls    v3.4s, a01.4s, z02.4s
        fmls    Vout0.4s, a02.4s, z02.4s
        st1     { z02.s }[3], [out_ptr], #4

        ld1r    { v16.4s }, [in_ptr], #4
        ext     v17.16b, v16.16b, z02.16b, #12
        fmla    v3.4s, b00.4s, v17.4s
        fmla    Vout0.4s, b01.4s, v17.4s
        fmul    z01.4s, b02.4s, v17.4s
        fmls    Vout0.4s, a01.4s, v3.4s
        fmls    z01.4s, a02.4s, v3.4s
        st1     { v3.s }[3], [out_ptr], #4


        ld1r    { v16.4s }, [in_ptr], #4
        ext     v17.16b, v16.16b, v3.16b, #12
        fmla    Vout0.4s, b00.4s, v17.4s
        fmla    z01.4s, b01.4s, v17.4s
        fmul    z02.4s, b02.4s, v17.4s
        fmls    z01.4s, a01.4s, Vout0.4s
        fmls    z02.4s, a02.4s, Vout0.4s
        st1     { Vout0.s }[3], [out_ptr], #4


    subs count, count, #1
    cbnz count, start



        str     q25, [state_ptr], #16
        str     q23, [state_ptr], #16
        str     q21, [state_ptr], #16
        str     q24, [state_ptr], #16
        str     q19, [state_ptr], #16
        str     q22, [state_ptr], #16
