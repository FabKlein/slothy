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

data_ptr      .req x0
twiddle_ptr   .req x1
modulus_ptr   .req x2
out_ptr      .req x3

z1ptr      .req x0
z2ptr      .req x1
xptr       .req x2
yptr       .req x3
N          .req w4

// ---- Coefficient aliases (incoming) ----
b0         .req s0
b1         .req s1
b2         .req s2
a1         .req s3
a2         .req s4

// ---- Working FP regs ----
xval       .req s5
yval       .req s6
t1         .req s7
t2         .req s18

// ---- State in regs (kept across loop) ----
z1s        .req s16
z2s        .req s17




count .req x20
ldr s0, [twiddle_ptr], #4
ldr s1, [twiddle_ptr], #4
ldr s2, [twiddle_ptr], #4
ldr s3, [twiddle_ptr], #4

ldr s5, [twiddle_ptr], #4
ldr s16, [twiddle_ptr], #4
ldr s6, [twiddle_ptr], #4



mov count, #16
start:

    ldr     xval, [xptr], #4        // xval = *xptr++

    // y = b0*x + z1
    fmadd   yval, b0, xval, z1s

    // t1 = b1*x + z2
    fmadd   t1,   b1, xval, z2s

    // t2 = b2*x
    fmul    t2,   b2, xval

    // z1 = t1 - a1*y  =>  z1s = -(a1*y) + t1
    fnmadd  z1s,  a1, yval, t1

    // z2 = t2 - a2*y  =>  z2s = -(a2*y) + t2
    fnmadd  z2s,  a2, yval, t2

    str     yval, [yptr], #4        // *yptr++ = y


    subs count, count, #1
    cbnz count, start
