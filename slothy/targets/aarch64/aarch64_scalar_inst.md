# AArch64 scalar instruction table

**Generated file — do not edit.**
Edit [aarch64_scalar_instructions.json](aarch64_scalar_instructions.json) instead; JSON is the source of truth.
Regenerate both tables from the repository root with:

```sh
python3 slothy/targets/aarch64/dump_instruction_tables.py
```

Only explicit JSON fields are shown; blank cells may inherit from the base.
This is not a complete ISA or CPU timing reference. See
[the specification guide](README.instructions.md) for scope and semantics.

| name | addr_source | base | dependsOnFlags | in_outs | inputs | modifiesFlags | outputs | pattern | pre_index_from_immediate | restore_immediate_from_pre_index | set_increment_from_immediate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s_ldr | {"type":"inputs","index":0} | Ldr_S |  |  | ["Xc"] |  | ["Sa"] | ldr &lt;Sa&gt;, [&lt;Xc&gt;] |  |  |  |
| s_ldr_with_inc | {"type":"inputs","index":0} | Ldr_S |  |  | ["Xc"] |  | ["Sa"] | ldr &lt;Sa&gt;, [&lt;Xc&gt;, &lt;imm&gt;] | True | True |  |
| s_ldr_with_inc_writeback | {"type":"in_outs","index":0} | Ldr_S |  | ["Xc"] |  |  | ["Sa"] | ldr &lt;Sa&gt;, [&lt;Xc&gt;, &lt;imm&gt;]! |  |  | True |
| s_ldr_with_postinc | {"type":"in_outs","index":0} | Ldr_S |  | ["Xc"] |  |  | ["Sa"] | ldr &lt;Sa&gt;, [&lt;Xc&gt;], &lt;imm&gt; |  |  | True |
| s_str | {"type":"inputs","index":1} | Str_S |  |  | ["Sa","Xc"] |  |  | str &lt;Sa&gt;, [&lt;Xc&gt;] |  |  |  |
| s_str_with_inc | {"type":"inputs","index":1} | Str_S |  |  | ["Sa","Xc"] |  |  | str &lt;Sa&gt;, [&lt;Xc&gt;, &lt;imm&gt;] | True | True |  |
| s_str_with_inc_writeback | {"type":"in_outs","index":0} | Str_S |  | ["Xc"] | ["Sa"] |  |  | str &lt;Sa&gt;, [&lt;Xc&gt;, &lt;imm&gt;]! |  |  | True |
| s_str_with_postinc | {"type":"in_outs","index":0} | Str_S |  | ["Xc"] | ["Sa"] |  |  | str &lt;Sa&gt;, [&lt;Xc&gt;], &lt;imm&gt; |  |  | True |
| s_ldp | {"type":"inputs","index":0} | Ldp_S |  |  | ["Xc"] |  | ["Sa","Sb"] | ldp &lt;Sa&gt;, &lt;Sb&gt;, [&lt;Xc&gt;] |  |  |  |
| s_ldp_with_inc | {"type":"inputs","index":0} | Ldp_S |  |  | ["Xc"] |  | ["Sa","Sb"] | ldp &lt;Sa&gt;, &lt;Sb&gt;, [&lt;Xc&gt;, &lt;imm&gt;] | True | True |  |
| s_ldp_with_inc_writeback | {"type":"in_outs","index":0} | Ldp_S |  | ["Xc"] |  |  | ["Sa","Sb"] | ldp &lt;Sa&gt;, &lt;Sb&gt;, [&lt;Xc&gt;, &lt;imm&gt;]! |  |  | True |
| s_ldp_with_postinc | {"type":"in_outs","index":0} | Ldp_S |  | ["Xc"] |  |  | ["Sa","Sb"] | ldp &lt;Sa&gt;, &lt;Sb&gt;, [&lt;Xc&gt;], &lt;imm&gt; |  |  | True |
| s_stp | {"type":"inputs","index":2} | Stp_S |  |  | ["Sa","Sb","Xc"] |  |  | stp &lt;Sa&gt;, &lt;Sb&gt;, [&lt;Xc&gt;] |  |  |  |
| s_stp_with_inc | {"type":"inputs","index":2} | Stp_S |  |  | ["Sa","Sb","Xc"] |  |  | stp &lt;Sa&gt;, &lt;Sb&gt;, [&lt;Xc&gt;, &lt;imm&gt;] | True | True |  |
| s_stp_with_inc_writeback | {"type":"in_outs","index":0} | Stp_S |  | ["Xc"] | ["Sa","Sb"] |  |  | stp &lt;Sa&gt;, &lt;Sb&gt;, [&lt;Xc&gt;, &lt;imm&gt;]! |  |  | True |
| s_stp_with_postinc | {"type":"in_outs","index":0} | Stp_S |  | ["Xc"] | ["Sa","Sb"] |  |  | stp &lt;Sa&gt;, &lt;Sb&gt;, [&lt;Xc&gt;], &lt;imm&gt; |  |  | True |
| sfmadd |  | Sfma |  |  | ["Sb","Sc","Sd"] |  | ["Sa"] | fmadd &lt;Sa&gt;, &lt;Sb&gt;, &lt;Sc&gt;, &lt;Sd&gt; |  |  |  |
| sfmsub |  | Sfma |  |  | ["Sb","Sc","Sd"] |  | ["Sa"] | fmsub &lt;Sa&gt;, &lt;Sb&gt;, &lt;Sc&gt;, &lt;Sd&gt; |  |  |  |
| sfnmadd |  | Sfma |  |  | ["Sb","Sc","Sd"] |  | ["Sa"] | fnmadd &lt;Sa&gt;, &lt;Sb&gt;, &lt;Sc&gt;, &lt;Sd&gt; |  |  |  |
| sfnmsub |  | Sfma |  |  | ["Sb","Sc","Sd"] |  | ["Sa"] | fnmsub &lt;Sa&gt;, &lt;Sb&gt;, &lt;Sc&gt;, &lt;Sd&gt; |  |  |  |
| sfmul |  | Smul |  |  | ["Sb","Sc"] |  | ["Sa"] | fmul &lt;Sa&gt;, &lt;Sb&gt;, &lt;Sc&gt; |  |  |  |
| sfnmul |  | Smul |  |  | ["Sb","Sc"] |  | ["Sa"] | fnmul &lt;Sa&gt;, &lt;Sb&gt;, &lt;Sc&gt; |  |  |  |
| d_ldr | {"type":"inputs","index":0} | Ldr_D |  |  | ["Xc"] |  | ["Da"] | ldr &lt;Da&gt;, [&lt;Xc&gt;] |  |  |  |
| d_ldr_with_postinc | {"type":"in_outs","index":0} | Ldr_D |  | ["Xc"] |  |  | ["Da"] | ldr &lt;Da&gt;, [&lt;Xc&gt;], &lt;imm&gt; |  |  | True |
| d_ldr_with_inc_writeback | {"type":"in_outs","index":0} | Ldr_D |  | ["Xc"] |  |  | ["Da"] | ldr &lt;Da&gt;, [&lt;Xc&gt;, &lt;imm&gt;]! |  |  | True |
| d_ldp_sp_imm | {"type":"literal","value":"sp"} | Ldr_Q |  |  |  |  | ["Da","Db"] | ldp &lt;Da&gt;, &lt;Db&gt;, [sp, &lt;imm&gt;] | True | True |  |
| d_ldr_stack_with_inc | {"type":"literal","value":"sp"} | Ldr_D |  |  |  |  | ["Da"] | ldr &lt;Da&gt;, [sp, &lt;imm&gt;] | True | True |  |
| d_str_stack_with_inc | {"type":"literal","value":"sp"} | AArch64Instruction |  |  | ["Da"] |  |  | str &lt;Da&gt;, [sp, &lt;imm&gt;] | True | True |  |
| d_stp_stack_with_inc | {"type":"literal","value":"sp"} | AArch64Instruction |  |  | ["Da","Db"] |  |  | stp &lt;Da&gt;, &lt;Db&gt;, [sp, &lt;imm&gt;] | True | True |  |
| x_ldr | {"type":"inputs","index":0} | Ldr_X |  |  | ["Xc"] |  | ["Xa"] | ldr &lt;Xa&gt;, [&lt;Xc&gt;] |  |  |  |
| x_ldr_with_imm | {"type":"inputs","index":0} | Ldr_X |  |  | ["Xc"] |  | ["Xa"] | ldr &lt;Xa&gt;, [&lt;Xc&gt;, &lt;imm&gt;] | True | True |  |
| x_ldr_with_imm_uxtw | {"type":"inputs","index":0} | Ldr_X |  |  | ["Xa","Xb"] |  | ["Xd"] | ldr &lt;Xd&gt;, [&lt;Xa&gt;, &lt;Xb&gt;, UXTW &lt;imm&gt;] | True | True |  |
| x_ldr_with_imm_shifted | {"type":"inputs","index":0} | Ldr_X |  |  | ["Xa","Xb"] |  | ["Xd"] | ldr &lt;Xd&gt;, [&lt;Xa&gt;, &lt;Xb&gt;, &lt;barrel&gt; &lt;imm&gt;] | True | True |  |
| x_ldr_regidx | {"type":"inputs","index":0} | Ldr_X |  |  | ["Xb","Xc"] |  | ["Xa"] | ldr &lt;Xa&gt;, [&lt;Xb&gt;, &lt;Xc&gt;] |  |  |  |
| x_ldr_with_postinc | {"type":"in_outs","index":0} | Ldr_X |  | ["Xc"] |  |  | ["Xa"] | ldr &lt;Xa&gt;, [&lt;Xc&gt;], &lt;imm&gt; |  |  | True |
| x_ldr_stack | {"type":"literal","value":"sp"} | Ldr_X |  |  |  |  | ["Xa"] | ldr &lt;Xa&gt;, [sp] |  |  |  |
| x_ldr_stack_imm | {"type":"literal","value":"sp"} | Ldr_X |  |  |  |  | ["Xa"] | ldr &lt;Xa&gt;, [sp, &lt;imm&gt;] | True | True |  |
| x_ldr_stack_imm_with_hint | {"type":"literal","value":"sp"} | Ldr_X |  |  | ["Th"] |  | ["Xa"] | ldrh &lt;Xa&gt;, sp, &lt;imm&gt;, &lt;Th&gt; | True | True |  |
| x_ldr_imm_with_hint | {"type":"inputs","index":0} | Ldr_X |  |  | ["Xb","Th"] |  | ["Xa"] | ldrh &lt;Xa&gt;, &lt;Xb&gt;, &lt;imm&gt;, &lt;Th&gt; | True | True |  |
| x_ldp | {"type":"inputs","index":0} | Ldp_X |  |  | ["Xc"] |  | ["Xa","Xb"] | ldp &lt;Xa&gt;, &lt;Xb&gt;, [&lt;Xc&gt;] |  |  |  |
| x_ldp_with_imm_sp_xzr | {"type":"literal","value":"sp"} | Ldp_X |  |  |  |  | ["Xa"] | ldp &lt;Xa&gt;, xzr, [sp, &lt;imm&gt;] | True | True |  |
| x_ldp_with_imm_sp | {"type":"literal","value":"sp"} | Ldp_X |  |  |  |  | ["Xa","Xb"] | ldp &lt;Xa&gt;, &lt;Xb&gt;, [sp, &lt;imm&gt;] | True | True |  |
| x_ldp_with_sp | {"type":"literal","value":"sp"} | Ldp_X |  |  |  |  | ["Xa","Xb"] | ldp &lt;Xa&gt;, &lt;Xb&gt;, [sp] |  |  |  |
| x_ldp_with_inc | {"type":"inputs","index":0} | Ldp_X |  |  | ["Xc"] |  | ["Xa","Xb"] | ldp &lt;Xa&gt;, &lt;Xb&gt;, [&lt;Xc&gt;, &lt;imm&gt;] | True | True |  |
| x_ldp_with_inc_writeback | {"type":"in_outs","index":0} | Ldp_X |  | ["Xc"] |  |  | ["Xa","Xb"] | ldp &lt;Xa&gt;, &lt;Xb&gt;, [&lt;Xc&gt;, &lt;imm&gt;]! |  |  | True |
| x_ldp_with_postinc_writeback | {"type":"in_outs","index":0} | Ldp_X |  | ["Xc"] |  |  | ["Xa","Xb"] | ldp &lt;Xa&gt;, &lt;Xb&gt;, [&lt;Xc&gt;], &lt;imm&gt; |  |  | True |
| x_ldp_with_imm_hint | {"type":"inputs","index":0} | Ldp_X |  |  | ["Xc","Th"] |  | ["Xa","Xb"] | ldph &lt;Xa&gt;, &lt;Xb&gt;, &lt;Xc&gt;, &lt;imm&gt;, &lt;Th&gt; | True | True |  |
| x_ldp_sp_with_imm_hint | {"type":"literal","value":"sp"} | Ldp_X |  |  | ["Th"] |  | ["Xa","Xb"] | ldph &lt;Xa&gt;, &lt;Xb&gt;, sp, &lt;imm&gt;, &lt;Th&gt; | True | True |  |
| x_ldp_sp_with_imm_hint2 | {"type":"literal","value":"sp"} | Ldp_X |  |  | ["Th0","Th1"] |  | ["Xa","Xb"] | ldphp &lt;Xa&gt;, &lt;Xb&gt;, sp, &lt;imm&gt;, &lt;Th0&gt;, &lt;Th1&gt; | True | True |  |
| x_ldp_with_imm_hint2 | {"type":"inputs","index":0} | Ldp_X |  |  | ["Xc","Th0","Th1"] |  | ["Xa","Xb"] | ldphp &lt;Xa&gt;, &lt;Xb&gt;, &lt;Xc&gt;, &lt;imm&gt;, &lt;Th0&gt;, &lt;Th1&gt; | True | True |  |
| ldr_sxtw_wform | {"type":"inputs","index":0} | AArch64Instruction |  |  | ["Xa","Wb"] |  | ["Wd"] | ldr &lt;Wd&gt;, [&lt;Xa&gt;, &lt;Wb&gt;, SXTW &lt;imm&gt;] |  |  |  |
| lsr_wform |  | AArch64Instruction |  |  | ["Wa","Wb"] |  | ["Wd"] | lsr &lt;Wd&gt;, &lt;Wa&gt;, &lt;Wb&gt; |  |  |  |
| asr_wform |  | AArch64Instruction |  |  | ["Wa"] |  | ["Wd"] | asr &lt;Wd&gt;, &lt;Wa&gt;, &lt;imm&gt; |  |  |  |
| subs_wform |  | AArch64BasicArithmetic |  |  | ["Wa"] | True | ["Wd"] | subs &lt;Wd&gt;, &lt;Wa&gt;, &lt;imm&gt; |  |  |  |
| subs_imm |  | AArch64BasicArithmetic |  |  | ["Xa"] | True | ["Xd"] | subs &lt;Xd&gt;, &lt;Xa&gt;, &lt;imm&gt; |  |  |  |
| sub_imm |  | AArch64BasicArithmetic |  |  | ["Xa"] |  | ["Xd"] | sub &lt;Xd&gt;, &lt;Xa&gt;, &lt;imm&gt; |  |  |  |
| add_imm |  | AArch64BasicArithmetic |  |  | ["Xa"] |  | ["Xd"] | add &lt;Xd&gt;, &lt;Xa&gt;, &lt;imm&gt; |  |  |  |
| add_sp_imm |  | AArch64BasicArithmetic |  |  |  |  | ["Xd"] | add &lt;Xd&gt;, sp, &lt;imm&gt; |  |  |  |
| neg |  | AArch64BasicArithmetic |  |  | ["Xa"] |  | ["Xd"] | neg &lt;Xd&gt;, &lt;Xa&gt; |  |  |  |
| negs |  | AArch64BasicArithmetic |  |  | ["Xa"] | True | ["Xd"] | negs &lt;Xd&gt;, &lt;Xa&gt; |  |  |  |
| ngc_zero |  | AArch64BasicArithmetic | True |  | [] |  | ["Xd"] | ngc &lt;Xd&gt;, xzr |  |  |  |
| ngcs |  | AArch64BasicArithmetic | True |  | ["Xa"] | True | ["Xd"] | ngcs &lt;Xd&gt;, &lt;Xa&gt; |  |  |  |
| ngcs_zero |  | AArch64BasicArithmetic | True |  | [] | True | ["Xd"] | ngcs &lt;Xd&gt;, xzr |  |  |  |
| adds |  | AArch64BasicArithmetic |  |  | ["Xa"] | True | ["Xd"] | adds &lt;Xd&gt;, &lt;Xa&gt;, &lt;imm&gt; |  |  |  |
| adds_to_zero |  | AArch64BasicArithmetic |  |  | ["Xa","Xb"] | True | [] | adds xzr, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| adds_imm_to_zero |  | AArch64BasicArithmetic |  |  | ["Xa"] | True | [] | adds xzr, &lt;Xa&gt;, &lt;imm&gt; |  |  |  |
| subs_twoarg |  | AArch64BasicArithmetic |  |  | ["Xa","Xb"] | True | ["Xd"] | subs &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| adds_twoarg |  | AArch64BasicArithmetic |  |  | ["Xa","Xb"] | True | ["Xd"] | adds &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| adcs |  | AArch64BasicArithmetic | True |  | ["Xa","Xb"] | True | ["Xd"] | adcs &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| sbcs |  | AArch64BasicArithmetic | True |  | ["Xa","Xb"] | True | ["Xd"] | sbcs &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| sbcs_zero |  | AArch64BasicArithmetic | True |  | ["Xa"] | True | ["Xd"] | sbcs &lt;Xd&gt;, &lt;Xa&gt;, xzr |  |  |  |
| sbcs_to_zero |  | AArch64BasicArithmetic | True |  | ["Xa","Xb"] | True | [] | sbcs xzr, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| sbcs_zero_to_zero |  | AArch64BasicArithmetic | True |  | ["Xa"] | True | [] | sbcs xzr, &lt;Xa&gt;, xzr |  |  |  |
| sbc |  | AArch64BasicArithmetic | True |  | ["Xa","Xb"] |  | ["Xd"] | sbc &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| sbc_zero_r |  | AArch64BasicArithmetic | True |  | ["Xa"] |  | ["Xd"] | sbc &lt;Xd&gt;, &lt;Xa&gt;, xzr |  |  |  |
| adcs_zero_r |  | AArch64BasicArithmetic | True |  | ["Xa"] | True | ["Xd"] | adcs &lt;Xd&gt;, &lt;Xa&gt;, xzr |  |  |  |
| adcs_zero_l |  | AArch64BasicArithmetic | True |  | ["Xb"] | True | ["Xd"] | adcs &lt;Xd&gt;, xzr, &lt;Xb&gt; |  |  |  |
| adcs_zero2 |  | AArch64BasicArithmetic | True |  | [] | True | ["Xd"] | adcs &lt;Xd&gt;, xzr, xzr |  |  |  |
| adcs_to_zero |  | AArch64BasicArithmetic | True |  | ["Xa","Xb"] | True | [] | adcs xzr, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| adcs_zero_r_to_zero |  | AArch64BasicArithmetic | True |  | ["Xa"] | True | [] | adcs xzr, &lt;Xa&gt;, xzr |  |  |  |
| adc |  | AArch64BasicArithmetic | True |  | ["Xa","Xb"] |  | ["Xd"] | adc &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| adc_zero2 |  | AArch64BasicArithmetic | True |  | [] |  | ["Xd"] | adc &lt;Xd&gt;, xzr, xzr |  |  |  |
| adc_zero_r |  | AArch64BasicArithmetic | True |  | ["Xa"] |  | ["Xd"] | adc &lt;Xd&gt;, &lt;Xa&gt;, xzr |  |  |  |
| adc_zero_l |  | AArch64BasicArithmetic | True |  | ["Xa"] |  | ["Xd"] | adc &lt;Xd&gt;, xzr, &lt;Xa&gt; |  |  |  |
| add |  | AArch64BasicArithmetic |  |  | ["Xa","Xb"] |  | ["Xd"] | add &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| add2 |  | AArch64BasicArithmetic |  |  | ["Xa","Xb"] |  | ["Xd"] | add &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt;, &lt;imm&gt; |  |  |  |
| add_w_imm |  | AArch64BasicArithmetic |  |  | ["Wa"] |  | ["Wd"] | add &lt;Wd&gt;, &lt;Wa&gt;, &lt;imm&gt; |  |  |  |
| sub |  | AArch64BasicArithmetic |  |  | ["Xa","Xb"] |  | ["Xd"] | sub &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| eor_shifted |  | AArch64ShiftedArithmetic |  |  | ["Xa","Xb"] |  | ["Xd"] | eor &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt;, &lt;barrel&gt; &lt;imm&gt; |  |  |  |
| bic_shifted |  | AArch64ShiftedArithmetic |  |  | ["Xa","Xb"] |  | ["Xd"] | bic &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt;, &lt;barrel&gt; &lt;imm&gt; |  |  |  |
| add_shifted |  | AArch64ShiftedArithmetic |  |  | ["Xa","Xb"] |  | ["Xd"] | add &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt;, &lt;barrel&gt; &lt;imm&gt; |  |  |  |
| adds_shifted |  | AArch64ShiftedArithmetic |  |  | ["Xa","Xb"] | True | ["Xd"] | adds &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt;, &lt;barrel&gt; &lt;imm&gt; |  |  |  |
| add_imm_shifted |  | AArch64ShiftedArithmetic |  |  | ["Xa"] |  | ["Xd"] | add &lt;Xd&gt;, &lt;Xa&gt;, &lt;imm0&gt;, &lt;barrel&gt; &lt;imm1&gt; |  |  |  |
| lsr_imm |  | AArch64Shift |  |  | ["Xa"] |  | ["Xd"] | lsr &lt;Xd&gt;, &lt;Xa&gt;, &lt;imm&gt; |  |  |  |
| lsr |  | AArch64Shift |  |  | ["Xa","Xc"] |  | ["Xd"] | lsr &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xc&gt; |  |  |  |
| lsl |  | AArch64Shift |  |  | ["Xa"] |  | ["Xd"] | lsl &lt;Xd&gt;, &lt;Xa&gt;, &lt;imm&gt; |  |  |  |
| ror |  | AArch64Shift |  |  | ["Xa"] |  | ["Xd"] | ror &lt;Xd&gt;, &lt;Xa&gt;, &lt;imm&gt; |  |  |  |
| asr_imm |  | AArch64Shift |  |  | ["Xa"] |  | ["Xd"] | asr &lt;Xd&gt;, &lt;Xa&gt;, &lt;imm&gt; |  |  |  |
| rev_w |  | AArch64Logical |  |  | ["Wa"] |  | ["Wd"] | rev &lt;Wd&gt;, &lt;Wa&gt; |  |  |  |
| eor_wform |  | AArch64Logical |  |  | ["Wa","Wb"] |  | ["Wd"] | eor &lt;Wd&gt;, &lt;Wa&gt;, &lt;Wb&gt; |  |  |  |
| eon_wform |  | AArch64Logical |  |  | ["Wa","Wb"] |  | ["Wd"] | eon &lt;Wd&gt;, &lt;Wa&gt;, &lt;Wb&gt; |  |  |  |
| eor |  | AArch64Logical |  |  | ["Xa","Xb"] |  | ["Xd"] | eor &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| eon |  | AArch64Logical |  |  | ["Xa","Xb"] |  | ["Xd"] | eon &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| orr |  | AArch64Logical |  |  | ["Xa","Xb"] |  | ["Xd"] | orr &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| orr_w |  | AArch64Logical |  |  | ["Wa","Wb"] |  | ["Wd"] | orr &lt;Wd&gt;, &lt;Wa&gt;, &lt;Wb&gt; |  |  |  |
| bfi |  | AArch64Logical |  | ["Xd"] | ["Xa"] |  |  | bfi &lt;Xd&gt;, &lt;Xa&gt;, &lt;imm0&gt;, &lt;imm1&gt; |  |  |  |
| and_imm |  | AArch64Logical |  |  | ["Xa"] |  | ["Xd"] | and &lt;Xd&gt;, &lt;Xa&gt;, &lt;imm&gt; |  |  |  |
| ands_imm |  | AArch64Logical |  |  | ["Xa"] | True | ["Xd"] | ands &lt;Xd&gt;, &lt;Xa&gt;, &lt;imm&gt; |  |  |  |
| ands_xzr_imm |  | AArch64Logical |  |  | ["Xa"] | True | [] | ands xzr, &lt;Xa&gt;, &lt;imm&gt; |  |  |  |
| and_twoarg |  | AArch64Logical |  |  | ["Xa","Xb"] |  | ["Xd"] | and &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| bic |  | AArch64Logical |  |  | ["Xa"] |  | ["Xd"] | bic &lt;Xd&gt;, &lt;Xa&gt;, &lt;imm&gt; |  |  |  |
| bic_reg |  | AArch64Logical |  |  | ["Xa","Xb"] |  | ["Xd"] | bic &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| orr_imm |  | AArch64Logical |  |  | ["Xa"] |  | ["Xd"] | orr &lt;Xd&gt;, &lt;Xa&gt;, &lt;imm&gt; |  |  |  |
| sbfx |  | AArch64Logical |  |  | ["Xa"] |  | ["Xd"] | sbfx &lt;Xd&gt;, &lt;Xa&gt;, &lt;imm0&gt;, &lt;imm1&gt; |  |  |  |
| ubfx |  | AArch64Logical |  |  | ["Xa"] |  | ["Xd"] | ubfx &lt;Xd&gt;, &lt;Xa&gt;, &lt;imm0&gt;, &lt;imm1&gt; |  |  |  |
| extr |  | AArch64Logical |  |  | ["Xa","Xb"] |  | ["Xd"] | extr &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt;, &lt;imm&gt; |  |  |  |
| orr_shifted |  | AArch64LogicalShifted |  |  | ["Xa","Xb"] |  | ["Xd"] | orr &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt;, &lt;barrel&gt; &lt;imm&gt; |  |  |  |
| orr_shifted_w |  | AArch64LogicalShifted |  |  | ["Wa","Wb"] |  | ["Wd"] | and &lt;Wd&gt;, &lt;Wa&gt;, &lt;Wb&gt;, &lt;barrel&gt; &lt;imm&gt; |  |  |  |
| ccmp |  | AArch64ConditionalCompare | True |  | ["Xa","Xb"] | True |  | ccmp &lt;Xa&gt;, &lt;Xb&gt;, &lt;imm&gt;, &lt;flag&gt; |  |  |  |
| ccmp_xzr |  | AArch64ConditionalCompare | True |  | ["Xa"] | True |  | ccmp xzr, &lt;Xa&gt;, &lt;imm&gt;, &lt;flag&gt; |  |  |  |
| ccmp_xzr2 |  | AArch64ConditionalCompare | True |  | ["Xa"] | True |  | ccmp &lt;Xa&gt;, xzr, &lt;imm&gt;, &lt;flag&gt; |  |  |  |
| ccmn |  | AArch64ConditionalCompare | True |  | ["Xa","Xb"] | True |  | ccmn &lt;Xa&gt;, &lt;Xb&gt;, &lt;imm&gt;, &lt;flag&gt; |  |  |  |
| ccmn_xzr |  | AArch64ConditionalCompare | True |  | ["Xa"] | True |  | ccmn xzr, &lt;Xa&gt;, &lt;imm&gt;, &lt;flag&gt; |  |  |  |
| ccmn_xzr2 |  | AArch64ConditionalCompare | True |  | ["Xa"] | True |  | ccmn &lt;Xa&gt;, xzr, &lt;imm&gt;, &lt;flag&gt; |  |  |  |
| cneg |  | AArch64ConditionalSelect | True |  | ["Xe"] |  | ["Xd"] | cneg &lt;Xd&gt;, &lt;Xe&gt;, &lt;flag&gt; |  |  |  |
| csel_xzr_ne |  | AArch64ConditionalSelect | True |  | ["Xe"] |  | ["Xd"] | csel &lt;Xd&gt;, &lt;Xe&gt;, xzr, &lt;flag&gt; |  |  |  |
| csel_xzr2_ne |  | AArch64ConditionalSelect | True |  | ["Xe"] |  | ["Xd"] | csel &lt;Xd&gt;, xzr, &lt;Xe&gt;, &lt;flag&gt; |  |  |  |
| csel |  | AArch64ConditionalSelect | True |  | ["Xe","Xf"] |  | ["Xd"] | csel &lt;Xd&gt;, &lt;Xe&gt;, &lt;Xf&gt;, &lt;flag&gt; |  |  |  |
| cinv |  | AArch64ConditionalSelect | True |  | ["Xe"] |  | ["Xd"] | cinv &lt;Xd&gt;, &lt;Xe&gt;, &lt;flag&gt; |  |  |  |
| cinc |  | AArch64ConditionalSelect | True |  | ["Xe"] |  | ["Xd"] | cinc &lt;Xd&gt;, &lt;Xe&gt;, &lt;flag&gt; |  |  |  |
| csetm |  | AArch64ConditionalSelect | True |  |  |  | ["Xd"] | csetm &lt;Xd&gt;, &lt;flag&gt; |  |  |  |
| cset |  | AArch64ConditionalSelect | True |  |  |  | ["Xd"] | cset &lt;Xd&gt;, &lt;flag&gt; |  |  |  |
| cmn |  | AArch64ConditionalSelect |  |  | ["Xd","Xe"] | True |  | cmn &lt;Xd&gt;, &lt;Xe&gt; |  |  |  |
| cmn_imm |  | AArch64ConditionalSelect |  |  | ["Xd"] | True |  | cmn &lt;Xd&gt;, &lt;imm&gt; |  |  |  |
| ldr_const |  | AArch64Instruction |  |  | [] |  | ["Xd"] | ldr &lt;Xd&gt;, &lt;literal&gt; |  |  |  |
| movk_imm |  | AArch64Instruction |  | ["Xd"] | [] |  |  | movk &lt;Xd&gt;, &lt;imm&gt; |  |  |  |
| mov |  | AArch64Instruction |  |  | ["Wa"] |  | ["Wd"] | mov &lt;Wd&gt;, &lt;Wa&gt; |  |  |  |
| movz_imm |  | AArch64Move |  |  | [] |  | ["Xd"] | movz &lt;Xd&gt;, &lt;imm&gt; |  |  |  |
| movz_imm_lsl |  | AArch64Move |  |  | [] |  | ["Xd"] | movz &lt;Xd&gt;, &lt;imm0&gt;, &lt;barrel&gt; &lt;imm1&gt; |  |  |  |
| mov_imm |  | AArch64Move |  |  | [] |  | ["Xd"] | mov &lt;Xd&gt;, &lt;imm&gt; |  |  |  |
| movw_imm |  | AArch64Move |  |  | [] |  | ["Wd"] | mov &lt;Wd&gt;, &lt;imm&gt; |  |  |  |
| mvn_xzr |  | AArch64Move |  |  | [] |  | ["Xd"] | mvn &lt;Xd&gt;, xzr |  |  |  |
| mov_xform |  | AArch64Move |  |  | ["Xa"] |  | ["Xd"] | mov &lt;Xd&gt;, &lt;Xa&gt; |  |  |  |
| umull_wform |  | AArch64Instruction |  |  | ["Wa","Wb"] |  | ["Xd"] | umull &lt;Xd&gt;, &lt;Wa&gt;, &lt;Wb&gt; |  |  |  |
| umaddl_wform |  | AArch64Instruction |  |  | ["Wa","Wb","Xacc"] |  | ["Xn"] | umaddl &lt;Xn&gt;, &lt;Wa&gt;, &lt;Wb&gt;, &lt;Xacc&gt; |  |  |  |
| mul_wform |  | AArch64Instruction |  |  | ["Wa","Wb"] |  | ["Wd"] | mul &lt;Wd&gt;, &lt;Wa&gt;, &lt;Wb&gt; |  |  |  |
| umulh_xform |  | AArch64HighMultiply |  |  | ["Xa","Xb"] |  | ["Xd"] | umulh &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| smulh_xform |  | AArch64HighMultiply |  |  | ["Xa","Xb"] |  | ["Xd"] | smulh &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| mul_xform |  | AArch64Multiply |  |  | ["Xa","Xb"] |  | ["Xd"] | mul &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| madd_xform |  | AArch64Multiply |  |  | ["Xacc","Xa","Xb"] |  | ["Xd"] | madd &lt;Xd&gt;, &lt;Xacc&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| mneg_xform |  | AArch64Multiply |  |  | ["Xa","Xb"] |  | ["Xd"] | mneg &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| msub_xform |  | AArch64Multiply |  |  | ["Xacc","Xa","Xb"] |  | ["Xd"] | msub &lt;Xd&gt;, &lt;Xacc&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| and_imm_wform |  | AArch64Instruction |  |  | ["Wa"] |  | ["Wd"] | and &lt;Wd&gt;, &lt;Wa&gt;, &lt;imm&gt; |  |  |  |
| tst_wform |  | Tst |  |  | ["Wa"] | True |  | tst &lt;Wa&gt;, &lt;imm&gt; |  |  |  |
| tst_imm_xform |  | Tst |  |  | ["Xa"] | True |  | tst &lt;Xa&gt;, &lt;imm&gt; |  |  |  |
| tst_xform |  | Tst |  |  | ["Xa","Xb"] | True |  | tst &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| cmp |  | Tst |  |  | ["Xa","Xb"] | True |  | cmp &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| cmp_xzr |  | Tst |  |  | ["Xa"] | True |  | cmp &lt;Xa&gt;, xzr |  |  |  |
| cmp_xzr2 |  | Tst |  |  | [] | True |  | cmp xzr, xzr |  |  |  |
| cmp_imm |  | Tst |  |  | ["Xa"] | True |  | cmp &lt;Xa&gt;, &lt;imm&gt; |  |  |  |
| asr |  | AArch64Shift |  |  | ["Xa","Xb"] |  | ["Xd"] | asr &lt;Xd&gt;, &lt;Xa&gt;, &lt;Xb&gt; |  |  |  |
| sxtb |  | AArch64Logical |  |  | ["Wa"] |  | ["Xd"] | sxtb &lt;Xd&gt;, &lt;Wa&gt; |  |  |  |
| uxtb |  | AArch64Logical |  |  | ["Wa"] |  | ["Wd"] | uxtb &lt;Wd&gt;, &lt;Wa&gt; |  |  |  |
| fcsel |  | AArch64ConditionalSelect | true |  | ["Dn","Dm"] |  | ["Dd"] | fcsel &lt;Dd&gt;, &lt;Dn&gt;, &lt;Dm&gt;, &lt;flag&gt; |  |  |  |
| movk_imm_lsl |  | AArch64Instruction |  | ["Xd"] | [] |  |  | movk &lt;Xd&gt;, &lt;imm0&gt;, &lt;barrel&gt; &lt;imm1&gt; |  |  |  |
| crc32b |  | AArch64CRC32 |  |  | ["Wa","Wb"] |  | ["Wd"] | crc32b &lt;Wd&gt;, &lt;Wa&gt;, &lt;Wb&gt; |  |  |  |
| crc32h |  | AArch64CRC32 |  |  | ["Wa","Wb"] |  | ["Wd"] | crc32h &lt;Wd&gt;, &lt;Wa&gt;, &lt;Wb&gt; |  |  |  |
| crc32w |  | AArch64CRC32 |  |  | ["Wa","Wb"] |  | ["Wd"] | crc32w &lt;Wd&gt;, &lt;Wa&gt;, &lt;Wb&gt; |  |  |  |
| crc32x |  | AArch64CRC32 |  |  | ["Wa","Xb"] |  | ["Wd"] | crc32x &lt;Wd&gt;, &lt;Wa&gt;, &lt;Xb&gt; |  |  |  |
| crc32cb |  | AArch64CRC32 |  |  | ["Wa","Wb"] |  | ["Wd"] | crc32cb &lt;Wd&gt;, &lt;Wa&gt;, &lt;Wb&gt; |  |  |  |
| crc32ch |  | AArch64CRC32 |  |  | ["Wa","Wb"] |  | ["Wd"] | crc32ch &lt;Wd&gt;, &lt;Wa&gt;, &lt;Wb&gt; |  |  |  |
| crc32cw |  | AArch64CRC32 |  |  | ["Wa","Wb"] |  | ["Wd"] | crc32cw &lt;Wd&gt;, &lt;Wa&gt;, &lt;Wb&gt; |  |  |  |
| crc32cx |  | AArch64CRC32 |  |  | ["Wa","Xb"] |  | ["Wd"] | crc32cx &lt;Wd&gt;, &lt;Wa&gt;, &lt;Xb&gt; |  |  |  |
