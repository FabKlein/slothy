// Original body: 20 estimated cycles per 16-byte block.
// SWP unroll x2: 32 estimated cycles per 32-byte pair (16 per original block); bound 32.0.
// Early instructions: 26; exceptional pairs: 1.
// Estimates exclude scalar loop control, setup, drain and tail costs.
// Signed-byte 2x4 dot-product loop; scalar loop control, no LE/LETP.
// Register-contract snippet, NOT an AAPCS-callable function.
// Pointers: r1=ip_row_0, r3=ip_row_1, r5=col_base. r7=unsigned byte count.
// Accumulators: r0=a00, r2=a10, r4=a01, r6=a11,
//               r8=a02, r10=a12, r12=a03, r14=a13.
// LR is an accumulator: the caller must save its return address elsewhere.
// Each full block advances both row pointers by 16 and col_base by 64 bytes.
// Any unsigned count: process full blocks, leave count%16. No partial tail.
// Scratch q0-q7, NZCV. Preserve ABI-required registers in the surrounding code.
.syntax unified
.thumb
.text
.p2align 2
    cmp r7, #16
    blo done
    cmp r7, #64
    blo scalar_tail
        vldrb.8 q1, [r5], #16
        vldrb.8 q6, [r3], #16
        vmladava.S8 r2, q6, q1
        vldrb.8 q7, [r1], #16
        vmladava.S8 r0, q7, q1
        vldrb.8 q3, [r5], #16
        vldrb.8 q0, [r5], #16
        vmladava.S8 r6, q6, q3
        vldrb.8 q5, [r5], #16
        vmladava.S8 r10, q6, q0
        vldrb.8 q1, [r3], #16
        vmladava.S8 r14, q6, q5
        vldrb.8 q4, [r5], #16
        vmladava.S8 r2, q1, q4
        vldrb.8 q2, [r1], #16
        vmladava.S8 r0, q2, q4
        vldrb.8 q6, [r5], #16
        vmladava.S8 r4, q7, q3
        vldrb.8 q4, [r5], #16
        vmladava.S8 r8, q7, q0
        vldrb.8 q0, [r5], #16
        vmladava.S8 r6, q1, q6
        vmladava.S8 r10, q1, q4
        vmladava.S8 r14, q1, q0
        vmladava.S8 r4, q2, q6
        vmladava.S8 r8, q2, q4
    sub r7, r7, #32
.p2align 2
start:
        vldrb.8 q1, [r5], #16
        vmladava.S8 r12, q7, q5
        vldrb.8 q6, [r3], #16
        vmladava.S8 r2, q6, q1
        vldrb.8 q7, [r1], #16
        vmladava.S8 r0, q7, q1
        vldrb.8 q3, [r5], #16
        vmladava.S8 r12, q2, q0
        vldrb.8 q0, [r5], #16
        vmladava.S8 r6, q6, q3
        vldrb.8 q5, [r5], #16
        vmladava.S8 r10, q6, q0
        vldrb.8 q1, [r3], #16
        vmladava.S8 r14, q6, q5
        vldrb.8 q4, [r5], #16
        vmladava.S8 r2, q1, q4
        vldrb.8 q2, [r1], #16
        vmladava.S8 r0, q2, q4
        vldrb.8 q6, [r5], #16
        vmladava.S8 r4, q7, q3
        vldrb.8 q4, [r5], #16
        vmladava.S8 r8, q7, q0
        vldrb.8 q0, [r5], #16
        vmladava.S8 r6, q1, q6
        vmladava.S8 r10, q1, q4
        vmladava.S8 r14, q1, q0
        vmladava.S8 r4, q2, q6
        vmladava.S8 r8, q2, q4
    subs r7, r7, #32
    cmp r7, #32
    bhs start
        vmladava.S8 r12, q7, q5
        vmladava.S8 r12, q2, q0
    cmp r7, #16
    blo done
.p2align 2
scalar_tail:
    vldrb.8 q0, [r1], #16
    vldrb.8 q1, [r3], #16
    vldrb.8 q2, [r5], #16
    vmladava.s8 r0, q0, q2
    vmladava.s8 r2, q1, q2
    vldrb.8 q3, [r5], #16
    vmladava.s8 r4, q0, q3
    vmladava.s8 r6, q1, q3
    vldrb.8 q4, [r5], #16
    vmladava.s8 r8, q0, q4
    vmladava.s8 r10, q1, q4
    vldrb.8 q5, [r5], #16
    vmladava.s8 r12, q0, q5
    vmladava.s8 r14, q1, q5
    subs r7, r7, #16
    cmp r7, #16
    bhs scalar_tail
done:
