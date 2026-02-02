

coef_ptr   .req r2

in_ptr      .req r0
out_ptr     .req r1

count .req x2

state_ptr     .req r3









start:

	    vldrw.u32  q0, [in_ptr], #16
	    vfma.f32   q1, q0,  q5
	    vstrw.u32    q1, [out_ptr], #16
	    vfma.f32   q2, q0, q6
		vldrw.u32 q7, [coef_ptr, #0]
	    vfms.f32   q2, q1, q7
		vldrw.u32 q7, [coef_ptr, #16]
	    vmul.f32   q3, q0, q7
		vldrw.u32 q7, [coef_ptr, #32]
	    vfms.f32   q3, q1, q7



	    vldrw.u32    q0, [in_ptr], #16
	    vfma.f32   q2, q0, q5
	    vstrw.u32    q2, [out_ptr], #16
	    vfma.f32   q3, q0, q6
		vldrw.u32 q7, [coef_ptr, #0]
	    vfms.f32   q3, q2, q7
		vldrw.u32 q7, [coef_ptr, #16]
	    vmul.f32   q4, q0, q7
		vldrw.u32 q7, [coef_ptr, #32]
	    vfms.f32   q4, q2, q7



	    vldrw.u32    q0, [in_ptr], #16
	    vfma.f32   q3, q0, q5
	    vstrw.u32    q3, [out_ptr], #16
	    vfma.f32   q4, q0, q6
		vldrw.u32 q7, [coef_ptr, #0]
	    vfms.f32   q4, q3, q7
		vldrw.u32 q7, [coef_ptr, #16]
	    vmul.f32   q1, q0, q7
		vldrw.u32 q7, [coef_ptr, #32]
	    vfms.f32   q1, q3, q7



	    vldrw.u32    q0, [in_ptr], #16
	    vfma.f32   q4, q0, q5
	    vstrw.u32    q4, [out_ptr], #16
	    vfma.f32   q1, q0, q6
		vldrw.u32 q7, [coef_ptr, #0]
	    vfms.f32   q1, q4, q7
		vldrw.u32 q7, [coef_ptr, #16]
	    vmul.f32   q2, q0, q7
		vldrw.u32 q7, [coef_ptr, #32]
	    vfms.f32   q2, q4, q7




    le lr, start



vstrw.u32    q1, [state_ptr], #16
vstrw.u32    q2, [state_ptr], #16