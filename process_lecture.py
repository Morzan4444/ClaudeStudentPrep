#!/usr/bin/env python3
"""ClaudeStudentPrep — transform a lecture PDF into structured study materials.

Usage:
    python process_lecture.py <module_name> [pdf_path] [--output-dir DIR]

Examples:
    python process_lecture.py statistics
        (auto-discovers PDF in modules/statistics/input/)
    python process_lecture.py statistics lectures/stats101.pdf
    python process_lecture.py machine-learning ~/Downloads/ml-week3.pdf
    python process_lecture.py cyber-security slides.pdf --output-dir ./my-output
"""

import argparse
import glob
import os
import sys

from src.pdf_extractor import extract_pdf
from src.ai_processor import call_claude
from src.response_parser import parse_sections
from src.output_writer import write_outputs


def find_pdf_in_module(module_name: str) -> str:
    """Auto-discover a PDF inside modules/<module_name>/input/."""
    input_dir = os.path.join("modules", module_name, "input")
    matches = glob.glob(os.path.join(input_dir, "*.pdf"))
    if not matches:
        sys.exit(
            f"ERROR: No PDF found in {input_dir}/\n"
            f"  Drop a PDF there, or pass the path explicitly:\n"
            f"  python process_lecture.py {module_name} path/to/lecture.pdf"
        )
    if len(matches) > 1:
        sys.exit(
            f"ERROR: Multiple PDFs found in {input_dir}/\n"
            f"  Specify which one to use:\n"
            f"  python process_lecture.py {module_name} path/to/lecture.pdf"
        )
    return matches[0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transform a lecture PDF into AI-generated exam prep materials.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "module_name",
        help='Module name slug, e.g. "statistics" or "machine-learning".',
    )
    parser.add_argument(
        "pdf_path",
        nargs="?",
        default=None,
        help=(
            "Path to the lecture PDF. "
            "If omitted, auto-discovered from modules/<module_name>/input/"
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Override the default output directory (default: modules/<module_name>/).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    pdf_path = args.pdf_path or find_pdf_in_module(args.module_name)

    print(f"\nClaudeStudentPrep — processing: {pdf_path}")
    print(f"Module: {args.module_name}\n")

    # Step 1 — Extract PDF
    print("[1/4] Extracting PDF text...")
    try:
        pdf_text = extract_pdf(pdf_path)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        sys.exit(f"ERROR (PDF extraction): {exc}")
    print(f"      Extracted {len(pdf_text):,} characters from PDF.")

    # Step 2 — Call Claude (local CLI, streams output live)
    print("[2/4] Running Claude (local) — streaming response:\n")
    try:
        ai_response = call_claude(pdf_text)
    except (FileNotFoundError, RuntimeError) as exc:
        sys.exit(f"ERROR (AI processing): {exc}")
    print(f"\n      Received {len(ai_response):,} character response.")

    # Step 3 — Parse sections
    print("[3/4] Parsing AI response sections...")
    try:
        sections = parse_sections(ai_response)
    except ValueError as exc:
        sys.exit(f"ERROR (response parsing): {exc}")
    print(f"      Found {len(sections)} section(s): {', '.join(sections.keys())}")

    # Step 4 — Write output files
    print("[4/4] Writing output files...")
    try:
        written = write_outputs(sections, args.module_name, args.output_dir)
    except (PermissionError, OSError) as exc:
        sys.exit(f"ERROR (file writing): {exc}")

    print(f"\nDone! {len(written)} file(s) created:")
    for path in written:
        print(f"  {path}")
    print()


if __name__ == "__main__":
    main()
