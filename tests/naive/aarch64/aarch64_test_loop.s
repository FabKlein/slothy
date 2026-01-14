

data0_ptr      .req x0
data1_ptr   .req x1
out_ptr   .req x2



count .req x2
mov count, #16
start:


ldp     q0, q1, [data0_ptr], #32
ldp     q2, q3, [data1_ptr], #32
add    v0.4s, v0.4s, v2.4s
add    v1.4s, v1.4s, v3.4s
stp     q0, q1, [out_ptr], #32

    subs count, count, #1
    cbnz count, start
