"""Parse the structured AI response (JSON) into named sections."""

import json
import re

SECTION_NAMES = [
    "LECTURE_SUMMARY",
    "KEY_CONCEPTS",
    "FORMULAS",
    "CHEAT_SHEET",
    "PRACTICE_EXAM",
    "SOLUTIONS",
    "HELPER_TOOL",
]

# Required sections — missing both means the response is unusable
REQUIRED_SECTIONS = {"LECTURE_SUMMARY", "KEY_CONCEPTS"}

# Sections that are legitimately absent for non-mathematical lectures
OPTIONAL_SECTIONS = {"FORMULAS", "HELPER_TOOL"}


def parse_sections(ai_response: str) -> dict:
    """Parse a JSON AI response into named content sections.

    The response is expected to be a JSON object whose keys are section names.
    Markdown code fences (```json ... ```) are stripped if present.

    Args:
        ai_response: The raw text returned by the AI model.

    Returns:
        Dictionary mapping section name to content string.
        Sections whose value is exactly "N/A" are excluded.

    Raises:
        ValueError: If the response is not valid JSON, contains no recognisable
                    sections, or if both LECTURE_SUMMARY and KEY_CONCEPTS are
                    missing.
    """
    raw = ai_response.strip()

    # Strip markdown code fences if Claude wrapped the JSON
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        snippet = ai_response[:500].replace("\n", " ")
        raise ValueError(
            f"AI response is not valid JSON: {exc}\n"
            f"Response preview: {snippet!r}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected a JSON object at the top level, got {type(data).__name__}."
        )

    # Normalise keys to uppercase and keep only known sections
    sections = {}
    for key, value in data.items():
        upper = key.upper()
        if upper in SECTION_NAMES:
            sections[upper] = str(value).strip()

    if not sections:
        snippet = ai_response[:500].replace("\n", " ")
        raise ValueError(
            "JSON response contained no recognised section keys. "
            f"Response preview: {snippet!r}"
        )

    # Filter out N/A sections
    sections = {k: v for k, v in sections.items() if v.upper() != "N/A"}

    # Warn about missing optional sections
    for name in OPTIONAL_SECTIONS:
        if name not in sections:
            print(f"  INFO: Section {name} is N/A or absent — skipping.")

    # Check required sections
    missing_required = REQUIRED_SECTIONS - set(sections.keys())
    if missing_required == REQUIRED_SECTIONS:
        snippet = ai_response[:500].replace("\n", " ")
        raise ValueError(
            f"Core sections {REQUIRED_SECTIONS} are both missing from the AI response. "
            f"Response preview: {snippet!r}"
        )
    if missing_required:
        print(f"  WARNING: Required section(s) missing: {missing_required}")

    return sections
