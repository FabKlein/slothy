qdata0   .req q8
qdata1   .req q9
qdata2   .req q10
qdata3   .req q11

qtwiddle .req q0
qmodulus .req q1

data0    .req v8
data1    .req v9
data2    .req v10
data3    .req v11

twiddle  .req v0
modulus  .req v1

tmp      .req v12

data0_ptr      .req x0
data1_ptr   .req x1
out_ptr   .req x2

.macro barmul out, in, twiddle, modulus
    mul      \out.8h,   \in.8h, \twiddle.h[0]
    sqrdmulh \in.8h,    \in.8h, \twiddle.h[1]
    mls      \out.8h,   \in.8h, \modulus.h[0]
.endm

.macro butterfly data0, data1, tmp, twiddle, modulus
    barmul \tmp, \data1, \twiddle, \modulus
    sub    \data1.8h, \data0.8h, \tmp.8h
    add    \data0.8h, \data0.8h, \tmp.8h
.endm

count .req x2
mov count, #16
start:


    ld1     {v0.4s}, [data0_ptr], #16
    ld1     {v1.4s}, [data1_ptr], #16

    fadd    v0.4s, v0.4s, v1.4s

    st1     {v0.4s}, [out_ptr], #16

    subs count, count, #1
    cbnz count, start
