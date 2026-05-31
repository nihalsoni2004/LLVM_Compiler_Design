	.text
	.file	"ub_type_punning.c"
	.globl	int_to_float_ub                 # -- Begin function int_to_float_ub
	.p2align	4, 0x90
	.type	int_to_float_ub,@function
int_to_float_ub:                        # @int_to_float_ub
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	movl	%edi, -4(%rbp)
	leaq	-4(%rbp), %rax
	movq	%rax, -16(%rbp)
	movq	-16(%rbp), %rax
	movss	(%rax), %xmm0                   # xmm0 = mem[0],zero,zero,zero
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end0:
	.size	int_to_float_ub, .Lfunc_end0-int_to_float_ub
	.cfi_endproc
                                        # -- End function
	.globl	int_to_float_safe               # -- Begin function int_to_float_safe
	.p2align	4, 0x90
	.type	int_to_float_safe,@function
int_to_float_safe:                      # @int_to_float_safe
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	movl	%edi, -4(%rbp)
	movl	-4(%rbp), %eax
	movl	%eax, -8(%rbp)
	movss	-8(%rbp), %xmm0                 # xmm0 = mem[0],zero,zero,zero
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end1:
	.size	int_to_float_safe, .Lfunc_end1-int_to_float_safe
	.cfi_endproc
                                        # -- End function
	.globl	main                            # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$16, %rsp
	movl	$0, -4(%rbp)
	movl	$1065353216, -8(%rbp)           # imm = 0x3F800000
	movl	-8(%rbp), %edi
	callq	int_to_float_ub
	cvtss2sd	%xmm0, %xmm0
	leaq	.L.str(%rip), %rdi
	movb	$1, %al
	callq	printf@PLT
	movl	-8(%rbp), %edi
	callq	int_to_float_safe
	cvtss2sd	%xmm0, %xmm0
	leaq	.L.str.1(%rip), %rdi
	movb	$1, %al
	callq	printf@PLT
	xorl	%eax, %eax
	addq	$16, %rsp
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end2:
	.size	main, .Lfunc_end2-main
	.cfi_endproc
                                        # -- End function
	.type	.L.str,@object                  # @.str
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str:
	.asciz	"UB way:   %f\n"
	.size	.L.str, 14

	.type	.L.str.1,@object                # @.str.1
.L.str.1:
	.asciz	"Safe way: %f\n"
	.size	.L.str.1, 14

	.ident	"Ubuntu clang version 18.1.3 (1ubuntu1)"
	.section	".note.GNU-stack","",@progbits
	.addrsig
	.addrsig_sym int_to_float_ub
	.addrsig_sym int_to_float_safe
	.addrsig_sym printf
