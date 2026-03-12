"""Parse the structured AI response into named sections."""

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
    """Split an AI response into named content sections.

    The parser attempts three strategies in order:
      1. Strict:  ### SECTION_NAME ### markers (primary format)
      2. Loose:   ## SECTION_NAME or # SECTION_NAME markdown headers
      3. Prefix:  SECTION_NAME: on its own line

    Args:
        ai_response: The raw text returned by the AI model.

    Returns:
        Dictionary mapping section name to content string.
        Sections whose content is exactly "N/A" are excluded.

    Raises:
        ValueError: If no sections can be parsed at all, or if both
                    LECTURE_SUMMARY and KEY_CONCEPTS are missing.
    """
    sections = (
        _parse_strict(ai_response)
        or _parse_loose_headers(ai_response)
        or _parse_prefix(ai_response)
    )

    if not sections:
        snippet = ai_response[:500].replace("\n", " ")
        raise ValueError(
            "Could not parse any sections from the AI response. "
            f"Response preview: {snippet!r}"
        )

    # Filter out N/A sections
    sections = {k: v for k, v in sections.items() if v.strip().upper() != "N/A"}

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


# ---------------------------------------------------------------------------
# Strategy 1: ### SECTION_NAME ### markers
# ---------------------------------------------------------------------------

_STRICT_NAMES_PATTERN = "|".join(SECTION_NAMES + ["END"])
_STRICT_RE = re.compile(
    r"###\s*(" + "|".join(SECTION_NAMES) + r")\s*###\s*\n(.*?)"
    r"(?=###\s*(?:" + _STRICT_NAMES_PATTERN + r")\s*###|\Z)",
    re.DOTALL | re.IGNORECASE,
)


def _parse_strict(text: str) -> dict:
    matches = _STRICT_RE.findall(text)
    if not matches:
        return {}
    return {name.upper(): content.strip() for name, content in matches}


# ---------------------------------------------------------------------------
# Strategy 2: ## SECTION_NAME or # SECTION_NAME markdown headers
# ---------------------------------------------------------------------------

_LOOSE_RE = re.compile(
    r"##?\s*(" + "|".join(SECTION_NAMES) + r")\s*\n(.*?)"
    r"(?=##?\s*(?:" + "|".join(SECTION_NAMES) + r")\s*\n|\Z)",
    re.DOTALL | re.IGNORECASE,
)


def _parse_loose_headers(text: str) -> dict:
    matches = _LOOSE_RE.findall(text)
    if not matches:
        return {}
    return {name.upper(): content.strip() for name, content in matches}


# ---------------------------------------------------------------------------
# Strategy 3: SECTION_NAME: prefix on its own line
# ---------------------------------------------------------------------------

_PREFIX_RE = re.compile(
    r"^(" + "|".join(SECTION_NAMES) + r"):\s*\n(.*?)"
    r"(?=^(?:" + "|".join(SECTION_NAMES) + r"):\s*\n|\Z)",
    re.DOTALL | re.IGNORECASE | re.MULTILINE,
)


def _parse_prefix(text: str) -> dict:
    matches = _PREFIX_RE.findall(text)
    if not matches:
        return {}
    return {name.upper(): content.strip() for name, content in matches}
