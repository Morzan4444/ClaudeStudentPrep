"""Send lecture text to Claude (local claude CLI) and return the structured response."""

import os
import subprocess
import sys

PROMPT_FILE = os.path.join(os.path.dirname(__file__), "..", "prompts", "summarization.txt")
MAX_TOKENS = 8192


def call_claude(pdf_text: str) -> str:
    """Send the extracted PDF text to the local claude CLI and stream the response.

    Streams Claude's output to stdout in real time (prefixed with spaces so it
    sits visually under the [2/4] step header), then returns the full response
    as a string.

    Args:
        pdf_text: Text extracted from the lecture PDF.

    Returns:
        Raw text response from Claude containing all labeled sections.

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

    return "".join(output_parts)
