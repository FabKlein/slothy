

state_ptr   .req x3

in_ptr      .req x0
out_ptr     .req x1

count .req x2

b00   .req v20
b01   .req v21
b02   .req v22
a01   .req v23
a02   .req v24
b10   .req v25
b11   .req v26
b12   .req v27
a11   .req v28
a12   .req v29


mov count, #16


        ldr     q1, [state_ptr], #16
        ldr     q2, [state_ptr], #16
        ldr     q11, [state_ptr], #16
        ldr     q12, [state_ptr], #16

start:


	    ldr    q0, [in_ptr], #16
	    fmla   v1.4s, v0.4s,  b00.4s
	    str    q1, [out_ptr], #16
	    fmla   v2.4s, v0.4s, b01.4s
	    fmls   v2.4s, v1.4s, a01.4s
	    fmul   v3.4s, v0.4s, b02.4s
	    fmls   v3.4s, v1.4s, a02.4s


	    ldr    q0, [in_ptr], #16
	    fmla   v11.4s, v0.4s,  b10.4s
	    str    q11, [out_ptr], #16
	    fmla   v12.4s, v0.4s, b11.4s
	    fmls   v12.4s, v11.4s, a11.4s
	    fmul   v13.4s, v0.4s, b12.4s
	    fmls   v13.4s, v11.4s, a12.4s


	    ldr    q0, [in_ptr], #16
	    fmla   v2.4s, v0.4s, b00.4s
	    str    q2, [out_ptr], #16
	    fmla   v3.4s, v0.4s, b01.4s
	    fmls   v3.4s, v2.4s, a01.4s
	    fmul   v4.4s, v0.4s, b02.4s
	    fmls   v4.4s, v2.4s, a02.4s


	    ldr    q0, [in_ptr], #16
	    fmla   v12.4s, v0.4s, b10.4s
	    str    q12, [out_ptr], #16
	    fmla   v13.4s, v0.4s, b11.4s
	    fmls   v13.4s, v12.4s, a11.4s
	    fmul   v14.4s, v0.4s, b12.4s
	    fmls   v14.4s, v12.4s, a12.4s


	    ldr    q0, [in_ptr], #16
	    fmla   v3.4s, v0.4s, b00.4s
	    str    q3, [out_ptr], #16
	    fmla   v4.4s, v0.4s, b01.4s
	    fmls   v4.4s, v3.4s, a01.4s
	    fmul   v1.4s, v0.4s, b02.4s
	    fmls   v1.4s, v3.4s, a02.4s


	    ldr    q0, [in_ptr], #16
	    fmla   v13.4s, v0.4s, b10.4s
	    str    q13, [out_ptr], #16
	    fmla   v14.4s, v0.4s, b11.4s
	    fmls   v14.4s, v13.4s, a11.4s
	    fmul   v11.4s, v0.4s, b12.4s
	    fmls   v11.4s, v13.4s, a12.4s


	    ldr    q0, [in_ptr], #16
	    fmla   v4.4s, v0.4s, b00.4s
	    str    q4, [out_ptr], #16
	    fmla   v1.4s, v0.4s, b01.4s
	    fmls   v1.4s, v4.4s, a01.4s
	    fmul   v2.4s, v0.4s, b02.4s
	    fmls   v2.4s, v4.4s, a02.4s


	    ldr    q0, [in_ptr], #16
	    fmla   v14.4s, v0.4s, b10.4s
	    str    q14, [out_ptr], #16
	    fmla   v11.4s, v0.4s, b11.4s
	    fmls   v11.4s, v14.4s, a11.4s
	    fmul   v12.4s, v0.4s, b12.4s
	    fmls   v12.4s, v14.4s, a12.4s

    subs count, count, #1
    cbnz count, start


        mov     v18.16b, v1.16b
        mov     v18.16b, v2.16b
        mov     v19.16b, v11.16b
        mov     v20.16b, v12.16b
