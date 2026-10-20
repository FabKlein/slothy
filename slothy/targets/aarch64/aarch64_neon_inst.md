# AArch64 NEON instruction table

**Generated file — do not edit.**
Edit [aarch64_neon_instructions.json](aarch64_neon_instructions.json) instead; JSON is the source of truth.
Regenerate both tables from the repository root with:

```sh
python3 slothy/targets/aarch64/dump_instruction_tables.py
```

Only explicit JSON fields are shown; blank cells may inherit from the base.
This is not a complete ISA or CPU timing reference. See
[the specification guide](README.instructions.md) for scope and semantics.

| name | base | in_outs | inputs | outputs | pattern | register_restrictions |
| --- | --- | --- | --- | --- | --- | --- |
| fmov_w_to_s | Fmov |  | ["Wa"] | ["Sd"] | fmov &lt;Sd&gt;, &lt;Wa&gt; |  |
| sfadd_d | AArch64Instruction |  | ["Da","Db"] | ["Dd"] | fadd &lt;Dd&gt;, &lt;Da&gt;, &lt;Db&gt; |  |
| vadd | AArch64Instruction |  | ["Vb","Vc"] | ["Va"] | add &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;Vc&gt;.&lt;dt&gt; |  |
| vaddf | AArch64Instruction |  | ["Vb","Vc"] | ["Va"] | fadd &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;Vc&gt;.&lt;dt&gt; |  |
| vsub | AArch64Instruction |  | ["Vb","Vc"] | ["Va"] | sub &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;Vc&gt;.&lt;dt&gt; |  |
| vmov | AArch64Instruction |  | ["Va"] | ["Vd"] | mov &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt; |  |
| vmovi | AArch64Instruction |  |  | ["Vd"] | movi &lt;Vd&gt;.&lt;dt&gt;, &lt;imm&gt; |  |
| vxtn | AArch64Instruction |  | ["Va"] | ["Vd"] | xtn &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt; |  |
| rev64 | Vrev |  | ["Va"] | ["Vd"] | rev64 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt; |  |
| rev32 | Vrev |  | ["Va"] | ["Vd"] | rev32 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt; |  |
| uaddlp | AArch64Instruction |  | ["Va"] | ["Vd"] | uaddlp &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt; |  |
| vzip1 | Vzip |  | ["Va","Vb"] | ["Vd"] | zip1 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |
| vzip2 | Vzip |  | ["Va","Vb"] | ["Vd"] | zip2 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |
| vuzp1 | Vzip |  | ["Va","Vb"] | ["Vd"] | uzp1 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |
| vuzp2 | Vzip |  | ["Va","Vb"] | ["Vd"] | uzp2 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |
| vqrdmulh_lane | Vqdmulh |  | ["Va","Vb"] | ["Vd"] | sqrdmulh &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt0&gt;, &lt;Vb&gt;.&lt;dt1&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt1":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] |
| vqdmulh_lane | Vqdmulh |  | ["Va","Vb"] | ["Vd"] | sqdmulh &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt0&gt;, &lt;Vb&gt;.&lt;dt1&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt1":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] |
| vqrdmulh | Vqdmulh |  | ["Va","Vb"] | ["Vd"] | sqrdmulh &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |
| vqdmulh_vector | Vqdmulh |  | ["Va","Vb"] | ["Vd"] | sqdmulh &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |
| vins_d | Vins | ["Vd"] | ["Xa"] |  | ins &lt;Vd&gt;.d[&lt;index&gt;], &lt;Xa&gt; |  |
| vcnt | AArch64NeonCount |  | ["Va"] | ["Vd"] | cnt &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt; |  |
| vclz | AArch64NeonCount |  | ["Va"] | ["Vd"] | clz &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt; |  |
| mov_wtov_s | AArch64Instruction | ["Vd"] | ["Wa"] |  | mov &lt;Vd&gt;.s[&lt;index&gt;], &lt;Wa&gt; |  |
| mov_xtov_d | Mov_xtov_d | ["Vd"] | ["Xa"] |  | mov &lt;Vd&gt;.d[&lt;index&gt;], &lt;Xa&gt; |  |
| mov_xtov_d_xzr | Mov_xtov_d | ["Vd"] |  |  | mov &lt;Vd&gt;.d[&lt;index&gt;], xzr |  |
| mov_b00 | AArch64Instruction | ["Vd"] | ["Va"] |  | mov &lt;Vd&gt;.b[0], &lt;Va&gt;.b[0] |  |
| mov_d01 | AArch64Instruction | ["Vd"] | ["Va"] |  | mov &lt;Vd&gt;.d[0], &lt;Va&gt;.d[1] |  |
| mov_vtov_d | AArch64Instruction | ["Vd"] | ["Va"] |  | mov &lt;Vd&gt;.d[&lt;index0&gt;], &lt;Va&gt;.d[&lt;index1&gt;] |  |
| vrax1 | SHA3Instruction |  | ["Va","Vb"] | ["Vd"] | rax1 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |
| veor3 | SHA3Instruction |  | ["Va","Vb","Vc"] | ["Vd"] | eor3 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;Vc&gt;.&lt;dt&gt; |  |
| vbcax | SHA3Instruction |  | ["Va","Vb","Vc"] | ["Vd"] | bcax &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;Vc&gt;.&lt;dt&gt; |  |
| vxar | SHA3Instruction |  | ["Va","Vb"] | ["Vd"] | xar &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;imm&gt; |  |
| vtbl | AArch64Instruction |  | ["Va","Vb"] | ["Vd"] | tbl &lt;Vd&gt;.&lt;dt&gt;, {&lt;Va&gt;.&lt;dt&gt;}, &lt;Vb&gt;.&lt;dt&gt; |  |
| vand | AArch64NeonLogical |  | ["Va","Vb"] | ["Vd"] | and &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |
| vbic | AArch64NeonLogical |  | ["Va","Vb"] | ["Vd"] | bic &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |
| vbic_imm_shifted | AArch64NeonLogical | ["Vda"] |  |  | bic &lt;Vda&gt;.&lt;dt&gt;, &lt;imm0&gt;, &lt;barrel&gt; &lt;imm1&gt; |  |
| vmvn | AArch64NeonLogical |  | ["Va"] | ["Vd"] | mvn &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt; |  |
| vorr | AArch64NeonLogical |  | ["Va","Vb"] | ["Vd"] | orr &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |
| vorr_imm | AArch64NeonLogical | ["Vda"] |  |  | orr &lt;Vda&gt;.&lt;dt&gt;, &lt;imm&gt; |  |
| vorn | AArch64NeonLogical |  | ["Va","Vb"] | ["Vd"] | orn &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |
| veor | AArch64NeonLogical |  | ["Va","Vb"] | ["Vd"] | eor &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |
| vbif | AArch64Instruction | ["Vd"] | ["Va","Vb"] |  | bif &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt; |  |
| vmov_d | AArch64Instruction |  | ["Va"] | ["Dd"] | mov &lt;Dd&gt;, &lt;Va&gt;.d[1] |  |
| vext | AArch64Instruction |  | ["Va","Vb"] | ["Vd"] | ext &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;imm&gt; |  |
| vmul | Vmul |  | ["Va","Vb"] | ["Vd"] | mul &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |
| vmulf | Vmul |  | ["Va","Vb"] | ["Vd"] | fmul &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |
| vmla | Vmla | ["Vd"] | ["Va","Vb"] |  | mla &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |
| vfmla | vmla |  |  |  | fmla &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |
| vmls | Vmla | ["Vd"] | ["Va","Vb"] |  | mls &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |
| vfmls | vmls |  |  |  | fmls &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |
| vdup | AArch64Instruction |  | ["Xa"] | ["Vd"] | dup &lt;Vd&gt;.&lt;dt&gt;, &lt;Xa&gt; |  |
| vdup_w | AArch64Instruction |  | ["Wa"] | ["Vd"] | dup &lt;Vd&gt;.&lt;dt&gt;, &lt;Wa&gt; |  |
| vumull | Vmull |  | ["Va","Vb"] | ["Vd"] | umull &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |
| vumull2 | Vmull |  | ["Va","Vb"] | ["Vd"] | umull2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |
| vsmull | Vmull |  | ["Va","Vb"] | ["Vd"] | smull &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |
| vsmull2 | Vmull |  | ["Va","Vb"] | ["Vd"] | smull2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |
| vumlal | Vmlal | ["Vd"] | ["Va","Vb"] |  | umlal &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |
| vumlal2 | Vmlal | ["Vd"] | ["Va","Vb"] |  | umlal2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |
| vsmlal | Vmlal | ["Vd"] | ["Va","Vb"] |  | smlal &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |
| vsmlal2 | Vmlal | ["Vd"] | ["Va","Vb"] |  | smlal2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |
| vumlsl | Vmlal | ["Vd"] | ["Va","Vb"] |  | umlsl &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |
| vumlsl2 | Vmlal | ["Vd"] | ["Va","Vb"] |  | umlsl2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |
| vsmlsl | Vmlal | ["Vd"] | ["Va","Vb"] |  | smlsl &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |
| vsmlsl2 | Vmlal | ["Vd"] | ["Va","Vb"] |  | smlsl2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |
| vshl | VShiftImmediateBasic |  | ["Va"] | ["Vd"] | shl &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  |
| vshl_d | VShiftImmediateBasic |  | ["Da"] | ["Dd"] | shl &lt;Dd&gt;, &lt;Da&gt;, &lt;imm&gt; |  |
| vshrn | VShiftImmediateBasic |  | ["Va"] | ["Vd"] | shrn &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;imm&gt; |  |
| vsshr | VShiftImmediateBasic |  | ["Va"] | ["Vd"] | sshr &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  |
| vushr | VShiftImmediateBasic |  | ["Va"] | ["Vd"] | ushr &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  |
| vuxtl | VShiftImmediateBasic |  | ["Va"] | ["Vd"] | uxtl &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt; |  |
| vsrshr | VShiftImmediateRounding |  | ["Va"] | ["Vd"] | srshr &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  |
| vurshr | VShiftImmediateRounding |  | ["Va"] | ["Vd"] | urshr &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  |
| vushl_reg | VShiftRegBasic |  | ["Va","Vb"] | ["Vd"] | ushl &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |
| vsli | AArch64NeonShiftInsert | ["Vd"] | ["Va"] |  | sli &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  |
| vsri | AArch64NeonShiftInsert | ["Vd"] | ["Va"] |  | sri &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  |
| vusra | AArch64Instruction | ["Vd"] | ["Va"] |  | usra &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  |
| vmul_lane | Vmul |  | ["Va","Vb"] | ["Vd"] | mul &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt0&gt;, &lt;Vb&gt;.&lt;dt1&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt1":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] |
| vmla_lane | Vmla | ["Vd"] | ["Va","Vb"] |  | mla &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt0&gt;, &lt;Vb&gt;.&lt;dt1&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt1":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] |
| vmls_lane | Vmla | ["Vd"] | ["Va","Vb"] |  | mls &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt0&gt;, &lt;Vb&gt;.&lt;dt1&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt1":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] |
| vumull_lane | Vmull |  | ["Va","Vb"] | ["Vd"] | umull &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] |
| vumull2_lane | Vmull |  | ["Va","Vb"] | ["Vd"] | umull2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] |
| vsmull_lane | Vmull |  | ["Va","Vb"] | ["Vd"] | smull &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] |
| vsmull2_lane | Vmull |  | ["Va","Vb"] | ["Vd"] | smull2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] |
| vumlal_lane | Vmlal | ["Vd"] | ["Va","Vb"] |  | umlal &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] |
| vumlal2_lane | Vmlal | ["Vd"] | ["Va","Vb"] |  | umlal2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] |
| vsmlal_lane | Vmlal | ["Vd"] | ["Va","Vb"] |  | smlal &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] |
| vsmlal2_lane | Vmlal | ["Vd"] | ["Va","Vb"] |  | smlal2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] |
| vumlsl_lane | Vmlal | ["Vd"] | ["Va","Vb"] |  | umlsl &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] |
| vumlsl2_lane | Vmlal | ["Vd"] | ["Va","Vb"] |  | umlsl2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] |
| vsmlsl_lane | Vmlal | ["Vd"] | ["Va","Vb"] |  | smlsl &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] |
| vsmlsl2_lane | Vmlal | ["Vd"] | ["Va","Vb"] |  | smlsl2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] |
