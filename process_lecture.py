#!/usr/bin/env python3
"""ClaudeStudentPrep — transform a lecture PDF into structured study materials.

Usage:
    python process_lecture.py <pdf_path> <module_name> [--output-dir DIR]

Examples:
    python process_lecture.py lectures/stats101.pdf statistics
    python process_lecture.py ~/Downloads/ml-week3.pdf machine-learning
    python process_lecture.py slides.pdf cyber-security --output-dir ./my-output
"""

import argparse
import sys

from src.pdf_extractor import extract_pdf
from src.ai_processor import call_claude
from src.response_parser import parse_sections
from src.output_writer import write_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transform a lecture PDF into AI-generated exam prep materials.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "pdf_path",
        help="Path to the lecture PDF file.",
    )
    parser.add_argument(
        "module_name",
        help='Module name slug, e.g. "statistics" or "machine-learning".',
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Override the default output directory (default: modules/<module_name>/).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print(f"\nClaudeStudentPrep — processing: {args.pdf_path}")
    print(f"Module: {args.module_name}\n")

    # Step 1 — Extract PDF
    print("[1/4] Extracting PDF text...")
    try:
        pdf_text = extract_pdf(args.pdf_path)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        sys.exit(f"ERROR (PDF extraction): {exc}")
    print(f"      Extracted {len(pdf_text):,} characters from PDF.")

    # Step 2 — Call Claude (local CLI)
    print("[2/4] Running Claude (local)...")
    try:
        ai_response = call_claude(pdf_text)
    except (FileNotFoundError, RuntimeError) as exc:
        sys.exit(f"ERROR (AI processing): {exc}")
    print(f"      Received {len(ai_response):,} character response.")

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
