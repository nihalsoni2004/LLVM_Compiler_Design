	.text
	.file	"ub_type_punning.c"
	.globl	int_to_float_ub                 # -- Begin function int_to_float_ub
	.p2align	4, 0x90
	.type	int_to_float_ub,@function
int_to_float_ub:                        # @int_to_float_ub
	.cfi_startproc
# %bb.0:
	movd	%edi, %xmm0
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
	movd	%edi, %xmm0
	retq
.Lfunc_end1:
	.size	int_to_float_safe, .Lfunc_end1-int_to_float_safe
	.cfi_endproc
                                        # -- End function
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3, 0x0                          # -- Begin function main
.LCPI2_0:
	.quad	0x3ff0000000000000              # double 1
	.text
	.globl	main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:
	pushq	%rax
	.cfi_def_cfa_offset 16
	leaq	.L.str(%rip), %rdi
	movsd	.LCPI2_0(%rip), %xmm0           # xmm0 = [1.0E+0,0.0E+0]
	movb	$1, %al
	callq	printf@PLT
	leaq	.L.str.1(%rip), %rdi
	movsd	.LCPI2_0(%rip), %xmm0           # xmm0 = [1.0E+0,0.0E+0]
	movb	$1, %al
	callq	printf@PLT
	xorl	%eax, %eax
	popq	%rcx
	.cfi_def_cfa_offset 8
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
