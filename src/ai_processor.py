"""Send lecture text to Claude and return the structured response."""

import os

import anthropic

PROMPT_FILE = os.path.join(os.path.dirname(__file__), "..", "prompts", "summarization.txt")
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 8192


def call_claude(pdf_text: str, api_key: str) -> str:
    """Send the extracted PDF text to Claude and return the full response.

    Args:
        pdf_text: Text extracted from the lecture PDF.
        api_key:  Anthropic API key.

    Returns:
        Raw text response from Claude containing all labeled sections.

    Raises:
        FileNotFoundError: If the prompt template file is missing.
        RuntimeError: On any Anthropic API error (wraps the original).
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

    client = anthropic.Anthropic(api_key=api_key)

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": full_prompt}],
        )
    except anthropic.AuthenticationError as exc:
        raise RuntimeError(
            "Invalid Anthropic API key. "
            "Check that ANTHROPIC_API_KEY in your .env file is correct."
        ) from exc
    except anthropic.RateLimitError as exc:
        raise RuntimeError(
            "Anthropic API rate limit reached. "
            "Wait a moment and try again."
        ) from exc
    except anthropic.APIStatusError as exc:
        raise RuntimeError(
            f"Anthropic API error (HTTP {exc.status_code}): {exc.message}"
        ) from exc

    return response.content[0].text
