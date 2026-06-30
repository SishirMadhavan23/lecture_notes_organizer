# SPDX-License-Identifier: GPL-3.0-or-later
"""DOCX text extraction using python-docx."""

from src.utils.exceptions import ExtractionError


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file.

    Args:
        file_path: Path to the DOCX file

    Returns:
        Extracted text

    Raises:
        ExtractionError: If extraction fails
    """
    try:
        from docx import Document
    except ImportError:
        raise ExtractionError(
            "python-docx is not installed. Install it with: pip install python-docx"
        )
    try:
        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)
    except Exception as exc:
        raise ExtractionError(f"Failed to extract text from DOCX: {exc}") from exc
