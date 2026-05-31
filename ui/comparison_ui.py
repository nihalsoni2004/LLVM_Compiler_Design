#!/usr/bin/env python3
import os
import re
import shutil
import subprocess
import tempfile
from html import escape
from typing import Dict, List, Tuple

import pandas as pd
import requests
import streamlit as st

MODEL = "gemini-2.5-flash"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

# No embedded API keys. Set GEMINI_API_KEY_1/2/3 in the environment instead.
DEFAULT_GEMINI_API_KEY_1 = ""
DEFAULT_GEMINI_API_KEY_2 = ""
DEFAULT_GEMINI_API_KEY_3 = ""

LLM_PROMPT = """You are an expert C/C++ compiler engineer specializing in undefined behaviour analysis.

Analyze the following C/C++ program carefully:

{code}

Please answer the following:
1. DETECTION: Does this program contain undefined behaviour (UB)? YES or NO.
2. IDENTIFICATION: Which line(s) and what type of UB?
3. EXPLANATION: Why this is UB according to C/C++ rules?
4. LLVM OPTIMIZATION: How LLVM/Clang may optimize under UB assumptions?
5. SEVERITY: Low / Medium / High / Critical.
6. FIX: Provide corrected code.
"""


def run_cmd(cmd: List[str], timeout: int = 30) -> Tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout
    except FileNotFoundError:
        return 127, f"Command not found: {cmd[0]}"
    except subprocess.TimeoutExpired as exc:
        partial = exc.stdout or ""
        return 124, f"Command timed out after {timeout}s\n{partial}"


def summarize_diagnostics(output: str, max_lines: int = 8) -> str:
    lines = []
    for line in output.splitlines():
        ll = line.lower()
        if (
            "error:" in ll
            or "warning:" in ll
            or "runtime error:" in ll
            or "addresssanitizer" in ll
            or "portability:" in ll
            or "style:" in ll
        ):
            lines.append(line.strip())
    if not lines:
        return "No explicit diagnostics captured."
    return "\n".join(lines[:max_lines])


def summarize_llm_findings(output: str) -> str:
    ll = output.lower()
    if ll.startswith("error:"):
        return output

    # Prefer explicit sections from the model answer.
    extracted = []
    for line in output.splitlines():
        l = line.strip()
        low = l.lower()
        if (
            "detection" in low
            or "identification" in low
            or "severity" in low
            or ("yes" in low and "detection" not in low and len(low) <= 20)
            or ("no" in low and "detection" not in low and len(low) <= 20)
        ):
            extracted.append(l)

    if extracted:
        return "\n".join(extracted[:8])

    # Fallback: show first meaningful lines.
    non_empty = [l.strip() for l in output.splitlines() if l.strip()]
    if not non_empty:
        return "No LLM output captured."
    return "\n".join(non_empty[:8])


def detect_ubsan(output: str) -> bool:
    ll = output.lower()
    return (
        "runtime error:" in ll
        or "undefinedbehaviorsanitizer" in ll
        or "addresssanitizer" in ll
        or "deadlysignal" in ll
    )


def detect_clang_warnings(output: str) -> bool:
    ll = output.lower()
    return "warning:" in ll or "error:" in ll


def detect_clang_tidy(output: str) -> bool:
    ll = output.lower()
    return "warning:" in ll or "error:" in ll


def detect_cppcheck(output: str) -> bool:
    ll = output.lower()
    return "error:" in ll or "warning:" in ll


def render_key_status(statuses: List[str], sidebar_placeholder) -> None:
    styles = {
        "pending": ("PENDING", "#6b7280"),
        "working": ("RUNNING", "#0ea5e9"),
        "failed": ("FAILED", "#ef4444"),
        "success": ("SUCCESS", "#22c55e"),
        "skipped": ("SKIPPED", "#a3a3a3"),
    }
    rows = []
    for idx, status in enumerate(statuses, start=1):
        label, color = styles.get(status, ("PENDING", "#6b7280"))
        symbol = "●"
        rows.append(
            f"<div class='key-row'><span class='dot' style='color:{color}'>{symbol}</span>"
            f"<span class='key-name'>Key {idx}</span><span class='key-badge' style='border-color:{color};color:{color}'>{label}</span></div>"
        )
    sidebar_placeholder.markdown("\n".join(rows), unsafe_allow_html=True)


def render_scroll_table(df: pd.DataFrame) -> None:
    headers = "".join(f"<th>{escape(str(col))}</th>" for col in df.columns)
    body_rows = []
    for _, row in df.iterrows():
        tds = []
        for col in df.columns:
            val = "" if pd.isna(row[col]) else str(row[col])
            if col == "Key Errors/Findings":
                tds.append(f"<td class='findings-cell'>{escape(val)}</td>")
            else:
                tds.append(f"<td>{escape(val)}</td>")
        body_rows.append("<tr>" + "".join(tds) + "</tr>")

    html = (
        "<div class='table-wrap'><table class='cmp-table'>"
        f"<thead><tr>{headers}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table></div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def gemini_query_with_fallback(code: str, api_keys: List[str], status_callback=None) -> str:
    payload = {
        "contents": [{"parts": [{"text": LLM_PROMPT.format(code=code)}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048},
    }

    last_error = None
    for idx, key in enumerate(api_keys, start=1):
        if not key:
            if status_callback:
                status_callback(idx - 1, "skipped")
            continue
        if status_callback:
            status_callback(idx - 1, "working")
        for attempt in range(1, 4):
            try:
                url = GEMINI_API_URL.format(model=MODEL)
                resp = requests.post(url, params={"key": key}, json=payload, timeout=90)
                if resp.status_code != 200:
                    raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")
                data = resp.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    raise RuntimeError(f"No candidates in response: {data}")
                parts = candidates[0].get("content", {}).get("parts", [])
                text = "\n".join(p.get("text", "") for p in parts if "text" in p).strip()
                if not text:
                    raise RuntimeError("Empty response text from Gemini")
                if status_callback:
                    status_callback(idx - 1, "success")
                return text
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if ("HTTP 503" in str(exc) or "HTTP 429" in str(exc)) and attempt < 3:
                    continue
                if status_callback:
                    status_callback(idx - 1, "failed")
                break

    raise RuntimeError(f"All Gemini keys failed. Last error: {last_error}")


def detect_llm_yes_no(text: str) -> Tuple[bool, str]:
    ll = text.lower()
    if "detection" in ll:
        m = re.search(r"detection[\s\S]{0,120}?(yes|no)", ll)
        if m:
            return m.group(1) == "yes", m.group(1).upper()
    if "yes" in ll and "undefined" in ll:
        return True, "YES"
    if "no" in ll and "undefined" in ll:
        return False, "NO"
    return False, "UNKNOWN"


def ensure_tool_available(tool: str) -> bool:
    return shutil.which(tool) is not None


def main() -> None:
    st.set_page_config(page_title="UB 5-Way Comparator", layout="wide")

    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
        h1, h2, h3 {letter-spacing: 0.2px;}
        .app-subtitle {
            color: #334155;
            background: linear-gradient(90deg, #e2e8f0 0%, #f8fafc 100%);
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            padding: 0.7rem 0.9rem;
            margin-bottom: 0.8rem;
        }
        .table-wrap {
            overflow-x: auto;
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            background: #ffffff;
        }
        .cmp-table {
            border-collapse: collapse;
            min-width: 1300px;
            width: max-content;
            font-size: 0.92rem;
        }
        .cmp-table th, .cmp-table td {
            border-bottom: 1px solid #e2e8f0;
            padding: 10px 12px;
            text-align: left;
            vertical-align: top;
        }
        .cmp-table th {
            position: sticky;
            top: 0;
            z-index: 2;
            background: #f8fafc;
            font-weight: 700;
        }
        .findings-cell {
            min-width: 650px;
            white-space: pre-wrap;
            word-break: break-word;
        }
        .key-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            margin: 6px 0;
            padding: 8px 10px;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            background: #ffffff;
        }
        .dot {font-size: 13px;}
        .key-name {font-weight: 600; color: #0f172a; margin-right: auto; margin-left: 6px;}
        .key-badge {
            font-size: 0.76rem;
            font-weight: 700;
            padding: 2px 8px;
            border: 1px solid;
            border-radius: 999px;
            letter-spacing: 0.2px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("UB Analyzer: 5-Way Comparison")
    st.markdown(
        "<div class='app-subtitle'>Upload one C/C++ file and run a 5-way UB comparison: UBSan, Clang warnings, clang-tidy, cppcheck, and Gemini.</div>",
        unsafe_allow_html=True,
    )

    api_keys = [
        os.environ.get("GEMINI_API_KEY_1", DEFAULT_GEMINI_API_KEY_1).strip(),
        os.environ.get("GEMINI_API_KEY_2", DEFAULT_GEMINI_API_KEY_2).strip(),
        os.environ.get("GEMINI_API_KEY_3", DEFAULT_GEMINI_API_KEY_3).strip(),
    ]
    key_statuses = ["pending", "pending", "pending"]

    with st.sidebar:
        st.header("LLM Key Status")
        st.caption("Fallback order: Key 1 -> Key 2 -> Key 3")
        key_status_placeholder = st.empty()
        render_key_status(key_statuses, key_status_placeholder)
        st.markdown("---")
        st.caption("Model: gemini-2.5-flash")

    uploaded = st.file_uploader("Upload .c or .cpp file", type=["c", "cpp", "cc", "cxx"])
    run_btn = st.button("Run 5-way comparison", type="primary", disabled=uploaded is None)

    if not run_btn or uploaded is None:
        return

    required = ["clang", "clang-tidy", "cppcheck"]
    missing = [t for t in required if not ensure_tool_available(t)]
    if missing:
        st.error("Missing required tools: " + ", ".join(missing))
        st.stop()

    suffix = "." + uploaded.name.split(".")[-1].lower() if "." in uploaded.name else ".c"

    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "input" + suffix)
        with open(src_path, "wb") as f:
            f.write(uploaded.getbuffer())

        bin_path = os.path.join(tmpdir, "test_ubsan")
        rows: List[Dict[str, str]] = []
        raw_outputs: Dict[str, str] = {}

        # 1) UBSan
        rc_compile, out_compile = run_cmd([
            "clang",
            "-fsanitize=undefined,address",
            "-fno-omit-frame-pointer",
            "-g",
            "-O1",
            src_path,
            "-o",
            bin_path,
        ])

        if rc_compile == 0:
            rc_run, out_run = run_cmd([bin_path], timeout=8)
            ubsan_output = out_compile + "\n" + out_run
            detected = detect_ubsan(ubsan_output)
            status = f"Compile OK, run exit={rc_run}"
        else:
            ubsan_output = out_compile
            detected = False
            status = f"Compile failed (exit {rc_compile})"

        raw_outputs["UBSan"] = ubsan_output
        rows.append(
            {
                "Tool": "UBSan",
                "Detected UB": "YES" if detected else "NO",
                "Status": status,
                "Key Errors/Findings": summarize_diagnostics(ubsan_output),
            }
        )

        # 2) Clang warnings
        rc, out = run_cmd([
            "clang",
            "-Wall",
            "-Wextra",
            "-Weverything",
            "-Wno-padded",
            "-fsyntax-only",
            src_path,
        ])
        raw_outputs["Clang Warnings"] = out
        rows.append(
            {
                "Tool": "Clang Warnings",
                "Detected UB": "YES" if detect_clang_warnings(out) else "NO",
                "Status": f"Exit={rc}",
                "Key Errors/Findings": summarize_diagnostics(out),
            }
        )

        # 3) clang-tidy
        rc, out = run_cmd([
            "clang-tidy",
            src_path,
            "--checks=clang-analyzer-*,bugprone-*,cert-*,misc-*",
            "--",
            "-std=c11",
        ])
        raw_outputs["clang-tidy"] = out
        rows.append(
            {
                "Tool": "clang-tidy",
                "Detected UB": "YES" if detect_clang_tidy(out) else "NO",
                "Status": f"Exit={rc}",
                "Key Errors/Findings": summarize_diagnostics(out),
            }
        )

        # 4) cppcheck
        rc, out = run_cmd([
            "cppcheck",
            "--enable=all",
            "--std=c11",
            "--verbose",
            "--suppress=missingIncludeSystem",
            src_path,
        ])
        raw_outputs["cppcheck"] = out
        rows.append(
            {
                "Tool": "cppcheck",
                "Detected UB": "YES" if detect_cppcheck(out) else "NO",
                "Status": f"Exit={rc}",
                "Key Errors/Findings": summarize_diagnostics(out),
            }
        )

        # 5) LLM
        llm_output = ""
        llm_status = "Skipped"
        llm_detect = "NO"

        def on_key_status(index: int, status: str) -> None:
            key_statuses[index] = status
            render_key_status(key_statuses, key_status_placeholder)

        try:
            with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()
            llm_output = gemini_query_with_fallback(code, api_keys, status_callback=on_key_status)
            is_ub, det_label = detect_llm_yes_no(llm_output)
            llm_detect = "YES" if is_ub else ("NO" if det_label == "NO" else "UNKNOWN")
            llm_status = "OK"
        except Exception as exc:  # noqa: BLE001
            llm_output = f"ERROR: {exc}"
            llm_detect = "NO"
            llm_status = "Failed"

        raw_outputs["LLM (Gemini 2.5 Flash)"] = llm_output
        rows.append(
            {
                "Tool": "LLM (Gemini 2.5 Flash)",
                "Detected UB": llm_detect,
                "Status": llm_status,
                "Key Errors/Findings": summarize_llm_findings(llm_output) if llm_status == "OK" else llm_output,
            }
        )

    st.subheader("Final 5-Way Comparison")
    df = pd.DataFrame(rows)
    render_scroll_table(df)

    st.subheader("Full Findings (No Truncation)")
    for row in rows:
        st.markdown(f"**{row['Tool']}**")
        st.text_area(
            label=f"{row['Tool']} findings",
            value=row["Key Errors/Findings"],
            height=140,
            key=f"findings_{row['Tool']}",
            disabled=True,
        )

    st.subheader("Detailed Output (Clear Errors Per Tool)")
    for tool_name, output in raw_outputs.items():
        with st.expander(tool_name, expanded=False):
            st.code(output if output.strip() else "(no output)", language="text")


if __name__ == "__main__":
    main()
