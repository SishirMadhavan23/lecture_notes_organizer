# SPDX-License-Identifier: GPL-3.0-or-later
"""PDF text extraction using PyMuPDF."""

from typing import Any

from src.utils.exceptions import ExtractionError


def extract_text_from_pdf(file_path: str, page_limit: int | None = None) -> str:
    """Extract text from a PDF file using PyMuPDF.

    Args:
        file_path: Path to the PDF file
        page_limit: Max pages to process (None = all)

    Returns:
        Extracted text content

    Raises:
        ExtractionError: If extraction fails
    """
    try:
        import fitz
    except ImportError as exc:
        raise ExtractionError(
            "PyMuPDF (fitz) is not installed. Install it with: pip install PyMuPDF"
        ) from exc

    try:
        doc = fitz.open(file_path)
        pages = range(min(page_limit, len(doc))) if page_limit else range(len(doc))
        text_parts = []
        for page_num in pages:
            page = doc.load_page(page_num)
            text_parts.append(page.get_text())
        doc.close()
        return "\n\n".join(text_parts)
    except Exception as exc:
        raise ExtractionError(f"Failed to extract text from PDF: {exc}") from exc


def extract_metadata(file_path: str) -> dict[str, Any]:
    """Extract PDF metadata (title, author, etc.)."""
    try:
        import fitz
    except ImportError:
        return {}
    try:
        doc = fitz.open(file_path)
        meta = doc.metadata or {}
        doc.close()
        return {
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
            "subject": meta.get("subject", ""),
            "keywords": meta.get("keywords", ""),
        }
    except Exception:
        return {}
