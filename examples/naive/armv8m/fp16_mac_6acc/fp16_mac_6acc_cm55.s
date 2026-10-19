// Converted from the supplied GCC inline assembly; instruction order preserved.
// Register contract (not an AAPCS-callable function):
//   r0 = x, r1 = w, r2 = x stride in bytes, r3 = w stride in bytes
//   r12 = positive loop count, consumed by dls
//   q1..q6 = a0..a5, initialized accumulators, updated in place
//   scratch: q0, q7, r4..r11, lr; condition flags may change
// Each iteration advances r0 by 2 bytes and r1 by 16 bytes.
// Buffers must cover every strided load; vector loads read 16 bytes.
// No prologue/epilogue: the surrounding caller supplies and preserves registers.
// Optimize the loop at start with Arm_v81M / Arm_Cortex_M55.

.syntax unified
.thumb
.text
.p2align 2

    mov        r10, r0
    mov        r11, r1
    dls        lr, r12
start:
    vldrh.u16  q0, [r11]
    add        r11, r11, r3
    vldrh.u16  q7, [r11]
    ldrh       r4, [r10]
    vfma.f16   q1, q0, r4
    add        r10, r10, r2
    ldrh       r5, [r10]
    vfma.f16   q2, q0, r5
    add        r10, r10, r2
    ldrh       r6, [r10]
    vfma.f16   q3, q0, r6
    add        r11, r11, r3
    add        r10, r10, r2
    ldrh       r7, [r10]
    vfma.f16   q4, q0, r7
    add        r10, r10, r2
    ldrh       r8, [r10]
    vfma.f16   q5, q0, r8
    add        r10, r10, r2
    ldrh       r9, [r10]
    vfma.f16   q6, q0, r9
    add        r10, r10, r2
    vldrh.u16  q0, [r11]
    vfma.f16   q1, q7, r5
    ldrh       r4, [r10]
    vfma.f16   q2, q7, r6
    add        r10, r10, r2
    vfma.f16   q3, q7, r7
    add        r11, r11, r3
    vfma.f16   q4, q7, r8
    ldrh       r5, [r10]
    vfma.f16   q5, q7, r9
    vfma.f16   q6, q7, r4
    vldrh.u16  q7, [r11]
    vfma.f16   q1, q0, r6
    add        r10, r10, r2
    vfma.f16   q2, q0, r7
    ldrh       r6, [r10]
    vfma.f16   q3, q0, r8
    add        r11, r11, r3
    vfma.f16   q4, q0, r9
    vfma.f16   q5, q0, r4
    vfma.f16   q6, q0, r5
    vldrh.u16  q0, [r11]
    vfma.f16   q1, q7, r7
    add        r10, r10, r2
    vfma.f16   q2, q7, r8
    ldrh       r7, [r10]
    vfma.f16   q3, q7, r9
    add        r11, r11, r3
    vfma.f16   q4, q7, r4
    vfma.f16   q5, q7, r5
    vfma.f16   q6, q7, r6
    vldrh.u16  q7, [r11]
    vfma.f16   q1, q0, r8
    add        r10, r10, r2
    vfma.f16   q2, q0, r9
    ldrh       r8, [r10]
    vfma.f16   q3, q0, r4
    add        r11, r11, r3
    vfma.f16   q4, q0, r5
    vfma.f16   q5, q0, r6
    vfma.f16   q6, q0, r7
    vldrh.u16  q0, [r11]
    vfma.f16   q1, q7, r9
    add        r10, r10, r2
    vfma.f16   q2, q7, r4
    ldrh       r9, [r10]
    vfma.f16   q3, q7, r5
    add        r11, r11, r3
    vfma.f16   q4, q7, r6
    vfma.f16   q5, q7, r7
    vfma.f16   q6, q7, r8
    vldrh.u16  q7, [r11]
    vfma.f16   q1, q0, r4
    add        r10, r10, r2
    vfma.f16   q2, q0, r5
    ldrh       r4, [r10]
    vfma.f16   q3, q0, r6
    add        r11, r11, r3
    vfma.f16   q4, q0, r7
    vfma.f16   q5, q0, r8
    vfma.f16   q6, q0, r9
    vldrh.u16  q0, [r11]
    vfma.f16   q1, q7, r5
    add        r10, r10, r2
    vfma.f16   q2, q7, r6
    ldrh       r5, [r10]
    vfma.f16   q3, q7, r7
    vfma.f16   q4, q7, r8
    vfma.f16   q5, q7, r9
    vfma.f16   q6, q7, r4
    vfma.f16   q1, q0, r6
    add        r0, r0, #2
    vfma.f16   q2, q0, r7
    add        r1, r1, #16
    vfma.f16   q3, q0, r8
    mov        r10, r0
    vfma.f16   q4, q0, r9
    mov        r11, r1
    vfma.f16   q5, q0, r4
    vfma.f16   q6, q0, r5
    le         lr, start
