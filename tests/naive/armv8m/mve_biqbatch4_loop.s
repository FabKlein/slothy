coef_ptr   .req r2

in_ptr      .req r0
out_ptr     .req r1

count .req r3





//z012 .req q2
//z02 .req q3

//q1 and q6 free




start:

        ldrd      r4, r5, [in_ptr], #8
        ldrd      r6, r7, [in_ptr], #8
        //ext     q4, v16.16b, q0.16b, #12
        //vorr.u32 q4, q0, q0
        vshlc           q0, r4, #32

        //vldrw.u32       q7, [coef_ptr, #0]

        vfma.f32    q2, q1, q0
        //vldrw.u32       q7, [coef_ptr, #16]
        vfma.f32    q3, q6, q0
        vldrw.u32       q7, [coef_ptr, #32]
        vmul.f32    q5, q7, q0
        vldrw.u32       q7, [coef_ptr, #48]
        vfms.f32    q3, q7, q2
        vldrw.u32       q7, [coef_ptr, #64]
        vfms.f32    q5, q7, q2
        //st1     { q2.s }[3], [out_ptr], #4

        vstm            %[out_ptr]!, {s11}
        // vstrw.u32    q2, [out_ptr], #4

        //ldr     r4, [in_ptr], #4
        //ext     q4, v16.16b, q2.16b, #12
        vshlc           q2, r5, #32
        //vldrw.u32       q7, [coef_ptr, #0]
        vfma.f32    q3, q1, q2
        //vldrw.u32       q7, [coef_ptr, #16]
        vfma.f32    q5, q6, q2
        vldrw.u32       q7, [coef_ptr, #32]
        vmul.f32    q0, q7, q2
        vldrw.u32       q7, [coef_ptr, #48]
        vfms.f32    q5, q7, q3
        vldrw.u32       q7, [coef_ptr, #64]
        vfms.f32    q0, q7, q3
        //st1     { q3.s }[3], [out_ptr], #4
        //vstrw.u32    q3, [out_ptr], #4
        vstm            %[out_ptr]!, {s15}

        //ldr     r4, [in_ptr], #4
        //ext     q4, v16.16b, q3.16b, #12
        vshlc           q3, r6, #32
        //vldrw.u32       q7, [coef_ptr, #0]
        vfma.f32    q5, q1, q3
        //vldrw.u32       q7, [coef_ptr, #16]
        vfma.f32    q0, q6, q3
        vldrw.u32       q7, [coef_ptr, #32]
        vmul.f32    q2, q7, q3
        vldrw.u32       q7, [coef_ptr, #48]
        vfms.f32    q0, q7, q5
        vldrw.u32       q7, [coef_ptr, #64]
        vfms.f32    q2, q7, q5
        //st1     { q5 }[3], [out_ptr], #4
         //vstrw.u32    q5, [out_ptr], #4
         vstm            %[out_ptr]!, {s23}


        //ldr     r4, [in_ptr], #4

        vshlc           q5, r7, #32
        //vldrw.u32       q7, [coef_ptr, #0]

        vfma.f32    q0, q1, q5
        //vldrw.u32       q7, [coef_ptr, #16]
        vfma.f32    q2, q6, q5
        vldrw.u32       q7, [coef_ptr, #32]
        vmul.f32    q3, q7, q5
        vldrw.u32       q7, [coef_ptr, #48]
        vfms.f32    q2, q7, q0
        vldrw.u32       q7, [coef_ptr, #64]
        vfms.f32    q3, q7, q0
        //st1     { q0.s }[3], [out_ptr], #4
        //vstrw.u32    q0, [out_ptr], #4
        vstm            %[out_ptr]!, {s3}





    le lr, start



vstrw.u32    q1, [state_ptr], #16
vstrw.u32    q2, [state_ptr], #16
