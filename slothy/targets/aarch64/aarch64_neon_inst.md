# AArch64 NEON instruction table

**Generated file — do not edit.**
Edit [aarch64_neon_instructions.json](aarch64_neon_instructions.json) instead; JSON is the source of truth.
Regenerate both tables from the repository root with:

```sh
python3 slothy/targets/aarch64/dump_instruction_tables.py
```

Only explicit JSON fields are shown. Operand fields may inherit from the base;
blank ISA requirements mean unclassified, not baseline-safe.
This is not a complete ISA or CPU timing reference. See
[the specification guide](README.instructions.md) for scope and semantics.

| name | base | conditional_features | in_outs | inputs | outputs | pattern | register_restrictions | required_features |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fmov_w_to_s | Fmov |  |  | ["Wa"] | ["Sd"] | fmov &lt;Sd&gt;, &lt;Wa&gt; |  | ["FEAT_FP"] |
| sfadd_d | AArch64Instruction |  |  | ["Da","Db"] | ["Dd"] | fadd &lt;Dd&gt;, &lt;Da&gt;, &lt;Db&gt; |  | ["FEAT_FP"] |
| vadd | AArch64Instruction |  |  | ["Vb","Vc"] | ["Va"] | add &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;Vc&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vaddf | AArch64Instruction | [{"when":{"dt":["4h","8h"]},"requires":["FEAT_FP16"]}] |  | ["Vb","Vc"] | ["Va"] | fadd &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;Vc&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vsub | AArch64Instruction |  |  | ["Vb","Vc"] | ["Va"] | sub &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;Vc&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vmov | AArch64Instruction |  |  | ["Va"] | ["Vd"] | mov &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt; |  | ["FEAT_AdvSIMD"] |
| vmovi | AArch64Instruction |  |  |  | ["Vd"] | movi &lt;Vd&gt;.&lt;dt&gt;, &lt;imm&gt; |  | ["FEAT_AdvSIMD"] |
| vxtn | AArch64Instruction |  |  | ["Va"] | ["Vd"] | xtn &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt; |  | ["FEAT_AdvSIMD"] |
| rev64 | Vrev |  |  | ["Va"] | ["Vd"] | rev64 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt; |  | ["FEAT_AdvSIMD"] |
| rev32 | Vrev |  |  | ["Va"] | ["Vd"] | rev32 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt; |  | ["FEAT_AdvSIMD"] |
| uaddlp | AArch64Instruction |  |  | ["Va"] | ["Vd"] | uaddlp &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt; |  | ["FEAT_AdvSIMD"] |
| vzip1 | Vzip |  |  | ["Va","Vb"] | ["Vd"] | zip1 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vzip2 | Vzip |  |  | ["Va","Vb"] | ["Vd"] | zip2 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vuzp1 | Vzip |  |  | ["Va","Vb"] | ["Vd"] | uzp1 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vuzp2 | Vzip |  |  | ["Va","Vb"] | ["Vd"] | uzp2 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vqrdmulh_lane | Vqdmulh |  |  | ["Va","Vb"] | ["Vd"] | sqrdmulh &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt0&gt;, &lt;Vb&gt;.&lt;dt1&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt1":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |
| vqdmulh_lane | Vqdmulh |  |  | ["Va","Vb"] | ["Vd"] | sqdmulh &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt0&gt;, &lt;Vb&gt;.&lt;dt1&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt1":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |
| vqrdmulh | Vqdmulh |  |  | ["Va","Vb"] | ["Vd"] | sqrdmulh &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vqdmulh_vector | Vqdmulh |  |  | ["Va","Vb"] | ["Vd"] | sqdmulh &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vins_d | Vins |  | ["Vd"] | ["Xa"] |  | ins &lt;Vd&gt;.d[&lt;index&gt;], &lt;Xa&gt; |  | ["FEAT_AdvSIMD"] |
| vcnt | AArch64NeonCount |  |  | ["Va"] | ["Vd"] | cnt &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vclz | AArch64NeonCount |  |  | ["Va"] | ["Vd"] | clz &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| mov_wtov_s | AArch64Instruction |  | ["Vd"] | ["Wa"] |  | mov &lt;Vd&gt;.s[&lt;index&gt;], &lt;Wa&gt; |  | ["FEAT_AdvSIMD"] |
| mov_xtov_d | Mov_xtov_d |  | ["Vd"] | ["Xa"] |  | mov &lt;Vd&gt;.d[&lt;index&gt;], &lt;Xa&gt; |  | ["FEAT_AdvSIMD"] |
| mov_xtov_d_xzr | Mov_xtov_d |  | ["Vd"] |  |  | mov &lt;Vd&gt;.d[&lt;index&gt;], xzr |  | ["FEAT_AdvSIMD"] |
| mov_b00 | AArch64Instruction |  | ["Vd"] | ["Va"] |  | mov &lt;Vd&gt;.b[0], &lt;Va&gt;.b[0] |  | ["FEAT_AdvSIMD"] |
| mov_d01 | AArch64Instruction |  | ["Vd"] | ["Va"] |  | mov &lt;Vd&gt;.d[0], &lt;Va&gt;.d[1] |  | ["FEAT_AdvSIMD"] |
| mov_vtov_d | AArch64Instruction |  | ["Vd"] | ["Va"] |  | mov &lt;Vd&gt;.d[&lt;index0&gt;], &lt;Va&gt;.d[&lt;index1&gt;] |  | ["FEAT_AdvSIMD"] |
| vrax1 | SHA3Instruction |  |  | ["Va","Vb"] | ["Vd"] | rax1 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD","FEAT_SHA3"] |
| veor3 | SHA3Instruction |  |  | ["Va","Vb","Vc"] | ["Vd"] | eor3 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;Vc&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD","FEAT_SHA3"] |
| vbcax | SHA3Instruction |  |  | ["Va","Vb","Vc"] | ["Vd"] | bcax &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;Vc&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD","FEAT_SHA3"] |
| vxar | SHA3Instruction |  |  | ["Va","Vb"] | ["Vd"] | xar &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;imm&gt; |  | ["FEAT_AdvSIMD","FEAT_SHA3"] |
| vtbl | AArch64Instruction |  |  | ["Va","Vb"] | ["Vd"] | tbl &lt;Vd&gt;.&lt;dt&gt;, {&lt;Va&gt;.&lt;dt&gt;}, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vand | AArch64NeonLogical |  |  | ["Va","Vb"] | ["Vd"] | and &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vbic | AArch64NeonLogical |  |  | ["Va","Vb"] | ["Vd"] | bic &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vbic_imm_shifted | AArch64NeonLogical |  | ["Vda"] |  |  | bic &lt;Vda&gt;.&lt;dt&gt;, &lt;imm0&gt;, &lt;barrel&gt; &lt;imm1&gt; |  | ["FEAT_AdvSIMD"] |
| vmvn | AArch64NeonLogical |  |  | ["Va"] | ["Vd"] | mvn &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vorr | AArch64NeonLogical |  |  | ["Va","Vb"] | ["Vd"] | orr &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vorr_imm | AArch64NeonLogical |  | ["Vda"] |  |  | orr &lt;Vda&gt;.&lt;dt&gt;, &lt;imm&gt; |  | ["FEAT_AdvSIMD"] |
| vorn | AArch64NeonLogical |  |  | ["Va","Vb"] | ["Vd"] | orn &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| veor | AArch64NeonLogical |  |  | ["Va","Vb"] | ["Vd"] | eor &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vbif | AArch64Instruction |  | ["Vd"] | ["Va","Vb"] |  | bif &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt; |  | ["FEAT_AdvSIMD"] |
| vmov_d | AArch64Instruction |  |  | ["Va"] | ["Dd"] | mov &lt;Dd&gt;, &lt;Va&gt;.d[1] |  | ["FEAT_AdvSIMD"] |
| vext | AArch64Instruction |  |  | ["Va","Vb"] | ["Vd"] | ext &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;imm&gt; |  | ["FEAT_AdvSIMD"] |
| vmul | Vmul |  |  | ["Va","Vb"] | ["Vd"] | mul &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vmulf | Vmul | [{"when":{"dt":["4h","8h"]},"requires":["FEAT_FP16"]}] |  | ["Va","Vb"] | ["Vd"] | fmul &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vmla | Vmla |  | ["Vd"] | ["Va","Vb"] |  | mla &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vfmla | vmla | [{"when":{"dt":["4h","8h"]},"requires":["FEAT_FP16"]}] |  |  |  | fmla &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vmls | Vmla |  | ["Vd"] | ["Va","Vb"] |  | mls &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vfmls | vmls | [{"when":{"dt":["4h","8h"]},"requires":["FEAT_FP16"]}] |  |  |  | fmls &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vdup | AArch64Instruction |  |  | ["Xa"] | ["Vd"] | dup &lt;Vd&gt;.&lt;dt&gt;, &lt;Xa&gt; |  | ["FEAT_AdvSIMD"] |
| vdup_w | AArch64Instruction |  |  | ["Wa"] | ["Vd"] | dup &lt;Vd&gt;.&lt;dt&gt;, &lt;Wa&gt; |  | ["FEAT_AdvSIMD"] |
| vumull | Vmull |  |  | ["Va","Vb"] | ["Vd"] | umull &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  | ["FEAT_AdvSIMD"] |
| vumull2 | Vmull |  |  | ["Va","Vb"] | ["Vd"] | umull2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  | ["FEAT_AdvSIMD"] |
| vsmull | Vmull |  |  | ["Va","Vb"] | ["Vd"] | smull &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  | ["FEAT_AdvSIMD"] |
| vsmull2 | Vmull |  |  | ["Va","Vb"] | ["Vd"] | smull2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  | ["FEAT_AdvSIMD"] |
| vumlal | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | umlal &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  | ["FEAT_AdvSIMD"] |
| vumlal2 | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | umlal2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  | ["FEAT_AdvSIMD"] |
| vsmlal | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | smlal &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  | ["FEAT_AdvSIMD"] |
| vsmlal2 | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | smlal2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  | ["FEAT_AdvSIMD"] |
| vumlsl | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | umlsl &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  | ["FEAT_AdvSIMD"] |
| vumlsl2 | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | umlsl2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  | ["FEAT_AdvSIMD"] |
| vsmlsl | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | smlsl &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  | ["FEAT_AdvSIMD"] |
| vsmlsl2 | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | smlsl2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  | ["FEAT_AdvSIMD"] |
| vshl | VShiftImmediateBasic |  |  | ["Va"] | ["Vd"] | shl &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  | ["FEAT_AdvSIMD"] |
| vshl_d | VShiftImmediateBasic |  |  | ["Da"] | ["Dd"] | shl &lt;Dd&gt;, &lt;Da&gt;, &lt;imm&gt; |  | ["FEAT_AdvSIMD"] |
| vshrn | VShiftImmediateBasic |  |  | ["Va"] | ["Vd"] | shrn &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;imm&gt; |  | ["FEAT_AdvSIMD"] |
| vsshr | VShiftImmediateBasic |  |  | ["Va"] | ["Vd"] | sshr &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  | ["FEAT_AdvSIMD"] |
| vushr | VShiftImmediateBasic |  |  | ["Va"] | ["Vd"] | ushr &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  | ["FEAT_AdvSIMD"] |
| vuxtl | VShiftImmediateBasic |  |  | ["Va"] | ["Vd"] | uxtl &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt; |  | ["FEAT_AdvSIMD"] |
| vsrshr | VShiftImmediateRounding |  |  | ["Va"] | ["Vd"] | srshr &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  | ["FEAT_AdvSIMD"] |
| vurshr | VShiftImmediateRounding |  |  | ["Va"] | ["Vd"] | urshr &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  | ["FEAT_AdvSIMD"] |
| vushl_reg | VShiftRegBasic |  |  | ["Va","Vb"] | ["Vd"] | ushl &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  | ["FEAT_AdvSIMD"] |
| vsli | AArch64NeonShiftInsert |  | ["Vd"] | ["Va"] |  | sli &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  | ["FEAT_AdvSIMD"] |
| vsri | AArch64NeonShiftInsert |  | ["Vd"] | ["Va"] |  | sri &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  | ["FEAT_AdvSIMD"] |
| vusra | AArch64Instruction |  | ["Vd"] | ["Va"] |  | usra &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  | ["FEAT_AdvSIMD"] |
| vmul_lane | Vmul |  |  | ["Va","Vb"] | ["Vd"] | mul &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt0&gt;, &lt;Vb&gt;.&lt;dt1&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt1":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |
| vmla_lane | Vmla |  | ["Vd"] | ["Va","Vb"] |  | mla &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt0&gt;, &lt;Vb&gt;.&lt;dt1&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt1":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |
| vmls_lane | Vmla |  | ["Vd"] | ["Va","Vb"] |  | mls &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt0&gt;, &lt;Vb&gt;.&lt;dt1&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt1":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |
| vumull_lane | Vmull |  |  | ["Va","Vb"] | ["Vd"] | umull &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |
| vumull2_lane | Vmull |  |  | ["Va","Vb"] | ["Vd"] | umull2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |
| vsmull_lane | Vmull |  |  | ["Va","Vb"] | ["Vd"] | smull &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |
| vsmull2_lane | Vmull |  |  | ["Va","Vb"] | ["Vd"] | smull2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |
| vumlal_lane | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | umlal &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |
| vumlal2_lane | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | umlal2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |
| vsmlal_lane | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | smlal &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |
| vsmlal2_lane | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | smlal2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |
| vumlsl_lane | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | umlsl &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |
| vumlsl2_lane | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | umlsl2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |
| vsmlsl_lane | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | smlsl &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |
| vsmlsl2_lane | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | smlsl2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |
