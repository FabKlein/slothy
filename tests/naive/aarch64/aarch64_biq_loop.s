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



count .req x2
ldr qtwiddle, [twiddle_ptr, #0]
ldr qmodulus, [modulus_ptr, #0]

mov count, #16
start:

ldp     s7, s8, [data_ptr], #8
fmadd   s16, s7, s0, s5
fmadd   s17, s7, s1, s6
fmul    s18, s7, s2
fmadd   s5, s16, s3, s17
fmadd   s6, s16, s4, s18
//str     s16, [out_ptr], #4

//ldr     s8, [data_ptr], #4
fmadd   s19, s8, s0, s5
fmadd   s17, s8, s1, s6
fmul    s18, s8, s2
fmadd   s5, s19, s3, s17
fmadd   s6, s19, s4, s18
stp     s16, s19, [out_ptr], #8

    subs count, count, #1
    cbnz count, start
