#!/usr/bin/env python3
import glob
import os
import time
import requests


MODEL = os.environ.get("LLM_MODEL", "gemini-2.5-flash")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

# No embedded API keys. Always set GEMINI_API_KEY_1/2/3 in the environment.
DEFAULT_GEMINI_API_KEY_1 = ""
DEFAULT_GEMINI_API_KEY_2 = ""
DEFAULT_GEMINI_API_KEY_3 = ""

PROMPT_TEMPLATE = """You are an expert C/C++ compiler engineer specializing in undefined behaviour analysis.

Analyze the following C program carefully:

{code}

Please answer the following questions:

1. DETECTION: Does this program contain undefined behaviour (UB)? Answer YES or NO.
2. IDENTIFICATION: If YES, identify exactly which line(s) contain UB and what type of UB it is.
3. EXPLANATION: Explain WHY this is UB according to the C standard.
4. LLVM OPTIMIZATION: How might LLVM/Clang legally optimize this code based on UB assumptions?
5. SEVERITY: Rate the severity: Low / Medium / High / Critical.
6. FIX: Show corrected code.
"""


def query_with_key(api_key: str, code: str) -> str:
	payload = {
		"contents": [
			{
				"parts": [
					{
						"text": PROMPT_TEMPLATE.format(code=code)
					}
				]
			}
		],
		"generationConfig": {
			"temperature": 0.2,
			"maxOutputTokens": 2048
		}
	}

	url = GEMINI_API_URL.format(model=MODEL)
	response = requests.post(url, params={"key": api_key}, json=payload, timeout=90)

	if response.status_code != 200:
		raise RuntimeError(f"HTTP {response.status_code}: {response.text[:300]}")

	data = response.json()
	candidates = data.get("candidates", [])
	if not candidates:
		raise RuntimeError(f"No candidates in response: {data}")

	parts = candidates[0].get("content", {}).get("parts", [])
	text_chunks = [part.get("text", "") for part in parts if "text" in part]
	text = "\n".join(chunk for chunk in text_chunks if chunk.strip())
	if not text:
		raise RuntimeError(f"Empty text response: {data}")
	return text


def query_llm_with_fallback(code: str, api_keys: list[str]) -> str:
	last_error = None
	for idx, key in enumerate(api_keys, start=1):
		if not key:
			continue

		max_attempts = 3
		for attempt in range(1, max_attempts + 1):
			try:
				print(f"Trying API key #{idx} (attempt {attempt}/{max_attempts})...")
				return query_with_key(key, code)
			except Exception as exc:
				last_error = exc
				print(f"Key #{idx} failed on attempt {attempt}: {exc}")

				# Retry only for likely transient overload/rate-limit errors.
				error_text = str(exc)
				if "HTTP 503" in error_text or "HTTP 429" in error_text:
					if attempt < max_attempts:
						time.sleep(3 * attempt)
						continue
				break

	raise RuntimeError(f"All Gemini API keys failed. Last error: {last_error}")


def main() -> None:
	api_key_1 = os.environ.get("GEMINI_API_KEY_1", DEFAULT_GEMINI_API_KEY_1).strip()
	api_key_2 = os.environ.get("GEMINI_API_KEY_2", DEFAULT_GEMINI_API_KEY_2).strip()
	api_key_3 = os.environ.get("GEMINI_API_KEY_3", DEFAULT_GEMINI_API_KEY_3).strip()
	api_keys = [api_key_1, api_key_2, api_key_3]

	if not any(api_keys):
		raise SystemExit("Set GEMINI_API_KEY_1/2/3 before running this script.")

	os.makedirs("llm_results", exist_ok=True)

	c_files = sorted(glob.glob("testcases/*.c") + glob.glob("testcases/safe_programs/*.c"))
	if not c_files:
		raise SystemExit("No benchmark .c files found.")

	for filepath in c_files:
		prog_name = os.path.basename(filepath).replace(".c", "")
		output_file = f"llm_results/llm_{prog_name}.txt"

		if os.path.exists(output_file):
			print(f"Skipping {prog_name} (already done)")
			continue

		print(f"Querying Gemini for: {prog_name} (model: {MODEL})")
		with open(filepath, "r", encoding="utf-8") as f_in:
			code = f_in.read()

		try:
			result = query_llm_with_fallback(code, api_keys)
		except Exception as exc:
			with open(output_file, "w", encoding="utf-8") as f_out:
				f_out.write(f"=== LLM Analysis: {prog_name} ===\n")
				f_out.write(f"=== Model: {MODEL} ===\n\n")
				f_out.write(f"ERROR: {exc}\n")
			print(f"Failed for {prog_name}; wrote error to {output_file}")
			continue

		with open(output_file, "w", encoding="utf-8") as f_out:
			f_out.write(f"=== LLM Analysis: {prog_name} ===\n")
			f_out.write(f"=== Model: {MODEL} ===\n\n")
			f_out.write(result)

		print(f"Saved to {output_file}")
		time.sleep(1)

	print("LLM querying complete.")


if __name__ == "__main__":
	main()
