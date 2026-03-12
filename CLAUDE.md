# ClaudeStudentPrep — Project Context

## What This Project Does
An AI-powered study system that transforms lecture PDFs into structured exam preparation materials using the local Claude Code CLI (no API key required).

## Architecture (single-pipeline)
```
PDF → src/pdf_extractor.py → src/ai_processor.py → src/response_parser.py → src/output_writer.py → modules/<name>/
```

## Entry Point
```bash
python process_lecture.py <pdf_path> <module_name> [--output-dir DIR]
```

## Key Files
- `process_lecture.py` — CLI entry point, orchestrates the pipeline
- `src/pdf_extractor.py` — `extract_pdf(path) -> str` using PyMuPDF
- `src/ai_processor.py` — `call_claude(text) -> str` using local `claude` CLI via subprocess
- `src/response_parser.py` — `parse_sections(response) -> dict` using regex
- `src/output_writer.py` — `write_outputs(sections, module, dir)` creates module folder structure
- `prompts/summarization.txt` — Master prompt; uses `{PDF_TEXT}` placeholder; returns 7 labeled sections

## AI Response Format
The master prompt instructs Claude to return sections delimited by `### SECTION_NAME ###` markers:
`LECTURE_SUMMARY`, `KEY_CONCEPTS`, `FORMULAS`, `CHEAT_SHEET`, `PRACTICE_EXAM`, `SOLUTIONS`, `HELPER_TOOL`

## Output Structure (per module)
```
modules/<module>/
  docs/   lecture-summary.md  key-concepts.md  cheat-sheet.md
  exams/  practice-exam.md    solutions.md
  formulas/ formulas.md
  tools/  calculator.html (or .py)
  input/  (drop PDFs here)
```

## Environment
- Requires `claude` CLI to be installed and authenticated (Claude Code)
- Dependencies: `PyMuPDF`

## Branch
Active development branch: `claude/ai-exam-prep-system-5Pc0f`

## Example Module
See `modules/example-statistics/` for realistic demo output showing all 7 artifacts.
