"""Send lecture text to Claude (local claude CLI) and return the structured response."""

import os
import subprocess

PROMPT_FILE = os.path.join(os.path.dirname(__file__), "..", "prompts", "summarization.txt")


def call_claude(pdf_text: str) -> str:
    """Send the extracted PDF text to the local claude CLI and return the full response.

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
        result = subprocess.run(
            ["claude", "-p", full_prompt],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "claude CLI not found. "
            "Ensure Claude Code is installed and available on your PATH."
        )

    if result.returncode != 0:
        raise RuntimeError(
            f"claude CLI exited with code {result.returncode}:\n{result.stderr.strip()}"
        )

    return result.stdout
