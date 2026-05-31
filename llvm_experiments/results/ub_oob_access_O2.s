	.text
	.file	"ub_oob_access.c"
	.globl	get_element                     # -- Begin function get_element
	.p2align	4, 0x90
	.type	get_element,@function
get_element:                            # @get_element
	.cfi_startproc
# %bb.0:
	movslq	%esi, %rax
	movl	(%rdi,%rax,4), %eax
	retq
.Lfunc_end0:
	.size	get_element, .Lfunc_end0-get_element
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
	.asciz	"%d\n"
	.size	.L.str, 4

	.ident	"Ubuntu clang version 18.1.3 (1ubuntu1)"
	.section	".note.GNU-stack","",@progbits
	.addrsig
