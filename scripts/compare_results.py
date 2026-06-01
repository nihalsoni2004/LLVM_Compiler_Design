#!/usr/bin/env python3
import csv
import os
import re
from pathlib import Path

PROGRAM_INFO = {
    "ub_signed_overflow": "Signed Overflow",
    "ub_null_deref": "Null Dereference",
    "ub_oob_access": "Out-of-Bounds",
    "ub_invalid_shift": "Invalid Shift",
    "ub_use_after_free": "Use-After-Free",
    "ub_uninitialized": "Uninitialized Read",
    "ub_div_zero": "Division by Zero",
    "ub_type_punning": "Strict Aliasing",
    "ub_double_free": "Double Free",
    "ub_string_literal": "String Literal Mod",
    "safe_arithmetic": "None (Safe)",
    "safe_array": "None (Safe)",
    "safe_pointers": "None (Safe)",
}

# Program-specific patterns to avoid counting generic style warnings as UB findings.
CLANG_WARN_PATTERNS = {
    "ub_signed_overflow": [r"overflow", r"invalid test for overflow"],
    "ub_null_deref": [r"null pointer", r"dereference"],
    "ub_oob_access": [r"unsafe buffer", r"out[- ]of[- ]bounds", r"array bounds"],
    "ub_invalid_shift": [r"shift count", r"shift"],
    "ub_use_after_free": [r"use[- ]after[- ]free", r"free"],
    "ub_uninitialized": [r"uninitialized"],
    "ub_div_zero": [r"division by zero"],
    "ub_type_punning": [r"strict alias", r"incompatible", r"invalid pointer"],
    "ub_double_free": [r"double free", r"free"],
    "ub_string_literal": [r"string literal", r"write"],
}

CLANG_TIDY_PATTERNS = {
    "ub_signed_overflow": [r"overflow", r"undefined"],
    "ub_null_deref": [r"nulldereference", r"dereference of null"],
    "ub_oob_access": [r"out[- ]of[- ]bounds", r"undef", r"garbage value"],
    "ub_invalid_shift": [r"bitwiseshift", r"shift"],
    "ub_use_after_free": [r"use of memory after it is freed", r"malloc"],
    "ub_uninitialized": [r"undefinedbinaryoperatorresult", r"garbage value"],
    "ub_div_zero": [r"dividezero", r"division by zero"],
    "ub_type_punning": [r"strict alias", r"aliasing", r"invalid"],
    "ub_double_free": [r"attempt to free released memory", r"malloc"],
    "ub_string_literal": [r"string literal", r"write"],
}

CPPCHECK_PATTERNS = {
    "ub_signed_overflow": [r"invalidTestForOverflow", r"overflow"],
    "ub_null_deref": [r"null pointer", r"ctunullpointer", r"nullPointer"],
    "ub_oob_access": [r"out[- ]of[- ]bounds", r"array", r"index"],
    "ub_invalid_shift": [r"shiftNegative", r"shiftTooManyBits", r"integerOverflow"],
    "ub_use_after_free": [r"deallocuse", r"doubleFree"],
    "ub_uninitialized": [r"uninitvar"],
    "ub_div_zero": [r"zerodiv"],
    "ub_type_punning": [r"invalidPointerCast", r"alias"],
    "ub_double_free": [r"doubleFree"],
    "ub_string_literal": [r"stringLiteralWrite"],
}


def bool_to_symbol(value: bool) -> str:
    return "Y" if value else "N"


def read_text(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")


def split_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        m = re.match(r"^---\s+([^\s]+)\s+---\s*$", line.strip())
        if m:
            current = m.group(1)
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return {k: "\n".join(v) for k, v in sections.items()}


def has_any_pattern(text: str, patterns: list[str]) -> bool:
    lower = text.lower()
    return any(re.search(p.lower(), lower) for p in patterns)


def parse_ubsan(ubsan_text: str, program: str) -> bool:
    sections = split_sections(ubsan_text)
    section = sections.get(program, "")
    if not section:
        return False
    # UBSan/ASan evidence of runtime UB.
    return (
        "runtime error:" in section.lower()
        or "addresssanitizer: error" in section.lower()
        or "error: addresssanitizer" in section.lower()
        or "deadlysignal" in section.lower()
    )


def parse_tool_section(tool_text: str, program: str, patterns_by_program: dict[str, list[str]]) -> bool:
    sections = split_sections(tool_text)
    section = sections.get(program, "")
    if not section:
        return False

    patterns = patterns_by_program.get(program, [])
    if not patterns:
        return False

    # Match only diagnostic message text to avoid false positives from filenames.
    diagnostic_lines = []
    for line in section.splitlines():
        lower = line.lower()
        if "warning:" in lower:
            diagnostic_lines.append(line.split("warning:", 1)[1].strip())
        elif "error:" in lower:
            diagnostic_lines.append(line.split("error:", 1)[1].strip())

    diagnostic_text = "\n".join(diagnostic_lines)
    return has_any_pattern(diagnostic_text, patterns)
def parse_cppcheck(cppcheck_text: str, program: str) -> bool:
    patterns = CPPCHECK_PATTERNS.get(program, [])
    if not patterns:
        return False

    file_markers = [
        f"benchmarks/{program}.c",
        f"testcases/{program}.c",
    ]
    if program.startswith("safe_"):
        file_markers.extend([
            f"benchmarks/safe_programs/{program}.c",
            f"testcases/safe_programs/{program}.c",
        ])

    relevant = []
    for line in cppcheck_text.splitlines():
        if any(marker in line for marker in file_markers) and ("error:" in line.lower() or "warning:" in line.lower()):
            relevant.append(line)

    return has_any_pattern("\n".join(relevant), patterns)


def parse_llm_detection(llm_text: str) -> tuple[bool, bool]:
    lower = llm_text.lower()

    if "error:" in lower and "llm analysis" in lower:
        return False, False

    # Prefer the DETECTION section, fallback to first YES/NO mentions.
    detect_match = re.search(r"detection[^\n]*\n([^\n]+)", lower)
    if detect_match:
        line = detect_match.group(1)
        if "yes" in line:
            detect = True
        elif "no" in line:
            detect = False
        else:
            detect = "contains undefined" in lower and "yes" in lower
    else:
        if "contains undefined" in lower and "yes" in lower:
            detect = True
        elif re.search(r"\bno\b", lower):
            detect = False
        else:
            detect = False

    explain = ("error:" not in lower) and ("explanation" in lower or "### 3" in lower or "3." in lower)
    return detect, explain


def main() -> None:
    os.makedirs("results", exist_ok=True)

    ubsan_text = read_text("tool_results/ubsan_results.txt")
    clang_warn_text = read_text("tool_results/clang_warnings.txt")
    clang_tidy_text = read_text("tool_results/clang_tidy_results.txt")
    cppcheck_text = read_text("tool_results/cppcheck_results.txt")

    results: dict[str, dict[str, object]] = {}

    for program, ub_type in PROGRAM_INFO.items():
        llm_path = Path(f"llm_results/llm_{program}.txt")
        llm_text = read_text(str(llm_path))
        llm_detect, llm_explain = parse_llm_detection(llm_text)

        results[program] = {
            "ub_type": ub_type,
            "ubsan": parse_ubsan(ubsan_text, program),
            "clang_warn": parse_tool_section(clang_warn_text, program, CLANG_WARN_PATTERNS),
            "clang_tidy": parse_tool_section(clang_tidy_text, program, CLANG_TIDY_PATTERNS),
            "cppcheck": parse_cppcheck(cppcheck_text, program),
            "llm_detect": llm_detect,
            "llm_explain": llm_explain,
        }

    with open("results/comparison_table.csv", "w", newline="", encoding="utf-8") as f_csv:
        writer = csv.writer(f_csv)
        writer.writerow([
            "Program",
            "UB Type",
            "UBSan",
            "Clang Warnings",
            "clang-tidy",
            "cppcheck",
            "LLM Detection",
            "LLM Explanation",
        ])
        for prog, data in results.items():
            writer.writerow([
                prog,
                data["ub_type"],
                bool_to_symbol(bool(data["ubsan"])),
                bool_to_symbol(bool(data["clang_warn"])),
                bool_to_symbol(bool(data["clang_tidy"])),
                bool_to_symbol(bool(data["cppcheck"])),
                bool_to_symbol(bool(data["llm_detect"])),
                bool_to_symbol(bool(data["llm_explain"])),
            ])

    with open("results/comparison_table.md", "w", encoding="utf-8") as f_md:
        f_md.write("# UB Detection Tool Comparison\n\n")
        f_md.write("| Program | UB Type | UBSan | Clang Warn | clang-tidy | cppcheck | LLM Detect | LLM Explain |\n")
        f_md.write("|---------|---------|-------|------------|------------|----------|------------|-------------|\n")
        for prog, data in results.items():
            f_md.write(
                f"| {prog} | {data['ub_type']} | {bool_to_symbol(bool(data['ubsan']))} | {bool_to_symbol(bool(data['clang_warn']))} | {bool_to_symbol(bool(data['clang_tidy']))} | {bool_to_symbol(bool(data['cppcheck']))} | {bool_to_symbol(bool(data['llm_detect']))} | {bool_to_symbol(bool(data['llm_explain']))} |\n"
            )

        ub_programs = [name for name, data in results.items() if data["ub_type"] != "None (Safe)"]
        total = len(ub_programs)
        f_md.write("\n## Summary\n\n")
        f_md.write(f"Total UB programs: {total}\n\n")
        for tool, key in [
            ("UBSan", "ubsan"),
            ("Clang Warnings", "clang_warn"),
            ("clang-tidy", "clang_tidy"),
            ("cppcheck", "cppcheck"),
            ("LLM", "llm_detect"),
        ]:
            detected = sum(1 for name in ub_programs if bool(results[name][key]))
            percent = int((100 * detected) / total) if total else 0
            f_md.write(f"- **{tool}**: {detected}/{total} detected ({percent}%)\n")

    print("Comparison table saved to results/")


if __name__ == "__main__":
    main()
