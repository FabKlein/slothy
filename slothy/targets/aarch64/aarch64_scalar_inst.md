| addr_source | base | dependsOnFlags | in_outs | inputs | modifiesFlags | name | outputs | pattern | pre_index_from_immediate | restore_immediate_from_pre_index | set_increment_from_immediate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {"type":"inputs","index":0} | Ldr_S |  |  | ["Xc"] |  | s_ldr | ["Sa"] | ldr <Sa>, [<Xc>] |  |  |  |
| {"type":"inputs","index":0} | Ldr_S |  |  | ["Xc"] |  | s_ldr_with_inc | ["Sa"] | ldr <Sa>, [<Xc>, <imm>] | True | True |  |
| {"type":"in_outs","index":0} | Ldr_S |  | ["Xc"] |  |  | s_ldr_with_inc_writeback | ["Sa"] | ldr <Sa>, [<Xc>, <imm>]! |  |  | True |
| {"type":"in_outs","index":0} | Ldr_S |  | ["Xc"] |  |  | s_ldr_with_postinc | ["Sa"] | ldr <Sa>, [<Xc>], <imm> |  |  | True |
| {"type":"inputs","index":1} | Str_S |  |  | ["Sa","Xc"] |  | s_str |  | str <Sa>, [<Xc>] |  |  |  |
| {"type":"inputs","index":1} | Str_S |  |  | ["Sa","Xc"] |  | s_str_with_inc |  | str <Sa>, [<Xc>, <imm>] | True | True |  |
| {"type":"in_outs","index":0} | Str_S |  | ["Xc"] | ["Sa"] |  | s_str_with_inc_writeback |  | str <Sa>, [<Xc>, <imm>]! |  |  | True |
| {"type":"in_outs","index":0} | Str_S |  | ["Xc"] | ["Sa"] |  | s_str_with_postinc |  | str <Sa>, [<Xc>], <imm> |  |  | True |
| {"type":"inputs","index":0} | Ldp_S |  |  | ["Xc"] |  | s_ldp | ["Sa","Sb"] | ldp <Sa>, <Sb>, [<Xc>] |  |  |  |
| {"type":"inputs","index":0} | Ldp_S |  |  | ["Xc"] |  | s_ldp_with_inc | ["Sa","Sb"] | ldp <Sa>, <Sb>, [<Xc>, <imm>] | True | True |  |
| {"type":"in_outs","index":0} | Ldp_S |  | ["Xc"] |  |  | s_ldp_with_inc_writeback | ["Sa","Sb"] | ldp <Sa>, <Sb>, [<Xc>, <imm>]! |  |  | True |
| {"type":"in_outs","index":0} | Ldp_S |  | ["Xc"] |  |  | s_ldp_with_postinc | ["Sa","Sb"] | ldp <Sa>, <Sb>, [<Xc>], <imm> |  |  | True |
| {"type":"inputs","index":2} | Stp_S |  |  | ["Sa","Sb","Xc"] |  | s_stp |  | stp <Sa>, <Sb>, [<Xc>] |  |  |  |
| {"type":"inputs","index":2} | Stp_S |  |  | ["Sa","Sb","Xc"] |  | s_stp_with_inc |  | stp <Sa>, <Sb>, [<Xc>, <imm>] | True | True |  |
| {"type":"in_outs","index":0} | Stp_S |  | ["Xc"] | ["Sa","Sb"] |  | s_stp_with_inc_writeback |  | stp <Sa>, <Sb>, [<Xc>, <imm>]! |  |  | True |
| {"type":"in_outs","index":0} | Stp_S |  | ["Xc"] | ["Sa","Sb"] |  | s_stp_with_postinc |  | stp <Sa>, <Sb>, [<Xc>], <imm> |  |  | True |
|  | Sfma |  |  | ["Sb","Sc","Sd"] |  | sfmadd | ["Sa"] | fmadd <Sa>, <Sb>, <Sc>, <Sd> |  |  |  |
|  | Sfma |  |  | ["Sb","Sc","Sd"] |  | sfmsub | ["Sa"] | fmsub <Sa>, <Sb>, <Sc>, <Sd> |  |  |  |
|  | Sfma |  |  | ["Sb","Sc","Sd"] |  | sfnmadd | ["Sa"] | fnmadd <Sa>, <Sb>, <Sc>, <Sd> |  |  |  |
|  | Sfma |  |  | ["Sb","Sc","Sd"] |  | sfnmsub | ["Sa"] | fnmsub <Sa>, <Sb>, <Sc>, <Sd> |  |  |  |
|  | Smul |  |  | ["Sb","Sc"] |  | sfmul | ["Sa"] | fmul <Sa>, <Sb>, <Sc> |  |  |  |
|  | Smul |  |  | ["Sb","Sc"] |  | sfnmul | ["Sa"] | fnmul <Sa>, <Sb>, <Sc> |  |  |  |
| {"type":"inputs","index":0} | Ldr_D |  |  | ["Xc"] |  | d_ldr | ["Da"] | ldr <Da>, [<Xc>] |  |  |  |
| {"type":"in_outs","index":0} | Ldr_D |  | ["Xc"] |  |  | d_ldr_with_postinc | ["Da"] | ldr <Da>, [<Xc>], <imm> |  |  | True |
| {"type":"in_outs","index":0} | Ldr_D |  | ["Xc"] |  |  | d_ldr_with_inc_writeback | ["Da"] | ldr <Da>, [<Xc>, <imm>]! |  |  | True |
| {"type":"literal","value":"sp"} | Ldr_Q |  |  |  |  | d_ldp_sp_imm | ["Da","Db"] | ldp <Da>, <Db>, [sp, <imm>] | True | True |  |
| {"type":"literal","value":"sp"} | Ldr_D |  |  |  |  | d_ldr_stack_with_inc | ["Da"] | ldr <Da>, [sp, <imm>] | True | True |  |
| {"type":"literal","value":"sp"} | AArch64Instruction |  |  | ["Da"] |  | d_str_stack_with_inc |  | str <Da>, [sp, <imm>] | True | True |  |
| {"type":"literal","value":"sp"} | AArch64Instruction |  |  | ["Da","Db"] |  | d_stp_stack_with_inc |  | stp <Da>, <Db>, [sp, <imm>] | True | True |  |
| {"type":"inputs","index":0} | Ldr_X |  |  | ["Xc"] |  | x_ldr | ["Xa"] | ldr <Xa>, [<Xc>] |  |  |  |
| {"type":"inputs","index":0} | Ldr_X |  |  | ["Xc"] |  | x_ldr_with_imm | ["Xa"] | ldr <Xa>, [<Xc>, <imm>] | True | True |  |
| {"type":"inputs","index":0} | Ldr_X |  |  | ["Xa","Xb"] |  | x_ldr_with_imm_uxtw | ["Xd"] | ldr <Xd>, [<Xa>, <Xb>, UXTW <imm>] | True | True |  |
| {"type":"inputs","index":0} | Ldr_X |  |  | ["Xa","Xb"] |  | x_ldr_with_imm_shifted | ["Xd"] | ldr <Xd>, [<Xa>, <Xb>, <barrel> <imm>] | True | True |  |
| {"type":"inputs","index":0} | Ldr_X |  |  | ["Xb","Xc"] |  | x_ldr_regidx | ["Xa"] | ldr <Xa>, [<Xb>, <Xc>] |  |  |  |
| {"type":"in_outs","index":0} | Ldr_X |  | ["Xc"] |  |  | x_ldr_with_postinc | ["Xa"] | ldr <Xa>, [<Xc>], <imm> |  |  | True |
| {"type":"literal","value":"sp"} | Ldr_X |  |  |  |  | x_ldr_stack | ["Xa"] | ldr <Xa>, [sp] |  |  |  |
| {"type":"literal","value":"sp"} | Ldr_X |  |  |  |  | x_ldr_stack_imm | ["Xa"] | ldr <Xa>, [sp, <imm>] | True | True |  |
| {"type":"literal","value":"sp"} | Ldr_X |  |  | ["Th"] |  | x_ldr_stack_imm_with_hint | ["Xa"] | ldrh <Xa>, sp, <imm>, <Th> | True | True |  |
| {"type":"inputs","index":0} | Ldr_X |  |  | ["Xb","Th"] |  | x_ldr_imm_with_hint | ["Xa"] | ldrh <Xa>, <Xb>, <imm>, <Th> | True | True |  |
| {"type":"inputs","index":0} | Ldp_X |  |  | ["Xc"] |  | x_ldp | ["Xa","Xb"] | ldp <Xa>, <Xb>, [<Xc>] |  |  |  |
| {"type":"literal","value":"sp"} | Ldp_X |  |  |  |  | x_ldp_with_imm_sp_xzr | ["Xa"] | ldp <Xa>, xzr, [sp, <imm>] | True | True |  |
| {"type":"literal","value":"sp"} | Ldp_X |  |  |  |  | x_ldp_with_imm_sp | ["Xa","Xb"] | ldp <Xa>, <Xb>, [sp, <imm>] | True | True |  |
| {"type":"literal","value":"sp"} | Ldp_X |  |  |  |  | x_ldp_with_sp | ["Xa","Xb"] | ldp <Xa>, <Xb>, [sp] |  |  |  |
| {"type":"inputs","index":0} | Ldp_X |  |  | ["Xc"] |  | x_ldp_with_inc | ["Xa","Xb"] | ldp <Xa>, <Xb>, [<Xc>, <imm>] | True | True |  |
| {"type":"in_outs","index":0} | Ldp_X |  | ["Xc"] |  |  | x_ldp_with_inc_writeback | ["Xa","Xb"] | ldp <Xa>, <Xb>, [<Xc>, <imm>]! |  |  | True |
| {"type":"in_outs","index":0} | Ldp_X |  | ["Xc"] |  |  | x_ldp_with_postinc_writeback | ["Xa","Xb"] | ldp <Xa>, <Xb>, [<Xc>], <imm> |  |  | True |
| {"type":"inputs","index":0} | Ldp_X |  |  | ["Xc","Th"] |  | x_ldp_with_imm_hint | ["Xa","Xb"] | ldph <Xa>, <Xb>, <Xc>, <imm>, <Th> | True | True |  |
| {"type":"literal","value":"sp"} | Ldp_X |  |  | ["Th"] |  | x_ldp_sp_with_imm_hint | ["Xa","Xb"] | ldph <Xa>, <Xb>, sp, <imm>, <Th> | True | True |  |
| {"type":"literal","value":"sp"} | Ldp_X |  |  | ["Th0","Th1"] |  | x_ldp_sp_with_imm_hint2 | ["Xa","Xb"] | ldphp <Xa>, <Xb>, sp, <imm>, <Th0>, <Th1> | True | True |  |
| {"type":"inputs","index":0} | Ldp_X |  |  | ["Xc","Th0","Th1"] |  | x_ldp_with_imm_hint2 | ["Xa","Xb"] | ldphp <Xa>, <Xb>, <Xc>, <imm>, <Th0>, <Th1> | True | True |  |
| {"type":"inputs","index":0} | AArch64Instruction |  |  | ["Xa","Wb"] |  | ldr_sxtw_wform | ["Wd"] | ldr <Wd>, [<Xa>, <Wb>, SXTW <imm>] |  |  |  |
|  | AArch64Instruction |  |  | ["Wa","Wb"] |  | lsr_wform | ["Wd"] | lsr <Wd>, <Wa>, <Wb> |  |  |  |
|  | AArch64Instruction |  |  | ["Wa"] |  | asr_wform | ["Wd"] | asr <Wd>, <Wa>, <imm> |  |  |  |
|  | AArch64BasicArithmetic |  |  | ["Wa"] | True | subs_wform | ["Wd"] | subs <Wd>, <Wa>, <imm> |  |  |  |
|  | AArch64BasicArithmetic |  |  | ["Xa"] | True | subs_imm | ["Xd"] | subs <Xd>, <Xa>, <imm> |  |  |  |
|  | AArch64BasicArithmetic |  |  | ["Xa"] |  | sub_imm | ["Xd"] | sub <Xd>, <Xa>, <imm> |  |  |  |
|  | AArch64BasicArithmetic |  |  | ["Xa"] |  | add_imm | ["Xd"] | add <Xd>, <Xa>, <imm> |  |  |  |
|  | AArch64BasicArithmetic |  |  |  |  | add_sp_imm | ["Xd"] | add <Xd>, sp, <imm> |  |  |  |
|  | AArch64BasicArithmetic |  |  | ["Xa"] |  | neg | ["Xd"] | neg <Xd>, <Xa> |  |  |  |
|  | AArch64BasicArithmetic |  |  | ["Xa"] | True | negs | ["Xd"] | negs <Xd>, <Xa> |  |  |  |
|  | AArch64BasicArithmetic | True |  | [] |  | ngc_zero | ["Xd"] | ngc <Xd>, xzr |  |  |  |
|  | AArch64BasicArithmetic | True |  | ["Xa"] | True | ngcs | ["Xd"] | ngcs <Xd>, <Xa> |  |  |  |
|  | AArch64BasicArithmetic | True |  | [] | True | ngcs_zero | ["Xd"] | ngcs <Xd>, xzr |  |  |  |
|  | AArch64BasicArithmetic |  |  | ["Xa"] | True | adds | ["Xd"] | adds <Xd>, <Xa>, <imm> |  |  |  |
|  | AArch64BasicArithmetic |  |  | ["Xa","Xb"] | True | adds_to_zero | [] | adds xzr, <Xa>, <Xb> |  |  |  |
|  | AArch64BasicArithmetic |  |  | ["Xa"] | True | adds_imm_to_zero | [] | adds xzr, <Xa>, <imm> |  |  |  |
|  | AArch64BasicArithmetic |  |  | ["Xa","Xb"] | True | subs_twoarg | ["Xd"] | subs <Xd>, <Xa>, <Xb> |  |  |  |
|  | AArch64BasicArithmetic |  |  | ["Xa","Xb"] | True | adds_twoarg | ["Xd"] | adds <Xd>, <Xa>, <Xb> |  |  |  |
|  | AArch64BasicArithmetic | True |  | ["Xa","Xb"] | True | adcs | ["Xd"] | adcs <Xd>, <Xa>, <Xb> |  |  |  |
|  | AArch64BasicArithmetic | True |  | ["Xa","Xb"] | True | sbcs | ["Xd"] | sbcs <Xd>, <Xa>, <Xb> |  |  |  |
|  | AArch64BasicArithmetic | True |  | ["Xa"] | True | sbcs_zero | ["Xd"] | sbcs <Xd>, <Xa>, xzr |  |  |  |
|  | AArch64BasicArithmetic | True |  | ["Xa","Xb"] | True | sbcs_to_zero | [] | sbcs xzr, <Xa>, <Xb> |  |  |  |
|  | AArch64BasicArithmetic | True |  | ["Xa"] | True | sbcs_zero_to_zero | [] | sbcs xzr, <Xa>, xzr |  |  |  |
|  | AArch64BasicArithmetic | True |  | ["Xa","Xb"] |  | sbc | ["Xd"] | sbc <Xd>, <Xa>, <Xb> |  |  |  |
|  | AArch64BasicArithmetic | True |  | ["Xa"] |  | sbc_zero_r | ["Xd"] | sbc <Xd>, <Xa>, xzr |  |  |  |
|  | AArch64BasicArithmetic | True |  | ["Xa"] | True | adcs_zero_r | ["Xd"] | adcs <Xd>, <Xa>, xzr |  |  |  |
|  | AArch64BasicArithmetic | True |  | ["Xb"] | True | adcs_zero_l | ["Xd"] | adcs <Xd>, xzr, <Xb> |  |  |  |
|  | AArch64BasicArithmetic | True |  | [] | True | adcs_zero2 | ["Xd"] | adcs <Xd>, xzr, xzr |  |  |  |
|  | AArch64BasicArithmetic | True |  | ["Xa","Xb"] | True | adcs_to_zero | [] | adcs xzr, <Xa>, <Xb> |  |  |  |
|  | AArch64BasicArithmetic | True |  | ["Xa"] | True | adcs_zero_r_to_zero | [] | adcs xzr, <Xa>, xzr |  |  |  |
|  | AArch64BasicArithmetic | True |  | ["Xa","Xb"] |  | adc | ["Xd"] | adc <Xd>, <Xa>, <Xb> |  |  |  |
|  | AArch64BasicArithmetic | True |  | [] |  | adc_zero2 | ["Xd"] | adc <Xd>, xzr, xzr |  |  |  |
|  | AArch64BasicArithmetic | True |  | ["Xa"] |  | adc_zero_r | ["Xd"] | adc <Xd>, <Xa>, xzr |  |  |  |
|  | AArch64BasicArithmetic | True |  | ["Xa"] |  | adc_zero_l | ["Xd"] | adc <Xd>, xzr, <Xa> |  |  |  |
|  | AArch64BasicArithmetic |  |  | ["Xa","Xb"] |  | add | ["Xd"] | add <Xd>, <Xa>, <Xb> |  |  |  |
|  | AArch64BasicArithmetic |  |  | ["Xa","Xb"] |  | add2 | ["Xd"] | add <Xd>, <Xa>, <Xb>, <imm> |  |  |  |
|  | AArch64BasicArithmetic |  |  | ["Wa"] |  | add_w_imm | ["Wd"] | add <Wd>, <Wa>, <imm> |  |  |  |
|  | AArch64BasicArithmetic |  |  | ["Xa","Xb"] |  | sub | ["Xd"] | sub <Xd>, <Xa>, <Xb> |  |  |  |
|  | AArch64ShiftedArithmetic |  |  | ["Xa","Xb"] |  | eor_shifted | ["Xd"] | eor <Xd>, <Xa>, <Xb>, <barrel> <imm> |  |  |  |
|  | AArch64ShiftedArithmetic |  |  | ["Xa","Xb"] |  | bic_shifted | ["Xd"] | bic <Xd>, <Xa>, <Xb>, <barrel> <imm> |  |  |  |
|  | AArch64ShiftedArithmetic |  |  | ["Xa","Xb"] |  | add_shifted | ["Xd"] | add <Xd>, <Xa>, <Xb>, <barrel> <imm> |  |  |  |
|  | AArch64ShiftedArithmetic |  |  | ["Xa","Xb"] | True | adds_shifted | ["Xd"] | adds <Xd>, <Xa>, <Xb>, <barrel> <imm> |  |  |  |
|  | AArch64ShiftedArithmetic |  |  | ["Xa"] |  | add_imm_shifted | ["Xd"] | add <Xd>, <Xa>, <imm0>, <barrel> <imm1> |  |  |  |
|  | AArch64Shift |  |  | ["Xa"] |  | lsr_imm | ["Xd"] | lsr <Xd>, <Xa>, <imm> |  |  |  |
|  | AArch64Shift |  |  | ["Xa","Xc"] |  | lsr | ["Xd"] | lsr <Xd>, <Xa>, <Xc> |  |  |  |
|  | AArch64Shift |  |  | ["Xa"] |  | lsl | ["Xd"] | lsl <Xd>, <Xa>, <imm> |  |  |  |
|  | AArch64Shift |  |  | ["Xa"] |  | ror | ["Xd"] | ror <Xd>, <Xa>, <imm> |  |  |  |
|  | AArch64Shift |  |  | ["Xa"] |  | asr_imm | ["Xd"] | asr <Xd>, <Xa>, <imm> |  |  |  |
|  | AArch64Logical |  |  | ["Wa"] |  | rev_w | ["Wd"] | rev <Wd>, <Wa> |  |  |  |
|  | AArch64Logical |  |  | ["Wa","Wb"] |  | eor_wform | ["Wd"] | eor <Wd>, <Wa>, <Wb> |  |  |  |
|  | AArch64Logical |  |  | ["Wa","Wb"] |  | eon_wform | ["Wd"] | eon <Wd>, <Wa>, <Wb> |  |  |  |
|  | AArch64Logical |  |  | ["Xa","Xb"] |  | eor | ["Xd"] | eor <Xd>, <Xa>, <Xb> |  |  |  |
|  | AArch64Logical |  |  | ["Xa","Xb"] |  | eon | ["Xd"] | eon <Xd>, <Xa>, <Xb> |  |  |  |
|  | AArch64Logical |  |  | ["Xa","Xb"] |  | orr | ["Xd"] | orr <Xd>, <Xa>, <Xb> |  |  |  |
|  | AArch64Logical |  |  | ["Wa","Wb"] |  | orr_w | ["Wd"] | orr <Wd>, <Wa>, <Wb> |  |  |  |
|  | AArch64Logical |  | ["Xd"] | ["Xa"] |  | bfi |  | bfi <Xd>, <Xa>, <imm0>, <imm1> |  |  |  |
|  | AArch64Logical |  |  | ["Xa"] |  | and_imm | ["Xd"] | and <Xd>, <Xa>, <imm> |  |  |  |
|  | AArch64Logical |  |  | ["Xa"] | True | ands_imm | ["Xd"] | ands <Xd>, <Xa>, <imm> |  |  |  |
|  | AArch64Logical |  |  | ["Xa"] | True | ands_xzr_imm | [] | ands xzr, <Xa>, <imm> |  |  |  |
|  | AArch64Logical |  |  | ["Xa","Xb"] |  | and_twoarg | ["Xd"] | and <Xd>, <Xa>, <Xb> |  |  |  |
|  | AArch64Logical |  |  | ["Xa"] |  | bic | ["Xd"] | bic <Xd>, <Xa>, <imm> |  |  |  |
|  | AArch64Logical |  |  | ["Xa","Xb"] |  | bic_reg | ["Xd"] | bic <Xd>, <Xa>, <Xb> |  |  |  |
|  | AArch64Logical |  |  | ["Xa"] |  | orr_imm | ["Xd"] | orr <Xd>, <Xa>, <imm> |  |  |  |
|  | AArch64Logical |  |  | ["Xa"] |  | sbfx | ["Xd"] | sbfx <Xd>, <Xa>, <imm0>, <imm1> |  |  |  |
|  | AArch64Logical |  |  | ["Xa"] |  | ubfx | ["Xd"] | ubfx <Xd>, <Xa>, <imm0>, <imm1> |  |  |  |
|  | AArch64Logical |  |  | ["Xa","Xb"] |  | extr | ["Xd"] | extr <Xd>, <Xa>, <Xb>, <imm> |  |  |  |
|  | AArch64LogicalShifted |  |  | ["Xa","Xb"] |  | orr_shifted | ["Xd"] | orr <Xd>, <Xa>, <Xb>, <barrel> <imm> |  |  |  |
|  | AArch64LogicalShifted |  |  | ["Wa","Wb"] |  | orr_shifted_w | ["Wd"] | and <Wd>, <Wa>, <Wb>, <barrel> <imm> |  |  |  |
|  | AArch64ConditionalCompare | True |  | ["Xa","Xb"] | True | ccmp |  | ccmp <Xa>, <Xb>, <imm>, <flag> |  |  |  |
|  | AArch64ConditionalCompare | True |  | ["Xa"] | True | ccmp_xzr |  | ccmp xzr, <Xa>, <imm>, <flag> |  |  |  |
|  | AArch64ConditionalCompare | True |  | ["Xa"] | True | ccmp_xzr2 |  | ccmp <Xa>, xzr, <imm>, <flag> |  |  |  |
|  | AArch64ConditionalCompare | True |  | ["Xa","Xb"] | True | ccmn |  | ccmn <Xa>, <Xb>, <imm>, <flag> |  |  |  |
|  | AArch64ConditionalCompare | True |  | ["Xa"] | True | ccmn_xzr |  | ccmn xzr, <Xa>, <imm>, <flag> |  |  |  |
|  | AArch64ConditionalCompare | True |  | ["Xa"] | True | ccmn_xzr2 |  | ccmn <Xa>, xzr, <imm>, <flag> |  |  |  |
|  | AArch64ConditionalSelect | True |  | ["Xe"] |  | cneg | ["Xd"] | cneg <Xd>, <Xe>, <flag> |  |  |  |
|  | AArch64ConditionalSelect | True |  | ["Xe"] |  | csel_xzr_ne | ["Xd"] | csel <Xd>, <Xe>, xzr, <flag> |  |  |  |
|  | AArch64ConditionalSelect | True |  | ["Xe"] |  | csel_xzr2_ne | ["Xd"] | csel <Xd>, xzr, <Xe>, <flag> |  |  |  |
|  | AArch64ConditionalSelect | True |  | ["Xe","Xf"] |  | csel | ["Xd"] | csel <Xd>, <Xe>, <Xf>, <flag> |  |  |  |
|  | AArch64ConditionalSelect | True |  | ["Xe"] |  | cinv | ["Xd"] | cinv <Xd>, <Xe>, <flag> |  |  |  |
|  | AArch64ConditionalSelect | True |  | ["Xe"] |  | cinc | ["Xd"] | cinc <Xd>, <Xe>, <flag> |  |  |  |
|  | AArch64ConditionalSelect | True |  |  |  | csetm | ["Xd"] | csetm <Xd>, <flag> |  |  |  |
|  | AArch64ConditionalSelect | True |  |  |  | cset | ["Xd"] | cset <Xd>, <flag> |  |  |  |
|  | AArch64ConditionalSelect |  |  | ["Xd","Xe"] | True | cmn |  | cmn <Xd>, <Xe> |  |  |  |
|  | AArch64ConditionalSelect |  |  | ["Xd"] | True | cmn_imm |  | cmn <Xd>, <imm> |  |  |  |
|  | AArch64Instruction |  |  | [] |  | ldr_const | ["Xd"] | ldr <Xd>, <literal> |  |  |  |
|  | AArch64Instruction |  | ["Xd"] | [] |  | movk_imm |  | movk <Xd>, <imm> |  |  |  |
|  | AArch64Instruction |  |  | ["Wa"] |  | mov | ["Wd"] | mov <Wd>, <Wa> |  |  |  |
|  | AArch64Move |  |  | [] |  | movz_imm | ["Xd"] | movz <Xd>, <imm> |  |  |  |
|  | AArch64Move |  |  | [] |  | movz_imm_lsl | ["Xd"] | movz <Xd>, <imm0>, <barrel> <imm1> |  |  |  |
|  | AArch64Move |  |  | [] |  | mov_imm | ["Xd"] | mov <Xd>, <imm> |  |  |  |
|  | AArch64Move |  |  | [] |  | movw_imm | ["Wd"] | mov <Wd>, <imm> |  |  |  |
|  | AArch64Move |  |  | [] |  | mvn_xzr | ["Xd"] | mvn <Xd>, xzr |  |  |  |
|  | AArch64Move |  |  | ["Xa"] |  | mov_xform | ["Xd"] | mov <Xd>, <Xa> |  |  |  |
|  | AArch64Instruction |  |  | ["Wa","Wb"] |  | umull_wform | ["Xd"] | umull <Xd>, <Wa>, <Wb> |  |  |  |
|  | AArch64Instruction |  |  | ["Wa","Wb","Xacc"] |  | umaddl_wform | ["Xn"] | umaddl <Xn>, <Wa>, <Wb>, <Xacc> |  |  |  |
|  | AArch64Instruction |  |  | ["Wa","Wb"] |  | mul_wform | ["Wd"] | mul <Wd>, <Wa>, <Wb> |  |  |  |
|  | AArch64HighMultiply |  |  | ["Xa","Xb"] |  | umulh_xform | ["Xd"] | umulh <Xd>, <Xa>, <Xb> |  |  |  |
|  | AArch64HighMultiply |  |  | ["Xa","Xb"] |  | smulh_xform | ["Xd"] | smulh <Xd>, <Xa>, <Xb> |  |  |  |
|  | AArch64Multiply |  |  | ["Xa","Xb"] |  | mul_xform | ["Xd"] | mul <Xd>, <Xa>, <Xb> |  |  |  |
|  | AArch64Multiply |  |  | ["Xacc","Xa","Xb"] |  | madd_xform | ["Xd"] | madd <Xd>, <Xacc>, <Xa>, <Xb> |  |  |  |
|  | AArch64Multiply |  |  | ["Xa","Xb"] |  | mneg_xform | ["Xd"] | mneg <Xd>, <Xa>, <Xb> |  |  |  |
|  | AArch64Multiply |  |  | ["Xacc","Xa","Xb"] |  | msub_xform | ["Xd"] | msub <Xd>, <Xacc>, <Xa>, <Xb> |  |  |  |
|  | AArch64Instruction |  |  | ["Wa"] |  | and_imm_wform | ["Wd"] | and <Wd>, <Wa>, <imm> |  |  |  |
|  | Tst |  |  | ["Wa"] | True | tst_wform |  | tst <Wa>, <imm> |  |  |  |
|  | Tst |  |  | ["Xa"] | True | tst_imm_xform |  | tst <Xa>, <imm> |  |  |  |
|  | Tst |  |  | ["Xa","Xb"] | True | tst_xform |  | tst <Xa>, <Xb> |  |  |  |
|  | Tst |  |  | ["Xa","Xb"] | True | cmp |  | cmp <Xa>, <Xb> |  |  |  |
|  | Tst |  |  | ["Xa"] | True | cmp_xzr |  | cmp <Xa>, xzr |  |  |  |
|  | Tst |  |  | [] | True | cmp_xzr2 |  | cmp xzr, xzr |  |  |  |
|  | Tst |  |  | ["Xa"] | True | cmp_imm |  | cmp <Xa>, <imm> |  |  |  |
|  | AArch64Shift |  |  | ["Xa","Xb"] |  | asr | ["Xd"] | asr <Xd>, <Xa>, <Xb> |  |  |  |
|  | AArch64Logical |  |  | ["Wa"] |  | sxtb | ["Xd"] | sxtb <Xd>, <Wa> |  |  |  |
|  | AArch64Logical |  |  | ["Wa"] |  | uxtb | ["Wd"] | uxtb <Wd>, <Wa> |  |  |  |
|  | AArch64ConditionalSelect | True |  | ["Dn","Dm"] |  | fcsel | ["Dd"] | fcsel <Dd>, <Dn>, <Dm>, <flag> |  |  |  |
|  | AArch64Instruction |  | ["Xd"] | [] |  | movk_imm_lsl |  | movk <Xd>, <imm0>, <barrel> <imm1> |  |  |  |
|  | AArch64CRC32 |  |  | ["Wa","Wb"] |  | crc32b | ["Wd"] | crc32b <Wd>, <Wa>, <Wb> |  |  |  |
|  | AArch64CRC32 |  |  | ["Wa","Wb"] |  | crc32h | ["Wd"] | crc32h <Wd>, <Wa>, <Wb> |  |  |  |
|  | AArch64CRC32 |  |  | ["Wa","Wb"] |  | crc32w | ["Wd"] | crc32w <Wd>, <Wa>, <Wb> |  |  |  |
|  | AArch64CRC32 |  |  | ["Wa","Xb"] |  | crc32x | ["Wd"] | crc32x <Wd>, <Wa>, <Xb> |  |  |  |
|  | AArch64CRC32 |  |  | ["Wa","Wb"] |  | crc32cb | ["Wd"] | crc32cb <Wd>, <Wa>, <Wb> |  |  |  |
|  | AArch64CRC32 |  |  | ["Wa","Wb"] |  | crc32ch | ["Wd"] | crc32ch <Wd>, <Wa>, <Wb> |  |  |  |
|  | AArch64CRC32 |  |  | ["Wa","Wb"] |  | crc32cw | ["Wd"] | crc32cw <Wd>, <Wa>, <Wb> |  |  |  |
|  | AArch64CRC32 |  |  | ["Wa","Xb"] |  | crc32cx | ["Wd"] | crc32cx <Wd>, <Wa>, <Xb> |  |  |  |
