// Original instruction order from the supplied GCC inline assembly.
// Register-contract snippet, not an AAPCS-callable function.
// x0 = s (source), x1 = y (destination), x2 = positive tile count.
// v24-v31 contain the 32 FP32 coefficients and remain unchanged.
// Scratch/output vectors: v0-v7 and v16-v23; NZCV is clobbered.
// Each tile writes 128 bytes and advances both pointers by 128 bytes.
// Source accesses extend through byte 251 relative to each tile's x0.
// Memory tags keep stores after all loads and preserve store order (including aliasing).
.text
.p2align 4
start:
    ldur q16, [x0, #0] // @slothy:before=fir_store0
    ldur q17, [x0, #4] // @slothy:before=fir_store0
    ldur q18, [x0, #8] // @slothy:before=fir_store0
    ldur q19, [x0, #12] // @slothy:before=fir_store0
    ldur q20, [x0, #16] // @slothy:before=fir_store0
    ldur q21, [x0, #20] // @slothy:before=fir_store0
    ldur q22, [x0, #24] // @slothy:before=fir_store0
    ldur q23, [x0, #28] // @slothy:before=fir_store0
    fmul v0.4s, v16.4s, v24.s[0]
    fmul v1.4s, v20.4s, v24.s[0]
    fmla v0.4s, v17.4s, v24.s[1]
    fmla v1.4s, v21.4s, v24.s[1]
    fmla v0.4s, v18.4s, v24.s[2]
    fmla v1.4s, v22.4s, v24.s[2]
    fmla v0.4s, v19.4s, v24.s[3]
    fmla v1.4s, v23.4s, v24.s[3]
    fmla v0.4s, v20.4s, v25.s[0]
    fmla v0.4s, v21.4s, v25.s[1]
    fmla v0.4s, v22.4s, v25.s[2]
    fmla v0.4s, v23.4s, v25.s[3]
    ldur q16, [x0, #32] // @slothy:before=fir_store0
    ldur q17, [x0, #36] // @slothy:before=fir_store0
    ldur q18, [x0, #40] // @slothy:before=fir_store0
    ldur q19, [x0, #44] // @slothy:before=fir_store0
    ldur q20, [x0, #48] // @slothy:before=fir_store0
    ldur q21, [x0, #52] // @slothy:before=fir_store0
    ldur q22, [x0, #56] // @slothy:before=fir_store0
    ldur q23, [x0, #60] // @slothy:before=fir_store0
    fmla v0.4s, v16.4s, v26.s[0]
    fmla v1.4s, v16.4s, v25.s[0]
    fmul v2.4s, v16.4s, v24.s[0]
    fmul v3.4s, v20.4s, v24.s[0]
    fmla v0.4s, v17.4s, v26.s[1]
    fmla v1.4s, v17.4s, v25.s[1]
    fmla v2.4s, v17.4s, v24.s[1]
    fmla v3.4s, v21.4s, v24.s[1]
    fmla v0.4s, v18.4s, v26.s[2]
    fmla v1.4s, v18.4s, v25.s[2]
    fmla v2.4s, v18.4s, v24.s[2]
    fmla v3.4s, v22.4s, v24.s[2]
    fmla v0.4s, v19.4s, v26.s[3]
    fmla v1.4s, v19.4s, v25.s[3]
    fmla v2.4s, v19.4s, v24.s[3]
    fmla v3.4s, v23.4s, v24.s[3]
    fmla v0.4s, v20.4s, v27.s[0]
    fmla v1.4s, v20.4s, v26.s[0]
    fmla v2.4s, v20.4s, v25.s[0]
    fmla v0.4s, v21.4s, v27.s[1]
    fmla v1.4s, v21.4s, v26.s[1]
    fmla v2.4s, v21.4s, v25.s[1]
    fmla v0.4s, v22.4s, v27.s[2]
    fmla v1.4s, v22.4s, v26.s[2]
    fmla v2.4s, v22.4s, v25.s[2]
    fmla v0.4s, v23.4s, v27.s[3]
    fmla v1.4s, v23.4s, v26.s[3]
    fmla v2.4s, v23.4s, v25.s[3]
    ldur q16, [x0, #64] // @slothy:before=fir_store0
    ldur q17, [x0, #68] // @slothy:before=fir_store0
    ldur q18, [x0, #72] // @slothy:before=fir_store0
    ldur q19, [x0, #76] // @slothy:before=fir_store0
    ldur q20, [x0, #80] // @slothy:before=fir_store0
    ldur q21, [x0, #84] // @slothy:before=fir_store0
    ldur q22, [x0, #88] // @slothy:before=fir_store0
    ldur q23, [x0, #92] // @slothy:before=fir_store0
    fmla v0.4s, v16.4s, v28.s[0]
    fmla v1.4s, v16.4s, v27.s[0]
    fmla v2.4s, v16.4s, v26.s[0]
    fmla v3.4s, v16.4s, v25.s[0]
    fmul v4.4s, v16.4s, v24.s[0]
    fmul v5.4s, v20.4s, v24.s[0]
    fmla v0.4s, v17.4s, v28.s[1]
    fmla v1.4s, v17.4s, v27.s[1]
    fmla v2.4s, v17.4s, v26.s[1]
    fmla v3.4s, v17.4s, v25.s[1]
    fmla v4.4s, v17.4s, v24.s[1]
    fmla v5.4s, v21.4s, v24.s[1]
    fmla v0.4s, v18.4s, v28.s[2]
    fmla v1.4s, v18.4s, v27.s[2]
    fmla v2.4s, v18.4s, v26.s[2]
    fmla v3.4s, v18.4s, v25.s[2]
    fmla v4.4s, v18.4s, v24.s[2]
    fmla v5.4s, v22.4s, v24.s[2]
    fmla v0.4s, v19.4s, v28.s[3]
    fmla v1.4s, v19.4s, v27.s[3]
    fmla v2.4s, v19.4s, v26.s[3]
    fmla v3.4s, v19.4s, v25.s[3]
    fmla v4.4s, v19.4s, v24.s[3]
    fmla v5.4s, v23.4s, v24.s[3]
    fmla v0.4s, v20.4s, v29.s[0]
    fmla v1.4s, v20.4s, v28.s[0]
    fmla v2.4s, v20.4s, v27.s[0]
    fmla v3.4s, v20.4s, v26.s[0]
    fmla v4.4s, v20.4s, v25.s[0]
    fmla v0.4s, v21.4s, v29.s[1]
    fmla v1.4s, v21.4s, v28.s[1]
    fmla v2.4s, v21.4s, v27.s[1]
    fmla v3.4s, v21.4s, v26.s[1]
    fmla v4.4s, v21.4s, v25.s[1]
    fmla v0.4s, v22.4s, v29.s[2]
    fmla v1.4s, v22.4s, v28.s[2]
    fmla v2.4s, v22.4s, v27.s[2]
    fmla v3.4s, v22.4s, v26.s[2]
    fmla v4.4s, v22.4s, v25.s[2]
    fmla v0.4s, v23.4s, v29.s[3]
    fmla v1.4s, v23.4s, v28.s[3]
    fmla v2.4s, v23.4s, v27.s[3]
    fmla v3.4s, v23.4s, v26.s[3]
    fmla v4.4s, v23.4s, v25.s[3]
    ldur q16, [x0, #96] // @slothy:before=fir_store0
    ldur q17, [x0, #100] // @slothy:before=fir_store0
    ldur q18, [x0, #104] // @slothy:before=fir_store0
    ldur q19, [x0, #108] // @slothy:before=fir_store0
    ldur q20, [x0, #112] // @slothy:before=fir_store0
    ldur q21, [x0, #116] // @slothy:before=fir_store0
    ldur q22, [x0, #120] // @slothy:before=fir_store0
    ldur q23, [x0, #124] // @slothy:before=fir_store0
    fmla v0.4s, v16.4s, v30.s[0]
    fmla v1.4s, v16.4s, v29.s[0]
    fmla v2.4s, v16.4s, v28.s[0]
    fmla v3.4s, v16.4s, v27.s[0]
    fmla v4.4s, v16.4s, v26.s[0]
    fmla v5.4s, v16.4s, v25.s[0]
    fmul v6.4s, v16.4s, v24.s[0]
    fmul v7.4s, v20.4s, v24.s[0]
    fmla v0.4s, v17.4s, v30.s[1]
    fmla v1.4s, v17.4s, v29.s[1]
    fmla v2.4s, v17.4s, v28.s[1]
    fmla v3.4s, v17.4s, v27.s[1]
    fmla v4.4s, v17.4s, v26.s[1]
    fmla v5.4s, v17.4s, v25.s[1]
    fmla v6.4s, v17.4s, v24.s[1]
    fmla v7.4s, v21.4s, v24.s[1]
    fmla v0.4s, v18.4s, v30.s[2]
    fmla v1.4s, v18.4s, v29.s[2]
    fmla v2.4s, v18.4s, v28.s[2]
    fmla v3.4s, v18.4s, v27.s[2]
    fmla v4.4s, v18.4s, v26.s[2]
    fmla v5.4s, v18.4s, v25.s[2]
    fmla v6.4s, v18.4s, v24.s[2]
    fmla v7.4s, v22.4s, v24.s[2]
    fmla v0.4s, v19.4s, v30.s[3]
    fmla v1.4s, v19.4s, v29.s[3]
    fmla v2.4s, v19.4s, v28.s[3]
    fmla v3.4s, v19.4s, v27.s[3]
    fmla v4.4s, v19.4s, v26.s[3]
    fmla v5.4s, v19.4s, v25.s[3]
    fmla v6.4s, v19.4s, v24.s[3]
    fmla v7.4s, v23.4s, v24.s[3]
    fmla v0.4s, v20.4s, v31.s[0]
    fmla v1.4s, v20.4s, v30.s[0]
    fmla v2.4s, v20.4s, v29.s[0]
    fmla v3.4s, v20.4s, v28.s[0]
    fmla v4.4s, v20.4s, v27.s[0]
    fmla v5.4s, v20.4s, v26.s[0]
    fmla v6.4s, v20.4s, v25.s[0]
    fmla v0.4s, v21.4s, v31.s[1]
    fmla v1.4s, v21.4s, v30.s[1]
    fmla v2.4s, v21.4s, v29.s[1]
    fmla v3.4s, v21.4s, v28.s[1]
    fmla v4.4s, v21.4s, v27.s[1]
    fmla v5.4s, v21.4s, v26.s[1]
    fmla v6.4s, v21.4s, v25.s[1]
    fmla v0.4s, v22.4s, v31.s[2]
    fmla v1.4s, v22.4s, v30.s[2]
    fmla v2.4s, v22.4s, v29.s[2]
    fmla v3.4s, v22.4s, v28.s[2]
    fmla v4.4s, v22.4s, v27.s[2]
    fmla v5.4s, v22.4s, v26.s[2]
    fmla v6.4s, v22.4s, v25.s[2]
    fmla v0.4s, v23.4s, v31.s[3]
    fmla v1.4s, v23.4s, v30.s[3]
    fmla v2.4s, v23.4s, v29.s[3]
    fmla v3.4s, v23.4s, v28.s[3]
    fmla v4.4s, v23.4s, v27.s[3]
    fmla v5.4s, v23.4s, v26.s[3]
    fmla v6.4s, v23.4s, v25.s[3]
    ldur q16, [x0, #128] // @slothy:before=fir_store0
    ldur q17, [x0, #132] // @slothy:before=fir_store0
    ldur q18, [x0, #136] // @slothy:before=fir_store0
    ldur q19, [x0, #140] // @slothy:before=fir_store0
    ldur q20, [x0, #144] // @slothy:before=fir_store0
    ldur q21, [x0, #148] // @slothy:before=fir_store0
    ldur q22, [x0, #152] // @slothy:before=fir_store0
    ldur q23, [x0, #156] // @slothy:before=fir_store0
    fmla v1.4s, v16.4s, v31.s[0]
    fmla v2.4s, v16.4s, v30.s[0]
    fmla v3.4s, v16.4s, v29.s[0]
    fmla v4.4s, v16.4s, v28.s[0]
    fmla v5.4s, v16.4s, v27.s[0]
    fmla v6.4s, v16.4s, v26.s[0]
    fmla v7.4s, v16.4s, v25.s[0]
    fmla v1.4s, v17.4s, v31.s[1]
    fmla v2.4s, v17.4s, v30.s[1]
    fmla v3.4s, v17.4s, v29.s[1]
    fmla v4.4s, v17.4s, v28.s[1]
    fmla v5.4s, v17.4s, v27.s[1]
    fmla v6.4s, v17.4s, v26.s[1]
    fmla v7.4s, v17.4s, v25.s[1]
    fmla v1.4s, v18.4s, v31.s[2]
    fmla v2.4s, v18.4s, v30.s[2]
    fmla v3.4s, v18.4s, v29.s[2]
    fmla v4.4s, v18.4s, v28.s[2]
    fmla v5.4s, v18.4s, v27.s[2]
    fmla v6.4s, v18.4s, v26.s[2]
    fmla v7.4s, v18.4s, v25.s[2]
    fmla v1.4s, v19.4s, v31.s[3]
    fmla v2.4s, v19.4s, v30.s[3]
    fmla v3.4s, v19.4s, v29.s[3]
    fmla v4.4s, v19.4s, v28.s[3]
    fmla v5.4s, v19.4s, v27.s[3]
    fmla v6.4s, v19.4s, v26.s[3]
    fmla v7.4s, v19.4s, v25.s[3]
    fmla v2.4s, v20.4s, v31.s[0]
    fmla v3.4s, v20.4s, v30.s[0]
    fmla v4.4s, v20.4s, v29.s[0]
    fmla v5.4s, v20.4s, v28.s[0]
    fmla v6.4s, v20.4s, v27.s[0]
    fmla v7.4s, v20.4s, v26.s[0]
    fmla v2.4s, v21.4s, v31.s[1]
    fmla v3.4s, v21.4s, v30.s[1]
    fmla v4.4s, v21.4s, v29.s[1]
    fmla v5.4s, v21.4s, v28.s[1]
    fmla v6.4s, v21.4s, v27.s[1]
    fmla v7.4s, v21.4s, v26.s[1]
    fmla v2.4s, v22.4s, v31.s[2]
    fmla v3.4s, v22.4s, v30.s[2]
    fmla v4.4s, v22.4s, v29.s[2]
    fmla v5.4s, v22.4s, v28.s[2]
    fmla v6.4s, v22.4s, v27.s[2]
    fmla v7.4s, v22.4s, v26.s[2]
    fmla v2.4s, v23.4s, v31.s[3]
    fmla v3.4s, v23.4s, v30.s[3]
    fmla v4.4s, v23.4s, v29.s[3]
    fmla v5.4s, v23.4s, v28.s[3]
    fmla v6.4s, v23.4s, v27.s[3]
    fmla v7.4s, v23.4s, v26.s[3]
    ldur q16, [x0, #160] // @slothy:before=fir_store0
    ldur q17, [x0, #164] // @slothy:before=fir_store0
    ldur q18, [x0, #168] // @slothy:before=fir_store0
    ldur q19, [x0, #172] // @slothy:before=fir_store0
    ldur q20, [x0, #176] // @slothy:before=fir_store0
    ldur q21, [x0, #180] // @slothy:before=fir_store0
    ldur q22, [x0, #184] // @slothy:before=fir_store0
    ldur q23, [x0, #188] // @slothy:before=fir_store0
    fmla v3.4s, v16.4s, v31.s[0]
    fmla v4.4s, v16.4s, v30.s[0]
    fmla v5.4s, v16.4s, v29.s[0]
    fmla v6.4s, v16.4s, v28.s[0]
    fmla v7.4s, v16.4s, v27.s[0]
    fmla v3.4s, v17.4s, v31.s[1]
    fmla v4.4s, v17.4s, v30.s[1]
    fmla v5.4s, v17.4s, v29.s[1]
    fmla v6.4s, v17.4s, v28.s[1]
    fmla v7.4s, v17.4s, v27.s[1]
    fmla v3.4s, v18.4s, v31.s[2]
    fmla v4.4s, v18.4s, v30.s[2]
    fmla v5.4s, v18.4s, v29.s[2]
    fmla v6.4s, v18.4s, v28.s[2]
    fmla v7.4s, v18.4s, v27.s[2]
    fmla v3.4s, v19.4s, v31.s[3]
    fmla v4.4s, v19.4s, v30.s[3]
    fmla v5.4s, v19.4s, v29.s[3]
    fmla v6.4s, v19.4s, v28.s[3]
    fmla v7.4s, v19.4s, v27.s[3]
    fmla v4.4s, v20.4s, v31.s[0]
    fmla v5.4s, v20.4s, v30.s[0]
    fmla v6.4s, v20.4s, v29.s[0]
    fmla v7.4s, v20.4s, v28.s[0]
    fmla v4.4s, v21.4s, v31.s[1]
    fmla v5.4s, v21.4s, v30.s[1]
    fmla v6.4s, v21.4s, v29.s[1]
    fmla v7.4s, v21.4s, v28.s[1]
    fmla v4.4s, v22.4s, v31.s[2]
    fmla v5.4s, v22.4s, v30.s[2]
    fmla v6.4s, v22.4s, v29.s[2]
    fmla v7.4s, v22.4s, v28.s[2]
    fmla v4.4s, v23.4s, v31.s[3]
    fmla v5.4s, v23.4s, v30.s[3]
    fmla v6.4s, v23.4s, v29.s[3]
    fmla v7.4s, v23.4s, v28.s[3]
    ldur q16, [x0, #192] // @slothy:before=fir_store0
    ldur q17, [x0, #196] // @slothy:before=fir_store0
    ldur q18, [x0, #200] // @slothy:before=fir_store0
    ldur q19, [x0, #204] // @slothy:before=fir_store0
    ldur q20, [x0, #208] // @slothy:before=fir_store0
    ldur q21, [x0, #212] // @slothy:before=fir_store0
    ldur q22, [x0, #216] // @slothy:before=fir_store0
    ldur q23, [x0, #220] // @slothy:before=fir_store0
    fmla v5.4s, v16.4s, v31.s[0]
    fmla v6.4s, v16.4s, v30.s[0]
    fmla v7.4s, v16.4s, v29.s[0]
    fmla v5.4s, v17.4s, v31.s[1]
    fmla v6.4s, v17.4s, v30.s[1]
    fmla v7.4s, v17.4s, v29.s[1]
    fmla v5.4s, v18.4s, v31.s[2]
    fmla v6.4s, v18.4s, v30.s[2]
    fmla v7.4s, v18.4s, v29.s[2]
    fmla v5.4s, v19.4s, v31.s[3]
    fmla v6.4s, v19.4s, v30.s[3]
    fmla v7.4s, v19.4s, v29.s[3]
    fmla v6.4s, v20.4s, v31.s[0]
    fmla v7.4s, v20.4s, v30.s[0]
    fmla v6.4s, v21.4s, v31.s[1]
    fmla v7.4s, v21.4s, v30.s[1]
    fmla v6.4s, v22.4s, v31.s[2]
    fmla v7.4s, v22.4s, v30.s[2]
    fmla v6.4s, v23.4s, v31.s[3]
    fmla v7.4s, v23.4s, v30.s[3]
    ldur q16, [x0, #224] // @slothy:before=fir_store0
    ldur q17, [x0, #228] // @slothy:before=fir_store0
    ldur q18, [x0, #232] // @slothy:before=fir_store0
    ldur q19, [x0, #236] // @slothy:before=fir_store0
    fmla v7.4s, v16.4s, v31.s[0]
    fmla v7.4s, v17.4s, v31.s[1]
    fmla v7.4s, v18.4s, v31.s[2]
    fmla v7.4s, v19.4s, v31.s[3]
    stp q0, q1, [x1, #0] // @slothy:id=fir_store0
    stp q2, q3, [x1, #32] // @slothy:id=fir_store1 @slothy:after=fir_store0
    stp q4, q5, [x1, #64] // @slothy:id=fir_store2 @slothy:after=fir_store1
    stp q6, q7, [x1, #96] // @slothy:id=fir_store3 @slothy:after=fir_store2
    add x0, x0, #128
    add x1, x1, #128
    subs x2, x2, #1
    b.ne start
