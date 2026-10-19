// SLOTHY Cortex-A520 SWP: 198 estimated steady-state cycles/tile.
// OPTIMAL within the current model; 346.22 solver seconds with timeout=600.
// Fixed registers, unroll=1, early instructions allowed, late instructions disabled.
// 315-instruction preamble, 322-instruction kernel, 7-instruction postamble.
// Enter before the preamble with x2 >= 1; x2=1 skips the kernel.
// Preamble/postamble, loop control and memory penalties are excluded from 198.
// REQUIRES DISJOINT SOURCE AND DESTINATION BUFFERS: not a general drop-in replacement.
// Software-pipelined original LDUR variant; FP accumulation order is preserved.
// Register-contract snippet, not an AAPCS-callable function.
// x0 = s (source), x1 = y (destination), x2 = positive tile count.
// v24-v31 contain the 32 FP32 coefficients and remain unchanged.
// Scratch/output vectors: v0-v7 and v16-v23; NZCV is clobbered.
// Each tile writes 128 bytes and advances both pointers by 128 bytes.
// Source accesses extend through byte 251 relative to each tile's x0.
// Memory annotations do not guarantee alias safety in the generated SWP schedule.
.text
.p2align 4
        ldur q16, [x0, #0]// @slothy:before=fir_store0
        ldur q21, [x0, #20]// @slothy:before=fir_store0
        ldur q20, [x0, #16]// @slothy:before=fir_store0
        fmul v0.4S, v16.4S, v24.S[0]
        ldur q17, [x0, #4]// @slothy:before=fir_store0
        ldur q16, [x0, #32]// @slothy:before=fir_store0
        fmul v1.4S, v20.4S, v24.S[0]
        fmla v0.4S, v17.4S, v24.S[1]
        ldur q18, [x0, #8]// @slothy:before=fir_store0
        ldur q22, [x0, #24]// @slothy:before=fir_store0
        fmla v1.4S, v21.4S, v24.S[1]
        fmla v0.4S, v18.4S, v24.S[2]
        ldur q19, [x0, #12]// @slothy:before=fir_store0
        ldur q23, [x0, #28]// @slothy:before=fir_store0
        fmla v1.4S, v22.4S, v24.S[2]
        fmul v2.4S, v16.4S, v24.S[0]
        fmla v0.4S, v19.4S, v24.S[3]
        ldur q17, [x0, #36]// @slothy:before=fir_store0
        ldur q18, [x0, #40]// @slothy:before=fir_store0
        fmla v1.4S, v23.4S, v24.S[3]
        fmla v0.4S, v20.4S, v25.S[0]
        ldur q19, [x0, #44]// @slothy:before=fir_store0
        fmla v2.4S, v17.4S, v24.S[1]
        fmla v1.4S, v16.4S, v25.S[0]
        ldur q20, [x0, #48]// @slothy:before=fir_store0
        fmla v0.4S, v21.4S, v25.S[1]
        fmla v2.4S, v18.4S, v24.S[2]
        fmla v1.4S, v17.4S, v25.S[1]
        fmul v3.4S, v20.4S, v24.S[0]
        ldur q21, [x0, #52]// @slothy:before=fir_store0
        fmla v0.4S, v22.4S, v25.S[2]
        fmla v2.4S, v19.4S, v24.S[3]
        fmla v3.4S, v21.4S, v24.S[1]
        fmla v1.4S, v18.4S, v25.S[2]
        ldur q22, [x0, #56]// @slothy:before=fir_store0
        fmla v0.4S, v23.4S, v25.S[3]
        ldur q23, [x0, #60]// @slothy:before=fir_store0
        fmla v2.4S, v20.4S, v25.S[0]
        fmla v3.4S, v22.4S, v24.S[2]
        fmla v1.4S, v19.4S, v25.S[3]
        fmla v0.4S, v16.4S, v26.S[0]
        ldur q16, [x0, #64]// @slothy:before=fir_store0
        fmla v2.4S, v21.4S, v25.S[1]
        fmla v3.4S, v23.4S, v24.S[3]
        fmla v1.4S, v20.4S, v26.S[0]
        fmul v4.4S, v16.4S, v24.S[0]
        fmla v0.4S, v17.4S, v26.S[1]
        ldur q17, [x0, #68]// @slothy:before=fir_store0
        fmla v2.4S, v22.4S, v25.S[2]
        fmla v3.4S, v16.4S, v25.S[0]
        fmla v1.4S, v21.4S, v26.S[1]
        fmla v4.4S, v17.4S, v24.S[1]
        fmla v0.4S, v18.4S, v26.S[2]
        ldur q18, [x0, #72]// @slothy:before=fir_store0
        fmla v2.4S, v23.4S, v25.S[3]
        fmla v1.4S, v22.4S, v26.S[2]
        fmla v3.4S, v17.4S, v25.S[1]
        fmla v4.4S, v18.4S, v24.S[2]
        fmla v0.4S, v19.4S, v26.S[3]
        ldur q19, [x0, #76]// @slothy:before=fir_store0
        fmla v2.4S, v16.4S, v26.S[0]
        fmla v3.4S, v18.4S, v25.S[2]
        fmla v1.4S, v23.4S, v26.S[3]
        fmla v4.4S, v19.4S, v24.S[3]
        fmla v0.4S, v20.4S, v27.S[0]
        ldur q20, [x0, #80]// @slothy:before=fir_store0
        fmla v2.4S, v17.4S, v26.S[1]
        fmla v1.4S, v16.4S, v27.S[0]
        fmla v3.4S, v19.4S, v25.S[3]
        fmul v5.4S, v20.4S, v24.S[0]
        fmla v4.4S, v20.4S, v25.S[0]
        fmla v0.4S, v21.4S, v27.S[1]
        ldur q21, [x0, #84]// @slothy:before=fir_store0
        fmla v2.4S, v18.4S, v26.S[2]
        fmla v3.4S, v20.4S, v26.S[0]
        fmla v1.4S, v17.4S, v27.S[1]
        fmla v5.4S, v21.4S, v24.S[1]
        fmla v4.4S, v21.4S, v25.S[1]
        fmla v0.4S, v22.4S, v27.S[2]
        ldur q22, [x0, #88]// @slothy:before=fir_store0
        fmla v2.4S, v19.4S, v26.S[3]
        fmla v1.4S, v18.4S, v27.S[2]
        fmla v3.4S, v21.4S, v26.S[1]
        fmla v5.4S, v22.4S, v24.S[2]
        fmla v4.4S, v22.4S, v25.S[2]
        fmla v0.4S, v23.4S, v27.S[3]
        ldur q23, [x0, #92]// @slothy:before=fir_store0
        fmla v2.4S, v20.4S, v27.S[0]
        fmla v3.4S, v22.4S, v26.S[2]
        fmla v1.4S, v19.4S, v27.S[3]
        fmla v4.4S, v23.4S, v25.S[3]
        fmla v5.4S, v23.4S, v24.S[3]
        fmla v0.4S, v16.4S, v28.S[0]
        ldur q16, [x0, #96]// @slothy:before=fir_store0
        fmla v2.4S, v21.4S, v27.S[1]
        fmla v3.4S, v23.4S, v26.S[3]
        fmla v1.4S, v20.4S, v28.S[0]
        fmla v4.4S, v16.4S, v26.S[0]
        fmla v5.4S, v16.4S, v25.S[0]
        fmla v0.4S, v17.4S, v28.S[1]
        ldur q17, [x0, #100]// @slothy:before=fir_store0
        fmul v6.4S, v16.4S, v24.S[0]
        fmla v2.4S, v22.4S, v27.S[2]
        fmla v3.4S, v16.4S, v27.S[0]
        fmla v1.4S, v21.4S, v28.S[1]
        fmla v5.4S, v17.4S, v25.S[1]
        fmla v4.4S, v17.4S, v26.S[1]
        fmla v0.4S, v18.4S, v28.S[2]
        ldur q18, [x0, #104]// @slothy:before=fir_store0
        fmla v6.4S, v17.4S, v24.S[1]
        fmla v2.4S, v23.4S, v27.S[3]
        fmla v3.4S, v17.4S, v27.S[1]
        fmla v1.4S, v22.4S, v28.S[2]
        fmla v4.4S, v18.4S, v26.S[2]
        fmla v5.4S, v18.4S, v25.S[2]
        fmla v0.4S, v19.4S, v28.S[3]
        ldur q19, [x0, #108]// @slothy:before=fir_store0
        fmla v6.4S, v18.4S, v24.S[2]
        fmla v2.4S, v16.4S, v28.S[0]
        fmla v3.4S, v18.4S, v27.S[2]
        fmla v1.4S, v23.4S, v28.S[3]
        fmla v5.4S, v19.4S, v25.S[3]
        fmla v4.4S, v19.4S, v26.S[3]
        fmla v0.4S, v20.4S, v29.S[0]
        ldur q20, [x0, #112]// @slothy:before=fir_store0
        fmla v6.4S, v19.4S, v24.S[3]
        fmla v2.4S, v17.4S, v28.S[1]
        fmla v1.4S, v16.4S, v29.S[0]
        fmla v3.4S, v19.4S, v27.S[3]
        fmul v7.4S, v20.4S, v24.S[0]
        fmla v5.4S, v20.4S, v26.S[0]
        fmla v0.4S, v21.4S, v29.S[1]
        ldur q21, [x0, #116]// @slothy:before=fir_store0
        fmla v6.4S, v20.4S, v25.S[0]
        fmla v2.4S, v18.4S, v28.S[2]
        fmla v4.4S, v20.4S, v27.S[0]
        fmla v1.4S, v17.4S, v29.S[1]
        fmla v7.4S, v21.4S, v24.S[1]
        fmla v5.4S, v21.4S, v26.S[1]
        fmla v0.4S, v22.4S, v29.S[2]
        ldur q22, [x0, #120]// @slothy:before=fir_store0
        fmla v6.4S, v21.4S, v25.S[1]
        fmla v2.4S, v19.4S, v28.S[3]
        fmla v4.4S, v21.4S, v27.S[1]
        fmla v1.4S, v18.4S, v29.S[2]
        fmla v5.4S, v22.4S, v26.S[2]
        fmla v7.4S, v22.4S, v24.S[2]
        fmla v0.4S, v23.4S, v29.S[3]
        ldur q23, [x0, #124]// @slothy:before=fir_store0
        fmla v6.4S, v22.4S, v25.S[2]
        fmla v2.4S, v20.4S, v29.S[0]
        fmla v4.4S, v22.4S, v27.S[2]
        fmla v1.4S, v19.4S, v29.S[3]
        fmla v7.4S, v23.4S, v24.S[3]
        fmla v5.4S, v23.4S, v26.S[3]
        fmla v0.4S, v16.4S, v30.S[0]
        ldur q16, [x0, #128]// @slothy:before=fir_store0
        fmla v6.4S, v23.4S, v25.S[3]
        fmla v2.4S, v21.4S, v29.S[1]
        fmla v4.4S, v23.4S, v27.S[3]
        fmla v1.4S, v20.4S, v30.S[0]
        fmla v7.4S, v16.4S, v25.S[0]
        fmla v5.4S, v16.4S, v27.S[0]
        fmla v0.4S, v17.4S, v30.S[1]
        ldur q17, [x0, #132]// @slothy:before=fir_store0
        fmla v6.4S, v16.4S, v26.S[0]
        fmla v2.4S, v22.4S, v29.S[2]
        fmla v4.4S, v16.4S, v28.S[0]
        fmla v1.4S, v21.4S, v30.S[1]
        fmla v5.4S, v17.4S, v27.S[1]
        fmla v7.4S, v17.4S, v25.S[1]
        fmla v0.4S, v18.4S, v30.S[2]
        ldur q18, [x0, #136]// @slothy:before=fir_store0
        fmla v6.4S, v17.4S, v26.S[1]
        fmla v2.4S, v23.4S, v29.S[3]
        fmla v1.4S, v22.4S, v30.S[2]
        fmla v3.4S, v20.4S, v28.S[0]
        fmla v7.4S, v18.4S, v25.S[2]
        fmla v5.4S, v18.4S, v27.S[2]
        fmla v0.4S, v19.4S, v30.S[3]
        ldur q19, [x0, #140]// @slothy:before=fir_store0
        fmla v2.4S, v16.4S, v30.S[0]
        fmla v6.4S, v18.4S, v26.S[2]
        fmla v1.4S, v23.4S, v30.S[3]
        fmla v3.4S, v21.4S, v28.S[1]
        fmla v5.4S, v19.4S, v27.S[3]
        fmla v7.4S, v19.4S, v25.S[3]
        fmla v0.4S, v20.4S, v31.S[0]
        ldur q20, [x0, #144]// @slothy:before=fir_store0
        fmla v2.4S, v17.4S, v30.S[1]
        fmla v6.4S, v19.4S, v26.S[3]
        fmla v1.4S, v16.4S, v31.S[0]
        fmla v3.4S, v22.4S, v28.S[2]
        fmla v7.4S, v20.4S, v26.S[0]
        fmla v5.4S, v20.4S, v28.S[0]
        fmla v0.4S, v21.4S, v31.S[1]
        ldur q21, [x0, #148]// @slothy:before=fir_store0
        fmla v2.4S, v18.4S, v30.S[2]
        fmla v6.4S, v20.4S, v27.S[0]
        fmla v1.4S, v17.4S, v31.S[1]
        fmla v3.4S, v23.4S, v28.S[3]
        fmla v7.4S, v21.4S, v26.S[1]
        fmla v5.4S, v21.4S, v28.S[1]
        fmla v0.4S, v22.4S, v31.S[2]
        ldur q22, [x0, #152]// @slothy:before=fir_store0
        fmla v2.4S, v19.4S, v30.S[3]
        fmla v6.4S, v21.4S, v27.S[1]
        fmla v3.4S, v16.4S, v29.S[0]
        fmla v1.4S, v18.4S, v31.S[2]
        fmla v7.4S, v22.4S, v26.S[2]
        fmla v5.4S, v22.4S, v28.S[2]
        fmla v0.4S, v23.4S, v31.S[3]
        ldur q23, [x0, #156]// @slothy:before=fir_store0
        fmla v4.4S, v17.4S, v28.S[1]
        fmla v6.4S, v22.4S, v27.S[2]
        fmla v3.4S, v17.4S, v29.S[1]
        fmla v2.4S, v20.4S, v31.S[0]
        fmla v7.4S, v23.4S, v26.S[3]
        ldur q17, [x0, #164]// @slothy:before=fir_store0
        ldur q16, [x0, #160]// @slothy:before=fir_store0
        fmla v5.4S, v23.4S, v28.S[3]
        fmla v4.4S, v18.4S, v28.S[2]
        fmla v6.4S, v23.4S, v27.S[3]
        fmla v3.4S, v18.4S, v29.S[2]
        fmla v2.4S, v21.4S, v31.S[1]
        ldur q18, [x0, #168]// @slothy:before=fir_store0
        fmla v7.4S, v16.4S, v27.S[0]
        fmla v1.4S, v19.4S, v31.S[3]
        fmla v5.4S, v16.4S, v29.S[0]
        fmla v6.4S, v16.4S, v28.S[0]
        fmla v4.4S, v19.4S, v28.S[3]
        fmla v3.4S, v19.4S, v29.S[3]
        fmla v2.4S, v22.4S, v31.S[2]
        fmla v7.4S, v17.4S, v27.S[1]
        stp q0, q1, [x1, #0]// @slothy:id=fir_store0
        fmla v5.4S, v17.4S, v29.S[1]
        fmla v4.4S, v20.4S, v29.S[0]
        fmla v6.4S, v17.4S, v28.S[1]
        fmla v2.4S, v23.4S, v31.S[3]
        fmla v3.4S, v20.4S, v30.S[0]
        ldur q19, [x0, #172]// @slothy:before=fir_store0
        fmla v7.4S, v18.4S, v27.S[2]
        fmla v5.4S, v18.4S, v29.S[2]
        fmla v4.4S, v21.4S, v29.S[1]
        fmla v6.4S, v18.4S, v28.S[2]
        fmla v3.4S, v21.4S, v30.S[1]
        ldur q21, [x0, #180]// @slothy:before=fir_store0
        ldur q20, [x0, #176]// @slothy:before=fir_store0
        fmla v7.4S, v19.4S, v27.S[3]
        fmla v5.4S, v19.4S, v29.S[3]
        fmla v4.4S, v22.4S, v29.S[2]
        fmla v6.4S, v19.4S, v28.S[3]
        fmla v3.4S, v22.4S, v30.S[2]
        ldur q22, [x0, #184]// @slothy:before=fir_store0
        fmla v7.4S, v20.4S, v28.S[0]
        fmla v5.4S, v20.4S, v30.S[0]
        fmla v4.4S, v23.4S, v29.S[3]
        fmla v6.4S, v20.4S, v29.S[0]
        fmla v3.4S, v23.4S, v30.S[3]
        ldur q23, [x0, #188]// @slothy:before=fir_store0
        fmla v7.4S, v21.4S, v28.S[1]
        fmla v5.4S, v21.4S, v30.S[1]
        fmla v4.4S, v16.4S, v30.S[0]
        fmla v6.4S, v21.4S, v29.S[1]
        fmla v3.4S, v16.4S, v31.S[0]
        ldur q16, [x0, #192]// @slothy:before=fir_store0
        fmla v7.4S, v22.4S, v28.S[2]
        fmla v5.4S, v22.4S, v30.S[2]
        fmla v6.4S, v22.4S, v29.S[2]
        fmla v4.4S, v17.4S, v30.S[1]
        fmla v3.4S, v17.4S, v31.S[1]
        ldur q17, [x0, #196]// @slothy:before=fir_store0
        fmla v7.4S, v23.4S, v28.S[3]
        fmla v5.4S, v23.4S, v30.S[3]
        fmla v6.4S, v23.4S, v29.S[3]
        fmla v4.4S, v18.4S, v30.S[2]
        fmla v3.4S, v18.4S, v31.S[2]
        ldur q18, [x0, #200]// @slothy:before=fir_store0
        fmla v7.4S, v16.4S, v29.S[0]
        fmla v5.4S, v16.4S, v31.S[0]
        fmla v6.4S, v16.4S, v30.S[0]
        ldur q16, [x0, #224]// @slothy:before=fir_store0
        fmla v4.4S, v19.4S, v30.S[3]
        fmla v7.4S, v17.4S, v29.S[1]
        fmla v3.4S, v19.4S, v31.S[3]
        fmla v5.4S, v17.4S, v31.S[1]
        fmla v6.4S, v17.4S, v30.S[1]
        ldur q17, [x0, #228]// @slothy:before=fir_store0
        fmla v4.4S, v20.4S, v31.S[0]
        fmla v7.4S, v18.4S, v29.S[2]
        ldur q19, [x0, #204]// @slothy:before=fir_store0
        fmla v5.4S, v18.4S, v31.S[2]
        fmla v6.4S, v18.4S, v30.S[2]
        ldur q20, [x0, #208]// @slothy:before=fir_store0
        fmla v4.4S, v21.4S, v31.S[1]
        fmla v7.4S, v19.4S, v29.S[3]
        ldur q18, [x0, #232]// @slothy:before=fir_store0
        ldur q21, [x0, #212]// @slothy:before=fir_store0
        fmla v5.4S, v19.4S, v31.S[3]
        fmla v6.4S, v19.4S, v30.S[3]
        fmla v4.4S, v22.4S, v31.S[2]
        fmla v7.4S, v20.4S, v30.S[0]
        ldur q19, [x0, #236]// @slothy:before=fir_store0
        ldur q22, [x0, #216]// @slothy:before=fir_store0
        fmla v6.4S, v20.4S, v31.S[0]
        fmla v4.4S, v23.4S, v31.S[3]
        fmla v7.4S, v21.4S, v30.S[1]
        stp q2, q3, [x1, #32]// @slothy:id=fir_store1 // @slothy:after=fir_store0
        stp q4, q5, [x1, #64]// @slothy:id=fir_store2 // @slothy:after=fir_store1
        fmla v6.4S, v21.4S, v31.S[1]
        fmla v7.4S, v22.4S, v30.S[2]
        ldur q23, [x0, #220]// @slothy:before=fir_store0
        fmla v6.4S, v22.4S, v31.S[2]
        fmla v7.4S, v23.4S, v30.S[3]
        add x0, x0, #128
        sub x2, x2, #1
cbz x2, start_postamble
start:
        fmla v7.4S, v16.4S, v31.S[0]
        ldur q16, [x0, #0]                  // @slothy:before=fir_store0
        ldur q21, [x0, #20]                 // @slothy:before=fir_store0
        ldur q20, [x0, #16]                 // @slothy:before=fir_store0
        fmul v0.4S, v16.4S, v24.S[0]
        fmla v7.4S, v17.4S, v31.S[1]
        ldur q17, [x0, #4]                  // @slothy:before=fir_store0
        ldur q16, [x0, #32]                 // @slothy:before=fir_store0
        fmul v1.4S, v20.4S, v24.S[0]
        fmla v0.4S, v17.4S, v24.S[1]
        fmla v7.4S, v18.4S, v31.S[2]
        ldur q18, [x0, #8]                  // @slothy:before=fir_store0
        ldur q22, [x0, #24]                 // @slothy:before=fir_store0
        fmla v1.4S, v21.4S, v24.S[1]
        fmla v6.4S, v23.4S, v31.S[3]
        fmla v0.4S, v18.4S, v24.S[2]
        fmla v7.4S, v19.4S, v31.S[3]
        ldur q19, [x0, #12]                 // @slothy:before=fir_store0
        ldur q23, [x0, #28]                 // @slothy:before=fir_store0
        fmla v1.4S, v22.4S, v24.S[2]
        fmul v2.4S, v16.4S, v24.S[0]
        fmla v0.4S, v19.4S, v24.S[3]
        ldur q17, [x0, #36]                 // @slothy:before=fir_store0
        ldur q18, [x0, #40]                 // @slothy:before=fir_store0
        fmla v1.4S, v23.4S, v24.S[3]
        fmla v0.4S, v20.4S, v25.S[0]
        ldur q19, [x0, #44]                 // @slothy:before=fir_store0
        fmla v2.4S, v17.4S, v24.S[1]
        fmla v1.4S, v16.4S, v25.S[0]
        stp q6, q7, [x1, #96]               // @slothy:id=fir_store3 // @slothy:after=fir_store2
        ldur q20, [x0, #48]                 // @slothy:before=fir_store0
        add x1, x1, #128
        fmla v0.4S, v21.4S, v25.S[1]
        fmla v2.4S, v18.4S, v24.S[2]
        fmla v1.4S, v17.4S, v25.S[1]
        fmul v3.4S, v20.4S, v24.S[0]
        ldur q21, [x0, #52]                 // @slothy:before=fir_store0
        fmla v0.4S, v22.4S, v25.S[2]
        fmla v2.4S, v19.4S, v24.S[3]
        fmla v3.4S, v21.4S, v24.S[1]
        fmla v1.4S, v18.4S, v25.S[2]
        ldur q22, [x0, #56]                 // @slothy:before=fir_store0
        fmla v0.4S, v23.4S, v25.S[3]
        ldur q23, [x0, #60]                 // @slothy:before=fir_store0
        fmla v2.4S, v20.4S, v25.S[0]
        fmla v3.4S, v22.4S, v24.S[2]
        fmla v1.4S, v19.4S, v25.S[3]
        fmla v0.4S, v16.4S, v26.S[0]
        ldur q16, [x0, #64]                 // @slothy:before=fir_store0
        fmla v2.4S, v21.4S, v25.S[1]
        fmla v3.4S, v23.4S, v24.S[3]
        fmla v1.4S, v20.4S, v26.S[0]
        fmul v4.4S, v16.4S, v24.S[0]
        fmla v0.4S, v17.4S, v26.S[1]
        ldur q17, [x0, #68]                 // @slothy:before=fir_store0
        fmla v2.4S, v22.4S, v25.S[2]
        fmla v3.4S, v16.4S, v25.S[0]
        fmla v1.4S, v21.4S, v26.S[1]
        fmla v4.4S, v17.4S, v24.S[1]
        fmla v0.4S, v18.4S, v26.S[2]
        ldur q18, [x0, #72]                 // @slothy:before=fir_store0
        fmla v2.4S, v23.4S, v25.S[3]
        fmla v1.4S, v22.4S, v26.S[2]
        fmla v3.4S, v17.4S, v25.S[1]
        fmla v4.4S, v18.4S, v24.S[2]
        fmla v0.4S, v19.4S, v26.S[3]
        ldur q19, [x0, #76]                 // @slothy:before=fir_store0
        fmla v2.4S, v16.4S, v26.S[0]
        fmla v3.4S, v18.4S, v25.S[2]
        fmla v1.4S, v23.4S, v26.S[3]
        fmla v4.4S, v19.4S, v24.S[3]
        fmla v0.4S, v20.4S, v27.S[0]
        ldur q20, [x0, #80]                 // @slothy:before=fir_store0
        fmla v2.4S, v17.4S, v26.S[1]
        fmla v1.4S, v16.4S, v27.S[0]
        fmla v3.4S, v19.4S, v25.S[3]
        fmul v5.4S, v20.4S, v24.S[0]
        fmla v4.4S, v20.4S, v25.S[0]
        fmla v0.4S, v21.4S, v27.S[1]
        ldur q21, [x0, #84]                 // @slothy:before=fir_store0
        fmla v2.4S, v18.4S, v26.S[2]
        fmla v3.4S, v20.4S, v26.S[0]
        fmla v1.4S, v17.4S, v27.S[1]
        fmla v5.4S, v21.4S, v24.S[1]
        fmla v4.4S, v21.4S, v25.S[1]
        fmla v0.4S, v22.4S, v27.S[2]
        ldur q22, [x0, #88]                 // @slothy:before=fir_store0
        fmla v2.4S, v19.4S, v26.S[3]
        fmla v1.4S, v18.4S, v27.S[2]
        fmla v3.4S, v21.4S, v26.S[1]
        fmla v5.4S, v22.4S, v24.S[2]
        fmla v4.4S, v22.4S, v25.S[2]
        fmla v0.4S, v23.4S, v27.S[3]
        ldur q23, [x0, #92]                 // @slothy:before=fir_store0
        fmla v2.4S, v20.4S, v27.S[0]
        fmla v3.4S, v22.4S, v26.S[2]
        fmla v1.4S, v19.4S, v27.S[3]
        fmla v4.4S, v23.4S, v25.S[3]
        fmla v5.4S, v23.4S, v24.S[3]
        fmla v0.4S, v16.4S, v28.S[0]
        ldur q16, [x0, #96]                 // @slothy:before=fir_store0
        fmla v2.4S, v21.4S, v27.S[1]
        fmla v3.4S, v23.4S, v26.S[3]
        fmla v1.4S, v20.4S, v28.S[0]
        fmla v4.4S, v16.4S, v26.S[0]
        fmla v5.4S, v16.4S, v25.S[0]
        fmla v0.4S, v17.4S, v28.S[1]
        ldur q17, [x0, #100]                // @slothy:before=fir_store0
        fmul v6.4S, v16.4S, v24.S[0]
        fmla v2.4S, v22.4S, v27.S[2]
        fmla v3.4S, v16.4S, v27.S[0]
        fmla v1.4S, v21.4S, v28.S[1]
        fmla v5.4S, v17.4S, v25.S[1]
        fmla v4.4S, v17.4S, v26.S[1]
        fmla v0.4S, v18.4S, v28.S[2]
        ldur q18, [x0, #104]                // @slothy:before=fir_store0
        fmla v6.4S, v17.4S, v24.S[1]
        fmla v2.4S, v23.4S, v27.S[3]
        fmla v3.4S, v17.4S, v27.S[1]
        fmla v1.4S, v22.4S, v28.S[2]
        fmla v4.4S, v18.4S, v26.S[2]
        fmla v5.4S, v18.4S, v25.S[2]
        fmla v0.4S, v19.4S, v28.S[3]
        ldur q19, [x0, #108]                // @slothy:before=fir_store0
        fmla v6.4S, v18.4S, v24.S[2]
        fmla v2.4S, v16.4S, v28.S[0]
        fmla v3.4S, v18.4S, v27.S[2]
        fmla v1.4S, v23.4S, v28.S[3]
        fmla v5.4S, v19.4S, v25.S[3]
        fmla v4.4S, v19.4S, v26.S[3]
        fmla v0.4S, v20.4S, v29.S[0]
        ldur q20, [x0, #112]                // @slothy:before=fir_store0
        fmla v6.4S, v19.4S, v24.S[3]
        fmla v2.4S, v17.4S, v28.S[1]
        fmla v1.4S, v16.4S, v29.S[0]
        fmla v3.4S, v19.4S, v27.S[3]
        fmul v7.4S, v20.4S, v24.S[0]
        fmla v5.4S, v20.4S, v26.S[0]
        fmla v0.4S, v21.4S, v29.S[1]
        ldur q21, [x0, #116]                // @slothy:before=fir_store0
        fmla v6.4S, v20.4S, v25.S[0]
        fmla v2.4S, v18.4S, v28.S[2]
        fmla v4.4S, v20.4S, v27.S[0]
        fmla v1.4S, v17.4S, v29.S[1]
        fmla v7.4S, v21.4S, v24.S[1]
        fmla v5.4S, v21.4S, v26.S[1]
        fmla v0.4S, v22.4S, v29.S[2]
        ldur q22, [x0, #120]                // @slothy:before=fir_store0
        fmla v6.4S, v21.4S, v25.S[1]
        fmla v2.4S, v19.4S, v28.S[3]
        fmla v4.4S, v21.4S, v27.S[1]
        fmla v1.4S, v18.4S, v29.S[2]
        fmla v5.4S, v22.4S, v26.S[2]
        fmla v7.4S, v22.4S, v24.S[2]
        fmla v0.4S, v23.4S, v29.S[3]
        ldur q23, [x0, #124]                // @slothy:before=fir_store0
        fmla v6.4S, v22.4S, v25.S[2]
        fmla v2.4S, v20.4S, v29.S[0]
        fmla v4.4S, v22.4S, v27.S[2]
        fmla v1.4S, v19.4S, v29.S[3]
        fmla v7.4S, v23.4S, v24.S[3]
        fmla v5.4S, v23.4S, v26.S[3]
        fmla v0.4S, v16.4S, v30.S[0]
        ldur q16, [x0, #128]                // @slothy:before=fir_store0
        fmla v6.4S, v23.4S, v25.S[3]
        fmla v2.4S, v21.4S, v29.S[1]
        fmla v4.4S, v23.4S, v27.S[3]
        fmla v1.4S, v20.4S, v30.S[0]
        fmla v7.4S, v16.4S, v25.S[0]
        fmla v5.4S, v16.4S, v27.S[0]
        fmla v0.4S, v17.4S, v30.S[1]
        ldur q17, [x0, #132]                // @slothy:before=fir_store0
        fmla v6.4S, v16.4S, v26.S[0]
        fmla v2.4S, v22.4S, v29.S[2]
        fmla v4.4S, v16.4S, v28.S[0]
        fmla v1.4S, v21.4S, v30.S[1]
        fmla v5.4S, v17.4S, v27.S[1]
        fmla v7.4S, v17.4S, v25.S[1]
        fmla v0.4S, v18.4S, v30.S[2]
        ldur q18, [x0, #136]                // @slothy:before=fir_store0
        fmla v6.4S, v17.4S, v26.S[1]
        fmla v2.4S, v23.4S, v29.S[3]
        fmla v1.4S, v22.4S, v30.S[2]
        fmla v3.4S, v20.4S, v28.S[0]
        fmla v7.4S, v18.4S, v25.S[2]
        fmla v5.4S, v18.4S, v27.S[2]
        fmla v0.4S, v19.4S, v30.S[3]
        ldur q19, [x0, #140]                // @slothy:before=fir_store0
        fmla v2.4S, v16.4S, v30.S[0]
        fmla v6.4S, v18.4S, v26.S[2]
        fmla v1.4S, v23.4S, v30.S[3]
        fmla v3.4S, v21.4S, v28.S[1]
        fmla v5.4S, v19.4S, v27.S[3]
        fmla v7.4S, v19.4S, v25.S[3]
        fmla v0.4S, v20.4S, v31.S[0]
        ldur q20, [x0, #144]                // @slothy:before=fir_store0
        fmla v2.4S, v17.4S, v30.S[1]
        fmla v6.4S, v19.4S, v26.S[3]
        fmla v1.4S, v16.4S, v31.S[0]
        fmla v3.4S, v22.4S, v28.S[2]
        fmla v7.4S, v20.4S, v26.S[0]
        fmla v5.4S, v20.4S, v28.S[0]
        fmla v0.4S, v21.4S, v31.S[1]
        ldur q21, [x0, #148]                // @slothy:before=fir_store0
        fmla v2.4S, v18.4S, v30.S[2]
        fmla v6.4S, v20.4S, v27.S[0]
        fmla v1.4S, v17.4S, v31.S[1]
        fmla v3.4S, v23.4S, v28.S[3]
        fmla v7.4S, v21.4S, v26.S[1]
        fmla v5.4S, v21.4S, v28.S[1]
        fmla v0.4S, v22.4S, v31.S[2]
        ldur q22, [x0, #152]                // @slothy:before=fir_store0
        fmla v2.4S, v19.4S, v30.S[3]
        fmla v6.4S, v21.4S, v27.S[1]
        fmla v3.4S, v16.4S, v29.S[0]
        fmla v1.4S, v18.4S, v31.S[2]
        fmla v7.4S, v22.4S, v26.S[2]
        fmla v5.4S, v22.4S, v28.S[2]
        fmla v0.4S, v23.4S, v31.S[3]
        ldur q23, [x0, #156]                // @slothy:before=fir_store0
        fmla v4.4S, v17.4S, v28.S[1]
        fmla v6.4S, v22.4S, v27.S[2]
        fmla v3.4S, v17.4S, v29.S[1]
        fmla v2.4S, v20.4S, v31.S[0]
        fmla v7.4S, v23.4S, v26.S[3]
        ldur q17, [x0, #164]                // @slothy:before=fir_store0
        ldur q16, [x0, #160]                // @slothy:before=fir_store0
        fmla v5.4S, v23.4S, v28.S[3]
        fmla v4.4S, v18.4S, v28.S[2]
        fmla v6.4S, v23.4S, v27.S[3]
        fmla v3.4S, v18.4S, v29.S[2]
        fmla v2.4S, v21.4S, v31.S[1]
        ldur q18, [x0, #168]                // @slothy:before=fir_store0
        fmla v7.4S, v16.4S, v27.S[0]
        fmla v1.4S, v19.4S, v31.S[3]
        fmla v5.4S, v16.4S, v29.S[0]
        fmla v6.4S, v16.4S, v28.S[0]
        fmla v4.4S, v19.4S, v28.S[3]
        fmla v3.4S, v19.4S, v29.S[3]
        fmla v2.4S, v22.4S, v31.S[2]
        fmla v7.4S, v17.4S, v27.S[1]
        stp q0, q1, [x1, #0]                // @slothy:id=fir_store0
        fmla v5.4S, v17.4S, v29.S[1]
        fmla v4.4S, v20.4S, v29.S[0]
        fmla v6.4S, v17.4S, v28.S[1]
        fmla v2.4S, v23.4S, v31.S[3]
        fmla v3.4S, v20.4S, v30.S[0]
        ldur q19, [x0, #172]                // @slothy:before=fir_store0
        fmla v7.4S, v18.4S, v27.S[2]
        fmla v5.4S, v18.4S, v29.S[2]
        fmla v4.4S, v21.4S, v29.S[1]
        fmla v6.4S, v18.4S, v28.S[2]
        fmla v3.4S, v21.4S, v30.S[1]
        ldur q21, [x0, #180]                // @slothy:before=fir_store0
        ldur q20, [x0, #176]                // @slothy:before=fir_store0
        fmla v7.4S, v19.4S, v27.S[3]
        fmla v5.4S, v19.4S, v29.S[3]
        fmla v4.4S, v22.4S, v29.S[2]
        fmla v6.4S, v19.4S, v28.S[3]
        fmla v3.4S, v22.4S, v30.S[2]
        ldur q22, [x0, #184]                // @slothy:before=fir_store0
        fmla v7.4S, v20.4S, v28.S[0]
        fmla v5.4S, v20.4S, v30.S[0]
        fmla v4.4S, v23.4S, v29.S[3]
        fmla v6.4S, v20.4S, v29.S[0]
        fmla v3.4S, v23.4S, v30.S[3]
        ldur q23, [x0, #188]                // @slothy:before=fir_store0
        fmla v7.4S, v21.4S, v28.S[1]
        fmla v5.4S, v21.4S, v30.S[1]
        fmla v4.4S, v16.4S, v30.S[0]
        fmla v6.4S, v21.4S, v29.S[1]
        fmla v3.4S, v16.4S, v31.S[0]
        ldur q16, [x0, #192]                // @slothy:before=fir_store0
        fmla v7.4S, v22.4S, v28.S[2]
        fmla v5.4S, v22.4S, v30.S[2]
        fmla v6.4S, v22.4S, v29.S[2]
        fmla v4.4S, v17.4S, v30.S[1]
        fmla v3.4S, v17.4S, v31.S[1]
        ldur q17, [x0, #196]                // @slothy:before=fir_store0
        fmla v7.4S, v23.4S, v28.S[3]
        fmla v5.4S, v23.4S, v30.S[3]
        fmla v6.4S, v23.4S, v29.S[3]
        fmla v4.4S, v18.4S, v30.S[2]
        fmla v3.4S, v18.4S, v31.S[2]
        ldur q18, [x0, #200]                // @slothy:before=fir_store0
        fmla v7.4S, v16.4S, v29.S[0]
        fmla v5.4S, v16.4S, v31.S[0]
        fmla v6.4S, v16.4S, v30.S[0]
        ldur q16, [x0, #224]                // @slothy:before=fir_store0
        fmla v4.4S, v19.4S, v30.S[3]
        fmla v7.4S, v17.4S, v29.S[1]
        fmla v3.4S, v19.4S, v31.S[3]
        fmla v5.4S, v17.4S, v31.S[1]
        fmla v6.4S, v17.4S, v30.S[1]
        ldur q17, [x0, #228]                // @slothy:before=fir_store0
        fmla v4.4S, v20.4S, v31.S[0]
        fmla v7.4S, v18.4S, v29.S[2]
        ldur q19, [x0, #204]                // @slothy:before=fir_store0
        fmla v5.4S, v18.4S, v31.S[2]
        fmla v6.4S, v18.4S, v30.S[2]
        ldur q20, [x0, #208]                // @slothy:before=fir_store0
        fmla v4.4S, v21.4S, v31.S[1]
        fmla v7.4S, v19.4S, v29.S[3]
        ldur q18, [x0, #232]                // @slothy:before=fir_store0
        ldur q21, [x0, #212]                // @slothy:before=fir_store0
        fmla v5.4S, v19.4S, v31.S[3]
        fmla v6.4S, v19.4S, v30.S[3]
        fmla v4.4S, v22.4S, v31.S[2]
        fmla v7.4S, v20.4S, v30.S[0]
        ldur q19, [x0, #236]                // @slothy:before=fir_store0
        ldur q22, [x0, #216]                // @slothy:before=fir_store0
        fmla v6.4S, v20.4S, v31.S[0]
        fmla v4.4S, v23.4S, v31.S[3]
        fmla v7.4S, v21.4S, v30.S[1]
        stp q2, q3, [x1, #32]               // @slothy:id=fir_store1 // @slothy:after=fir_store0
        stp q4, q5, [x1, #64]               // @slothy:id=fir_store2 // @slothy:after=fir_store1
        fmla v6.4S, v21.4S, v31.S[1]
        fmla v7.4S, v22.4S, v30.S[2]
        ldur q23, [x0, #220]                // @slothy:before=fir_store0
        fmla v6.4S, v22.4S, v31.S[2]
        fmla v7.4S, v23.4S, v30.S[3]
        add x0, x0, #128
        subs x2, x2, #1
        b.ne start
start_postamble:// end of loop kernel
        fmla v7.4S, v16.4S, v31.S[0]
        fmla v7.4S, v17.4S, v31.S[1]
        fmla v7.4S, v18.4S, v31.S[2]
        fmla v6.4S, v23.4S, v31.S[3]
        fmla v7.4S, v19.4S, v31.S[3]
        stp q6, q7, [x1, #96]// @slothy:id=fir_store3 // @slothy:after=fir_store2
        add x1, x1, #128
        b start_end
start_end:
