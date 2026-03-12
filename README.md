# ClaudeStudentPrep

An AI-powered study system that transforms lecture PDFs into complete exam preparation materials using Claude AI.

Drop in a lecture PDF and get back:
- Structured lecture summary
- Key concepts & definitions glossary
- Extracted formulas
- Condensed cheat sheet
- Realistic practice exam
- Full solutions
- Interactive formula calculator (HTML)

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up your API key
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
# Get one at: https://console.anthropic.com/
```

### 3. Add your lecture PDF
```
modules/my-module/input/lecture.pdf
```
(Create the folder, or let the tool create it automatically.)

### 4. Run the processor
```bash
python process_lecture.py modules/my-module/input/lecture.pdf my-module
```

### 5. Find your study materials
```
modules/my-module/
├── docs/
│   ├── lecture-summary.md     ← Structured overview
│   ├── key-concepts.md        ← Glossary with examples
│   └── cheat-sheet.md         ← Quick-reference table
├── exams/
│   ├── practice-exam.md       ← 10-question realistic exam
│   └── solutions.md           ← Full step-by-step solutions
├── formulas/
│   └── formulas.md            ← All formulas with explanations
└── tools/
    └── calculator.html        ← Offline formula calculator
```

---

## Example Output

See [`modules/example-statistics/`](modules/example-statistics/) for a complete example showing all output artifacts for an introductory statistics lecture.

Open the calculator directly in your browser:
```
modules/example-statistics/tools/calculator.html
```

---

## Project Structure

```
ClaudeStudentPrep/
├── process_lecture.py      # Main CLI script
├── requirements.txt
├── .env.example
├── src/
│   ├── pdf_extractor.py    # PDF text extraction (PyMuPDF)
│   ├── ai_processor.py     # Claude API call
│   ├── response_parser.py  # Parse AI response sections
│   └── output_writer.py    # Write files to module folder
├── prompts/
│   ├── summarization.txt   # Master AI prompt (all 7 sections)
│   └── ...                 # Standalone prompts for future use
├── templates/              # Markdown file headers
└── modules/
    └── example-statistics/ # Demo module with example outputs
```

---

## Supported Modules

Any subject works. Name your module folder anything:
```
modules/machine-learning/
modules/cyber-security/
modules/econometrics/
modules/statistics/
```

---

## Requirements

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/)
- A text-based PDF (scanned image-only PDFs require OCR pre-processing)

---

## Pipeline

```
PDF file
  └─→ [1/4] pdf_extractor.py  — extracts text with PyMuPDF
  └─→ [2/4] ai_processor.py   — sends to Claude (claude-sonnet-4-6)
  └─→ [3/4] response_parser.py — splits response into 7 labeled sections
  └─→ [4/4] output_writer.py  — saves each section to correct file
```

One API call generates all seven study artifacts simultaneously.

---

## Extending the System

| Idea | How |
|---|---|
| Add a new output section | Add marker to `prompts/summarization.txt` and a new entry in `src/output_writer.py:SECTION_MAP` |
| Change AI model | Edit `MODEL` in `src/ai_processor.py` |
| Batch process a folder | Wrap `process_lecture.py` in a shell loop |
| Re-run only one section | Use standalone prompts in `prompts/` with the Anthropic API directly |
| Support scanned PDFs | Pre-process with `ocrmypdf` or Adobe Acrobat before running |
