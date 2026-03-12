"""Send lecture text to Claude (local claude CLI) and return the structured response."""

import hashlib
import json
import os
import subprocess

PROMPT_FILE = os.path.join(os.path.dirname(__file__), "..", "prompts", "summarization.txt")
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", ".cache")
MAX_TOKENS = 32768


def call_claude(pdf_text: str) -> str:
    """Send the extracted PDF text to the local claude CLI and stream the response.

    Streams Claude's output to stdout in real time (prefixed with spaces so it
    sits visually under the [2/4] step header), then returns the full response
    as a string. Responses are cached by content hash to avoid redundant calls.

    Args:
        pdf_text: Text extracted from the lecture PDF.

    Returns:
        Raw text response from Claude containing a JSON object with all sections.

    Raises:
        FileNotFoundError: If the prompt template file is missing.
        RuntimeError: If the claude CLI is not found or exits with an error.
    """
    prompt_path = os.path.normpath(PROMPT_FILE)
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(
            f"Prompt template not found at: {prompt_path}. "
            "Ensure the prompts/ directory is present."
        )

    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    full_prompt = prompt_template.replace("{PDF_TEXT}", pdf_text)

    # Cache lookup — skip AI call if we've seen this exact prompt before
    cache_key = hashlib.sha256(full_prompt.encode("utf-8")).hexdigest()
    cached = _load_cache(cache_key)
    if cached is not None:
        print("      (cache hit — skipping AI call)")
        return cached

    try:
        process = subprocess.Popen(
            ["claude", "-p", full_prompt, "--max-tokens", str(MAX_TOKENS)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "claude CLI not found. "
            "Ensure Claude Code is installed and available on your PATH."
        )

    output_parts = []
    for line in process.stdout:
        print(f"      {line}", end="", flush=True)
        output_parts.append(line)

    process.wait()

    if process.returncode != 0:
        stderr_text = process.stderr.read().strip()
        raise RuntimeError(
            f"claude CLI exited with code {process.returncode}:\n{stderr_text}"
        )

    response = "".join(output_parts)
    _save_cache(cache_key, response)
    return response


def _load_cache(key: str) -> str | None:
    path = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def _save_cache(key: str, response: str) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, f"{key}.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write(response)
