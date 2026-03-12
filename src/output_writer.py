"""Write parsed AI sections to the correct files in the module folder."""

import os
from datetime import datetime

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

# Maps AI section name → (subdirectory, filename, template_file)
SECTION_MAP = {
    "LECTURE_SUMMARY": ("docs", "lecture-summary.md", "lecture_summary.md"),
    "KEY_CONCEPTS":    ("docs", "key-concepts.md",    "lecture_summary.md"),
    "CHEAT_SHEET":     ("docs", "cheat-sheet.md",     "cheat_sheet.md"),
    "PRACTICE_EXAM":   ("exams", "practice-exam.md",  "exam.md"),
    "SOLUTIONS":       ("exams", "solutions.md",       "solutions.md"),
    "FORMULAS":        ("formulas", "formulas.md",     "lecture_summary.md"),
    "HELPER_TOOL":     ("tools", None,                 None),  # filename determined at runtime
}

MODULE_SUBDIRS = ["docs", "exams", "formulas", "tools", "input"]


def slugify(name: str) -> str:
    """Convert a module name to a lowercase, hyphenated slug."""
    return name.strip().lower().replace(" ", "-").replace("_", "-")


def write_outputs(
    sections: dict,
    module_name: str,
    output_dir: str | None = None,
) -> list[str]:
    """Write each parsed section to the appropriate file.

    Args:
        sections:    Dict of section_name -> content from response_parser.
        module_name: The module slug (e.g. "statistics", "machine-learning").
        output_dir:  Optional override for the base output directory.
                     Defaults to modules/<module_name>/.

    Returns:
        List of file paths that were written.
    """
    slug = slugify(module_name)
    base = output_dir if output_dir else os.path.join("modules", slug)

    # Create all subdirectories
    for subdir in MODULE_SUBDIRS:
        os.makedirs(os.path.join(base, subdir), exist_ok=True)

    # Place a .gitkeep in input/ so the folder is tracked by git
    gitkeep_path = os.path.join(base, "input", ".gitkeep")
    if not os.path.exists(gitkeep_path):
        open(gitkeep_path, "w").close()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    written = []

    for section_name, content in sections.items():
        if section_name not in SECTION_MAP:
            print(f"  INFO: Unknown section '{section_name}' — skipping.")
            continue

        subdir, filename, template_file = SECTION_MAP[section_name]

        # Determine filename for HELPER_TOOL based on content type
        if section_name == "HELPER_TOOL":
            content_lower = content.lstrip()
            if content_lower.startswith("<!DOCTYPE") or content_lower.startswith("<html"):
                filename = "calculator.html"
            else:
                filename = "calculator.py"

        file_path = os.path.join(base, subdir, filename)

        # Build header from template
        header = _load_template(
            template_file,
            module_name=slug,
            pdf_filename="(see input/ folder)",
            timestamp=timestamp,
        ) if template_file else ""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(header + content + "\n")

        print(f"  Wrote: {file_path}")
        written.append(file_path)

    return written


def _load_template(
    template_file: str,
    module_name: str,
    pdf_filename: str,
    timestamp: str,
) -> str:
    """Load a template file and substitute placeholders."""
    path = os.path.join(TEMPLATES_DIR, template_file)
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        template = f.read()
    return template.format(
        module_name=module_name,
        pdf_filename=pdf_filename,
        timestamp=timestamp,
    )
