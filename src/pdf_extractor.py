"""PDF text extraction using PyMuPDF (fitz)."""

import fitz  # PyMuPDF

MAX_PAGES = 80
MAX_CHARS = 150_000


def extract_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file.

    Args:
        pdf_path: Absolute or relative path to the PDF file.

    Returns:
        Extracted text with page separators.

    Raises:
        FileNotFoundError: If the PDF path does not exist.
        ValueError: If the file is not a PDF, is empty, or is image-only.
        RuntimeError: If the PDF is password-protected or corrupt.
    """
    import os

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if not pdf_path.lower().endswith(".pdf"):
        raise ValueError(f"File does not appear to be a PDF: {pdf_path}")

    try:
        doc = fitz.open(pdf_path)
    except fitz.errors.FitzError as exc:
        raise RuntimeError(
            f"Could not open PDF '{pdf_path}'. "
            "It may be password-protected or corrupt."
        ) from exc

    if doc.needs_pass:
        raise RuntimeError(
            f"PDF '{pdf_path}' is password-protected. "
            "Please unlock it before processing."
        )

    total_pages = len(doc)
    pages_to_read = min(total_pages, MAX_PAGES)

    if total_pages > MAX_PAGES:
        print(
            f"  WARNING: PDF has {total_pages} pages. "
            f"Processing first {MAX_PAGES} pages only."
        )

    page_texts = []
    for i in range(pages_to_read):
        page = doc[i]
        text = page.get_text("text")
        if text.strip():
            page_texts.append(f"--- Page {i + 1} ---\n{text.strip()}")

    doc.close()

    combined = "\n\n".join(page_texts)

    if len(combined.strip()) < 100:
        raise ValueError(
            "PDF appears to be empty or image-only — no extractable text found. "
            "If this is a scanned document, run it through an OCR tool first "
            "(e.g. Adobe Acrobat, tesseract-ocr)."
        )

    if len(combined) > MAX_CHARS:
        print(
            f"  WARNING: Extracted text exceeds {MAX_CHARS:,} characters. "
            "Truncating to fit within the AI context window."
        )
        combined = combined[:MAX_CHARS]

    return combined
