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

| name | addr_source | base | conditional_features | in_outs | inputs | outputs | pattern | pre_index_from_immediate | register_restrictions | required_features | restore_immediate_from_pre_index | set_increment_from_immediate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fmov_w_to_s |  | Fmov |  |  | ["Wa"] | ["Sd"] | fmov &lt;Sd&gt;, &lt;Wa&gt; |  |  | ["FEAT_FP"] |  |  |
| sfadd_d |  | AArch64Instruction |  |  | ["Da","Db"] | ["Dd"] | fadd &lt;Dd&gt;, &lt;Da&gt;, &lt;Db&gt; |  |  | ["FEAT_FP"] |  |  |
| vadd |  | AArch64Instruction |  |  | ["Vb","Vc"] | ["Va"] | add &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;Vc&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vaddf |  | AArch64Instruction | [{"when":{"dt":["4h","8h"]},"requires":["FEAT_FP16"]}] |  | ["Vb","Vc"] | ["Va"] | fadd &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;Vc&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vsub |  | AArch64Instruction |  |  | ["Vb","Vc"] | ["Va"] | sub &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;Vc&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vmov |  | AArch64Instruction |  |  | ["Va"] | ["Vd"] | mov &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vmovi |  | AArch64Instruction |  |  |  | ["Vd"] | movi &lt;Vd&gt;.&lt;dt&gt;, &lt;imm&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vxtn |  | AArch64Instruction |  |  | ["Va"] | ["Vd"] | xtn &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| rev64 |  | Vrev |  |  | ["Va"] | ["Vd"] | rev64 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| rev32 |  | Vrev |  |  | ["Va"] | ["Vd"] | rev32 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| uaddlp |  | AArch64Instruction |  |  | ["Va"] | ["Vd"] | uaddlp &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vzip1 |  | Vzip |  |  | ["Va","Vb"] | ["Vd"] | zip1 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vzip2 |  | Vzip |  |  | ["Va","Vb"] | ["Vd"] | zip2 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vuzp1 |  | Vzip |  |  | ["Va","Vb"] | ["Vd"] | uzp1 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vuzp2 |  | Vzip |  |  | ["Va","Vb"] | ["Vd"] | uzp2 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vqrdmulh_lane |  | Vqdmulh |  |  | ["Va","Vb"] | ["Vd"] | sqrdmulh &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt0&gt;, &lt;Vb&gt;.&lt;dt1&gt;[&lt;index&gt;] |  | [{"operand":"Vb","when":{"dt1":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |  |  |
| vqdmulh_lane |  | Vqdmulh |  |  | ["Va","Vb"] | ["Vd"] | sqdmulh &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt0&gt;, &lt;Vb&gt;.&lt;dt1&gt;[&lt;index&gt;] |  | [{"operand":"Vb","when":{"dt1":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |  |  |
| vqrdmulh |  | Vqdmulh |  |  | ["Va","Vb"] | ["Vd"] | sqrdmulh &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vqdmulh_vector |  | Vqdmulh |  |  | ["Va","Vb"] | ["Vd"] | sqdmulh &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vins_d |  | Vins |  | ["Vd"] | ["Xa"] |  | ins &lt;Vd&gt;.d[&lt;index&gt;], &lt;Xa&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vcnt |  | AArch64NeonCount |  |  | ["Va"] | ["Vd"] | cnt &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vclz |  | AArch64NeonCount |  |  | ["Va"] | ["Vd"] | clz &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| mov_wtov_s |  | AArch64Instruction |  | ["Vd"] | ["Wa"] |  | mov &lt;Vd&gt;.s[&lt;index&gt;], &lt;Wa&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| mov_xtov_d |  | Mov_xtov_d |  | ["Vd"] | ["Xa"] |  | mov &lt;Vd&gt;.d[&lt;index&gt;], &lt;Xa&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| mov_xtov_d_xzr |  | Mov_xtov_d |  | ["Vd"] |  |  | mov &lt;Vd&gt;.d[&lt;index&gt;], xzr |  |  | ["FEAT_AdvSIMD"] |  |  |
| mov_b00 |  | AArch64Instruction |  | ["Vd"] | ["Va"] |  | mov &lt;Vd&gt;.b[0], &lt;Va&gt;.b[0] |  |  | ["FEAT_AdvSIMD"] |  |  |
| mov_d01 |  | AArch64Instruction |  | ["Vd"] | ["Va"] |  | mov &lt;Vd&gt;.d[0], &lt;Va&gt;.d[1] |  |  | ["FEAT_AdvSIMD"] |  |  |
| mov_vtov_d |  | AArch64Instruction |  | ["Vd"] | ["Va"] |  | mov &lt;Vd&gt;.d[&lt;index0&gt;], &lt;Va&gt;.d[&lt;index1&gt;] |  |  | ["FEAT_AdvSIMD"] |  |  |
| vrax1 |  | SHA3Instruction |  |  | ["Va","Vb"] | ["Vd"] | rax1 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD","FEAT_SHA3"] |  |  |
| veor3 |  | SHA3Instruction |  |  | ["Va","Vb","Vc"] | ["Vd"] | eor3 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;Vc&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD","FEAT_SHA3"] |  |  |
| vbcax |  | SHA3Instruction |  |  | ["Va","Vb","Vc"] | ["Vd"] | bcax &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;Vc&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD","FEAT_SHA3"] |  |  |
| vxar |  | SHA3Instruction |  |  | ["Va","Vb"] | ["Vd"] | xar &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;imm&gt; |  |  | ["FEAT_AdvSIMD","FEAT_SHA3"] |  |  |
| vtbl |  | AArch64Instruction |  |  | ["Va","Vb"] | ["Vd"] | tbl &lt;Vd&gt;.&lt;dt&gt;, {&lt;Va&gt;.&lt;dt&gt;}, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vand |  | AArch64NeonLogical |  |  | ["Va","Vb"] | ["Vd"] | and &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vbic |  | AArch64NeonLogical |  |  | ["Va","Vb"] | ["Vd"] | bic &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vbic_imm_shifted |  | AArch64NeonLogical |  | ["Vda"] |  |  | bic &lt;Vda&gt;.&lt;dt&gt;, &lt;imm0&gt;, &lt;barrel&gt; &lt;imm1&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vmvn |  | AArch64NeonLogical |  |  | ["Va"] | ["Vd"] | mvn &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vorr |  | AArch64NeonLogical |  |  | ["Va","Vb"] | ["Vd"] | orr &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vorr_imm |  | AArch64NeonLogical |  | ["Vda"] |  |  | orr &lt;Vda&gt;.&lt;dt&gt;, &lt;imm&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vorn |  | AArch64NeonLogical |  |  | ["Va","Vb"] | ["Vd"] | orn &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| veor |  | AArch64NeonLogical |  |  | ["Va","Vb"] | ["Vd"] | eor &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vbif |  | AArch64Instruction |  | ["Vd"] | ["Va","Vb"] |  | bif &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vmov_d |  | AArch64Instruction |  |  | ["Va"] | ["Dd"] | mov &lt;Dd&gt;, &lt;Va&gt;.d[1] |  |  | ["FEAT_AdvSIMD"] |  |  |
| vext |  | AArch64Instruction |  |  | ["Va","Vb"] | ["Vd"] | ext &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt;, &lt;imm&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vmul |  | Vmul |  |  | ["Va","Vb"] | ["Vd"] | mul &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vmulf |  | Vmul | [{"when":{"dt":["4h","8h"]},"requires":["FEAT_FP16"]}] |  | ["Va","Vb"] | ["Vd"] | fmul &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vmla |  | Vmla |  | ["Vd"] | ["Va","Vb"] |  | mla &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vfmla |  | vmla | [{"when":{"dt":["4h","8h"]},"requires":["FEAT_FP16"]}] |  |  |  | fmla &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vmls |  | Vmla |  | ["Vd"] | ["Va","Vb"] |  | mls &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vfmls |  | vmls | [{"when":{"dt":["4h","8h"]},"requires":["FEAT_FP16"]}] |  |  |  | fmls &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vdup |  | AArch64Instruction |  |  | ["Xa"] | ["Vd"] | dup &lt;Vd&gt;.&lt;dt&gt;, &lt;Xa&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vdup_w |  | AArch64Instruction |  |  | ["Wa"] | ["Vd"] | dup &lt;Vd&gt;.&lt;dt&gt;, &lt;Wa&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vumull |  | Vmull |  |  | ["Va","Vb"] | ["Vd"] | umull &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vumull2 |  | Vmull |  |  | ["Va","Vb"] | ["Vd"] | umull2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vsmull |  | Vmull |  |  | ["Va","Vb"] | ["Vd"] | smull &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vsmull2 |  | Vmull |  |  | ["Va","Vb"] | ["Vd"] | smull2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vumlal |  | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | umlal &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vumlal2 |  | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | umlal2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vsmlal |  | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | smlal &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vsmlal2 |  | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | smlal2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vumlsl |  | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | umlsl &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vumlsl2 |  | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | umlsl2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vsmlsl |  | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | smlsl &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vsmlsl2 |  | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | smlsl2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt1&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vshl |  | VShiftImmediateBasic |  |  | ["Va"] | ["Vd"] | shl &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vshl_d |  | VShiftImmediateBasic |  |  | ["Da"] | ["Dd"] | shl &lt;Dd&gt;, &lt;Da&gt;, &lt;imm&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vshrn |  | VShiftImmediateBasic |  |  | ["Va"] | ["Vd"] | shrn &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;imm&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vsshr |  | VShiftImmediateBasic |  |  | ["Va"] | ["Vd"] | sshr &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vushr |  | VShiftImmediateBasic |  |  | ["Va"] | ["Vd"] | ushr &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vuxtl |  | VShiftImmediateBasic |  |  | ["Va"] | ["Vd"] | uxtl &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vsrshr |  | VShiftImmediateRounding |  |  | ["Va"] | ["Vd"] | srshr &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vurshr |  | VShiftImmediateRounding |  |  | ["Va"] | ["Vd"] | urshr &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vushl_reg |  | VShiftRegBasic |  |  | ["Va","Vb"] | ["Vd"] | ushl &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vsli |  | AArch64NeonShiftInsert |  | ["Vd"] | ["Va"] |  | sli &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vsri |  | AArch64NeonShiftInsert |  | ["Vd"] | ["Va"] |  | sri &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vusra |  | AArch64Instruction |  | ["Vd"] | ["Va"] |  | usra &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vmul_lane |  | Vmul |  |  | ["Va","Vb"] | ["Vd"] | mul &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt0&gt;, &lt;Vb&gt;.&lt;dt1&gt;[&lt;index&gt;] |  | [{"operand":"Vb","when":{"dt1":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |  |  |
| vmla_lane |  | Vmla |  | ["Vd"] | ["Va","Vb"] |  | mla &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt0&gt;, &lt;Vb&gt;.&lt;dt1&gt;[&lt;index&gt;] |  | [{"operand":"Vb","when":{"dt1":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |  |  |
| vmls_lane |  | Vmla |  | ["Vd"] | ["Va","Vb"] |  | mls &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt0&gt;, &lt;Vb&gt;.&lt;dt1&gt;[&lt;index&gt;] |  | [{"operand":"Vb","when":{"dt1":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |  |  |
| vumull_lane |  | Vmull |  |  | ["Va","Vb"] | ["Vd"] | umull &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] |  | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |  |  |
| vumull2_lane |  | Vmull |  |  | ["Va","Vb"] | ["Vd"] | umull2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] |  | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |  |  |
| vsmull_lane |  | Vmull |  |  | ["Va","Vb"] | ["Vd"] | smull &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] |  | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |  |  |
| vsmull2_lane |  | Vmull |  |  | ["Va","Vb"] | ["Vd"] | smull2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] |  | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |  |  |
| vumlal_lane |  | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | umlal &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] |  | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |  |  |
| vumlal2_lane |  | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | umlal2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] |  | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |  |  |
| vsmlal_lane |  | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | smlal &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] |  | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |  |  |
| vsmlal2_lane |  | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | smlal2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] |  | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |  |  |
| vumlsl_lane |  | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | umlsl &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] |  | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |  |  |
| vumlsl2_lane |  | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | umlsl2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] |  | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |  |  |
| vsmlsl_lane |  | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | smlsl &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] |  | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |  |  |
| vsmlsl2_lane |  | Vmlal |  | ["Vd"] | ["Va","Vb"] |  | smlsl2 &lt;Vd&gt;.&lt;dt0&gt;, &lt;Va&gt;.&lt;dt1&gt;, &lt;Vb&gt;.&lt;dt2&gt;[&lt;index&gt;] |  | [{"operand":"Vb","when":{"dt2":["h"]},"registers":{"prefix":"v","first":0,"last":15}}] | ["FEAT_AdvSIMD"] |  |  |
| nop |  | AArch64Instruction |  |  |  |  | nop |  |  | [] |  |  |
| umov_d |  | VecToGprMov |  |  | ["Va"] | ["Xd"] | umov &lt;Xd&gt;, &lt;Va&gt;.d[&lt;index&gt;] |  |  | ["FEAT_AdvSIMD"] |  |  |
| mov_d |  | VecToGprMov |  |  | ["Va"] | ["Xd"] | mov &lt;Xd&gt;, &lt;Va&gt;.d[&lt;index&gt;] |  |  | ["FEAT_AdvSIMD"] |  |  |
| fmov_s_form |  | Fmov |  |  | ["Sa"] | ["Wd"] | fmov &lt;Wd&gt;, &lt;Sa&gt; |  |  | ["FEAT_FP"] |  |  |
| fmov_d_form |  | Fmov |  |  | ["Da"] | ["Xd"] | fmov &lt;Xd&gt;, &lt;Da&gt; |  |  | ["FEAT_FP"] |  |  |
| fmov_0 |  | Fmov |  | ["Dd"] | ["Xa"] |  | fmov &lt;Dd&gt;, &lt;Xa&gt; |  |  | ["FEAT_FP"] |  |  |
| fmov_1 |  | Fmov |  | ["Vd"] | ["Xa"] |  | fmov &lt;Vd&gt;.d[1], &lt;Xa&gt; |  |  | ["FEAT_FP"] |  |  |
| trn1 |  | Transpose |  |  | ["Va","Vb"] | ["Vd"] | trn1 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| trn2 |  | Transpose |  |  | ["Va","Vb"] | ["Vd"] | trn2 &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| aesr |  | AESInstruction |  | ["Vd"] | ["Va"] |  | aesr &lt;Vd&gt;.16b, &lt;Va&gt;.16b |  |  | ["FEAT_AES"] |  |  |
| aesr_x2 |  | AArch64Instruction |  | ["Vd0","Vd1"] | ["Va"] |  | aesr_x2 &lt;Vd0&gt;.16b, &lt;Vd1&gt;.16b, &lt;Va&gt;.16b |  |  | ["FEAT_AES"] |  |  |
| aesr_x4 |  | AArch64Instruction |  | ["Vd0","Vd1","Vd2","Vd3"] | ["Va"] |  | aesr_x4 &lt;Vd0&gt;.16b, &lt;Vd1&gt;.16b, &lt;Vd2&gt;.16b, &lt;Vd3&gt;.16b, &lt;Va&gt;.16b |  |  | ["FEAT_AES"] |  |  |
| aese_x4 |  | AArch64Instruction |  | ["Vd0","Vd1","Vd2","Vd3"] | ["Va"] |  | aese_x4 &lt;Vd0&gt;.16b, &lt;Vd1&gt;.16b, &lt;Vd2&gt;.16b, &lt;Vd3&gt;.16b, &lt;Va&gt;.16b |  |  | ["FEAT_AES"] |  |  |
| aesdr |  | AESInstruction |  | ["Vd"] | ["Va"] |  | aesdr &lt;Vd&gt;.16b, &lt;Va&gt;.16b |  |  | ["FEAT_AES"] |  |  |
| aese |  | AESInstruction |  | ["Vd"] | ["Va"] |  | aese &lt;Vd&gt;.16b, &lt;Va&gt;.16b |  |  | ["FEAT_AES"] |  |  |
| aesmc |  | AESInstruction |  |  | ["Va"] | ["Vd"] | aesmc &lt;Vd&gt;.16b, &lt;Va&gt;.16b |  |  | ["FEAT_AES"] |  |  |
| aesd |  | AESInstruction |  | ["Vd"] | ["Va"] |  | aesd &lt;Vd&gt;.16b, &lt;Va&gt;.16b |  |  | ["FEAT_AES"] |  |  |
| aesimc |  | AESInstruction |  |  | ["Va"] | ["Vd"] | aesimc &lt;Vd&gt;.16b, &lt;Va&gt;.16b |  |  | ["FEAT_AES"] |  |  |
| pmull1_q |  | AESInstruction |  |  | ["Va","Vb"] | ["Vd"] | pmull &lt;Vd&gt;.1q, &lt;Va&gt;.1d, &lt;Vb&gt;.1d |  |  | ["FEAT_PMULL"] |  |  |
| pmull2_q |  | AESInstruction |  |  | ["Va","Vb"] | ["Vd"] | pmull2 &lt;Vd&gt;.1q, &lt;Va&gt;.2d, &lt;Vb&gt;.2d |  |  | ["FEAT_PMULL"] |  |  |
| cmge |  | ASimdCompare |  |  | ["Va","Vb"] | ["Vd"] | cmge &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| cmhi |  | ASimdCompare |  |  | ["Va","Vb"] | ["Vd"] | cmhi &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| cmeq |  | ASimdCompare |  |  | ["Va","Vb"] | ["Vd"] | cmeq &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| cmgt |  | ASimdCompare |  |  | ["Va","Vb"] | ["Vd"] | cmgt &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| cmhs |  | ASimdCompare |  |  | ["Va","Vb"] | ["Vd"] | cmhs &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;Vb&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| cmle |  | ASimdCompare |  |  | ["Va"] | ["Vd"] | cmle &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| cmlt |  | ASimdCompare |  |  | ["Va"] | ["Vd"] | cmlt &lt;Vd&gt;.&lt;dt&gt;, &lt;Va&gt;.&lt;dt&gt;, &lt;imm&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| vuaddlv_sform |  | AArch64Instruction |  |  | ["Va"] | ["Sd"] | uaddlv &lt;Sd&gt;, &lt;Va&gt;.&lt;dt&gt; |  |  | ["FEAT_AdvSIMD"] |  |  |
| q_ldr | {"type":"inputs","index":0} | Ldr_Q |  |  | ["Xc"] | ["Qa"] | ldr &lt;Qa&gt;, [&lt;Xc&gt;] |  |  | ["FEAT_FP"] |  |  |
| q_ld1 | {"type":"inputs","index":0} | Ldr_Q |  |  | ["Xc"] | ["Va"] | ld1 {&lt;Va&gt;.&lt;dt&gt;}, [&lt;Xc&gt;] |  |  | ["FEAT_AdvSIMD"] |  |  |
| prefetch | {"type":"inputs","index":0} | Ldr_Q |  |  | ["Xc"] |  | prfm pld1lkeep, [&lt;Xc&gt;, &lt;imm&gt;] | true |  | [] |  |  |
| q_ldr_with_imm_hint | {"type":"inputs","index":0} | Ldr_Q |  |  | ["Xc","Th"] | ["Qa"] | ldrh &lt;Qa&gt;, &lt;Xc&gt;, &lt;imm&gt;, &lt;Th&gt; | true |  | ["FEAT_FP"] | true |  |
| b_ldr_stack_with_inc | {"type":"literal","value":"sp"} | AArch64Instruction |  |  |  | ["Ba"] | ldr &lt;Ba&gt;, [sp, &lt;imm&gt;] | true |  | ["FEAT_FP"] | true |  |
| q_ldr1_stack | {"type":"literal","value":"sp"} | Ldr_Q |  |  |  | ["Va"] | ld1r {&lt;Va&gt;.&lt;dt&gt;}, [sp] |  |  | ["FEAT_AdvSIMD"] |  |  |
| q_ldr1_post_inc | {"type":"in_outs","index":0} | Ldr_Q |  | ["Xa"] |  | ["Va"] | ld1r {&lt;Va&gt;.&lt;dt&gt;}, [&lt;Xa&gt;], &lt;imm&gt; |  |  | ["FEAT_AdvSIMD"] |  | true |
| q_ldr_stack_with_inc | {"type":"literal","value":"sp"} | Ldr_Q |  |  |  | ["Qa"] | ldr &lt;Qa&gt;, [sp, &lt;imm&gt;] | true |  | ["FEAT_FP"] | true |  |
| q_ldr_with_inc | {"type":"inputs","index":0} | Ldr_Q |  |  | ["Xc"] | ["Qa"] | ldr &lt;Qa&gt;, [&lt;Xc&gt;, &lt;imm&gt;] | true |  | ["FEAT_FP"] | true |  |
| q_ld1_with_inc | {"type":"inputs","index":0} | Ldr_Q |  |  | ["Xc"] | ["Va"] | ld1 {&lt;Va&gt;.&lt;dt&gt;}, [&lt;Xc&gt;, &lt;imm&gt;] | true |  | ["FEAT_AdvSIMD"] | true |  |
| q_ldp_with_inc | {"type":"inputs","index":0} | Ldp_Q |  |  | ["Xc"] | ["Qa","Qb"] | ldp &lt;Qa&gt;, &lt;Qb&gt;, [&lt;Xc&gt;, &lt;imm&gt;] | true |  | ["FEAT_FP"] | true |  |
| q_ldr_with_inc_writeback | {"type":"in_outs","index":0} | Ldr_Q |  | ["Xc"] |  | ["Qa"] | ldr &lt;Qa&gt;, [&lt;Xc&gt;, &lt;imm&gt;]! |  |  | ["FEAT_FP"] |  | true |
| q_ldr_with_postinc | {"type":"in_outs","index":0} | Ldr_Q |  | ["Xc"] |  | ["Qa"] | ldr &lt;Qa&gt;, [&lt;Xc&gt;], &lt;imm&gt; |  |  | ["FEAT_FP"] |  | true |
| q_ld1_with_postinc | {"type":"in_outs","index":0} | Ldr_Q |  | ["Xc"] |  | ["Va"] | ld1 {&lt;Va&gt;.&lt;dt&gt;}, [&lt;Xc&gt;], &lt;imm&gt; |  |  | ["FEAT_AdvSIMD"] |  | true |
| q_ldp_with_postinc | {"type":"in_outs","index":0} | Ldp_Q |  | ["Xc"] |  | ["Qa","Qb"] | ldp &lt;Qa&gt;, &lt;Qb&gt;, [&lt;Xc&gt;], &lt;imm&gt; |  |  | ["FEAT_FP"] |  | true |
| q_str | {"type":"inputs","index":1} | Str_Q |  |  | ["Qa","Xc"] |  | str &lt;Qa&gt;, [&lt;Xc&gt;] |  |  | ["FEAT_FP"] |  |  |
| q_str_with_imm_hint | {"type":"inputs","index":1} | Str_Q |  |  | ["Qa","Xc"] | ["Th"] | strh &lt;Qa&gt;, &lt;Xc&gt;, &lt;imm&gt;, &lt;Th&gt; | true |  | ["FEAT_FP"] | true |  |
| q_str_with_inc | {"type":"inputs","index":1} | Str_Q |  |  | ["Qa","Xc"] |  | str &lt;Qa&gt;, [&lt;Xc&gt;, &lt;imm&gt;] | true |  | ["FEAT_FP"] | true |  |
| q_str_stack_with_inc | {"type":"literal","value":"sp"} | Str_Q |  |  | ["Qa"] |  | str &lt;Qa&gt;, [sp, &lt;imm&gt;] | true |  | ["FEAT_FP"] | true |  |
| q_stp_stack_with_inc | {"type":"literal","value":"sp"} | AArch64Instruction |  |  | ["Qa","Qb"] |  | stp &lt;Qa&gt;, &lt;Qb&gt;, [sp, &lt;imm&gt;] | true |  | ["FEAT_FP"] | true |  |
| q_stp_with_inc | {"type":"inputs","index":2} | Stp_Q |  |  | ["Qa","Qb","Xc"] |  | stp &lt;Qa&gt;, &lt;Qb&gt;, [&lt;Xc&gt;, &lt;imm&gt;] | true |  | ["FEAT_FP"] | true |  |
| q_str_with_inc_writeback | {"type":"in_outs","index":0} | Str_Q |  | ["Xc"] | ["Qa"] |  | str &lt;Qa&gt;, [&lt;Xc&gt;, &lt;imm&gt;]! |  |  | ["FEAT_FP"] |  | true |
| q_str_with_postinc | {"type":"in_outs","index":0} | Str_Q |  | ["Xc"] | ["Qa"] |  | str &lt;Qa&gt;, [&lt;Xc&gt;], &lt;imm&gt; |  |  | ["FEAT_FP"] |  | true |
| q_st1_with_postinc | {"type":"in_outs","index":0} | Str_Q |  | ["Xc"] | ["Va"] |  | st1 {&lt;Va&gt;.&lt;dt&gt;}, [&lt;Xc&gt;], &lt;imm&gt; |  |  | ["FEAT_AdvSIMD"] |  | true |
| q_st1_lane_with_postinc | {"type":"in_outs","index":0} | Str_Q |  | ["Xc"] | ["Va"] |  | st1 {&lt;Va&gt;.&lt;dt&gt;}[&lt;index&gt;], [&lt;Xc&gt;], &lt;imm&gt; |  |  | ["FEAT_AdvSIMD"] |  | true |
| q_stp_with_postinc | {"type":"in_outs","index":0} | Stp_Q |  | ["Xc"] | ["Qa","Qb"] |  | stp &lt;Qa&gt;, &lt;Qb&gt;, [&lt;Xc&gt;], &lt;imm&gt; |  |  | ["FEAT_FP"] |  | true |
