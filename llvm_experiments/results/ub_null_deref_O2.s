	.text
	.file	"ub_null_deref.c"
	.globl	process                         # -- Begin function process
	.p2align	4, 0x90
	.type	process,@function
process:                                # @process
	.cfi_startproc
# %bb.0:
	movl	(%rdi), %esi
	leaq	.L.str.1(%rip), %rdi
	xorl	%eax, %eax
	jmp	printf@PLT                      # TAILCALL
.Lfunc_end0:
	.size	process, .Lfunc_end0-process
	.cfi_endproc
                                        # -- End function
	.globl	main                            # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:
.Lfunc_end1:
	.size	main, .Lfunc_end1-main
	.cfi_endproc
                                        # -- End function
	.type	.L.str.1,@object                # @.str.1
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str.1:
	.asciz	"value: %d\n"
	.size	.L.str.1, 11

	.ident	"Ubuntu clang version 18.1.3 (1ubuntu1)"
	.section	".note.GNU-stack","",@progbits
	.addrsig
