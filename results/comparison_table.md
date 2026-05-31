# UB Detection Tool Comparison

| Program | UB Type | UBSan | Clang Warn | clang-tidy | cppcheck | LLM Detect | LLM Explain |
|---------|---------|-------|------------|------------|----------|------------|-------------|
| ub_signed_overflow | Signed Overflow | Y | Y | N | Y | Y | Y |
| ub_null_deref | Null Dereference | Y | N | Y | Y | Y | Y |
| ub_oob_access | Out-of-Bounds | Y | Y | Y | N | Y | Y |
| ub_invalid_shift | Invalid Shift | Y | Y | Y | Y | Y | Y |
| ub_use_after_free | Use-After-Free | Y | N | Y | Y | Y | N |
| ub_uninitialized | Uninitialized Read | Y | Y | Y | Y | Y | Y |
| ub_div_zero | Division by Zero | Y | N | Y | Y | Y | N |
| ub_type_punning | Strict Aliasing | N | N | N | N | Y | N |
| ub_double_free | Double Free | Y | N | Y | Y | Y | N |
| ub_string_literal | String Literal Mod | N | N | N | Y | Y | Y |
| safe_arithmetic | None (Safe) | N | N | N | N | N | Y |
| safe_array | None (Safe) | N | N | N | N | N | Y |
| safe_pointers | None (Safe) | N | N | N | N | N | Y |

## Summary

Total UB programs: 10

- **UBSan**: 8/10 detected (80%)
- **Clang Warnings**: 4/10 detected (40%)
- **clang-tidy**: 7/10 detected (70%)
- **cppcheck**: 8/10 detected (80%)
- **LLM**: 10/10 detected (100%)
