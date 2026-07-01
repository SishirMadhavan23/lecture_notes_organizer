"""Tests for PDF text extraction."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.ingestion.pdf_extractor import extract_metadata, extract_text_from_pdf
from src.utils.exceptions import ExtractionError


class TestPdfExtractor:
    """Tests for extract_text_from_pdf function."""

    def test_extract_text_from_pdf(self, temp_pdf_file: Path) -> None:
        """Test extracting text from a valid PDF file."""
        text = extract_text_from_pdf(str(temp_pdf_file))
        assert isinstance(text, str)

    def test_extract_text_with_page_limit(self, temp_pdf_file: Path) -> None:
        """Test extracting text with page limit."""
        text = extract_text_from_pdf(str(temp_pdf_file), page_limit=1)
        assert isinstance(text, str)

    def test_extract_text_from_nonexistent_file(self) -> None:
        """Test raises ExtractionError for missing file."""
        with pytest.raises(ExtractionError):
            extract_text_from_pdf("/nonexistent/file.pdf")

    def test_extract_text_from_invalid_file(self, temp_dir: Path) -> None:
        """Test raises ExtractionError for invalid PDF content."""
        invalid_file = temp_dir / "invalid.pdf"
        invalid_file.write_bytes(b"not a valid pdf")
        with pytest.raises(ExtractionError):
            extract_text_from_pdf(str(invalid_file))

    def test_empty_pdf(self, temp_dir: Path) -> None:
        """Test extracting from a PDF with no pages."""
        pdf_path = temp_dir / "empty.pdf"
        # Minimal PDF with no pages
        pdf_content = (
            b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
            b"2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\n"
            b"xref\n0 3\n0000000000 65535 f \n0000000009 00000 n \n"
            b"0000000058 00000 n \ntrailer\n<< /Size 3 /Root 1 0 R >>\n"
            b"startxref\n107\n%%EOF"
        )
        pdf_path.write_bytes(pdf_content)
        text = extract_text_from_pdf(str(pdf_path))
        assert text == ""


class TestPdfMetadata:
    """Tests for extract_metadata function."""

    def test_metadata_extraction(self, temp_pdf_file: Path) -> None:
        """Test extracting metadata from PDF."""
        metadata = extract_metadata(str(temp_pdf_file))
        assert isinstance(metadata, dict)
        assert "title" in metadata
        assert "author" in metadata

    def test_metadata_invalid_file(self, temp_dir: Path) -> None:
        """Test returns empty dict for invalid file."""
        invalid_file = temp_dir / "invalid.pdf"
        invalid_file.write_bytes(b"garbage")
        result = extract_metadata(str(invalid_file))
        assert result == {}
