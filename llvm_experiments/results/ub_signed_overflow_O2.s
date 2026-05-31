	.text
	.file	"ub_signed_overflow.c"
	.globl	check_overflow                  # -- Begin function check_overflow
	.p2align	4, 0x90
	.type	check_overflow,@function
check_overflow:                         # @check_overflow
	.cfi_startproc
# %bb.0:
	movl	$1, %eax
	retq
.Lfunc_end0:
	.size	check_overflow, .Lfunc_end0-check_overflow
	.cfi_endproc
                                        # -- End function
	.globl	main                            # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:
	pushq	%rax
	.cfi_def_cfa_offset 16
	leaq	.L.str(%rip), %rdi
	movl	$1, %esi
	xorl	%eax, %eax
	callq	printf@PLT
	xorl	%eax, %eax
	popq	%rcx
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end1:
	.size	main, .Lfunc_end1-main
	.cfi_endproc
                                        # -- End function
	.type	.L.str,@object                  # @.str
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str:
	.asciz	"check_overflow(INT_MAX) = %d\n"
	.size	.L.str, 30

	.ident	"Ubuntu clang version 18.1.3 (1ubuntu1)"
	.section	".note.GNU-stack","",@progbits
	.addrsig
