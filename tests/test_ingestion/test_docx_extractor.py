"""Tests for DOCX text extraction."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.ingestion.docx_extractor import extract_text_from_docx
from src.utils.exceptions import ExtractionError


class TestDocxExtractor:
    """Tests for extract_text_from_docx function."""

    def test_extract_from_docx_file(self, temp_docx_file: Path) -> None:
        """Test extracting text from a valid DOCX file."""
        text = extract_text_from_docx(str(temp_docx_file))
        assert "Test Document Content" in text
        assert "Second paragraph" in text

    def test_extract_from_nonexistent_file(self) -> None:
        """Test raises ExtractionError for missing file."""
        with pytest.raises(ExtractionError):
            extract_text_from_docx("/nonexistent/file.docx")

    def test_extract_from_invalid_file(self, temp_dir: Path) -> None:
        """Test raises ExtractionError for invalid file."""
        invalid_file = temp_dir / "invalid.docx"
        invalid_file.write_bytes(b"not a valid docx file")
        with pytest.raises(ExtractionError):
            extract_text_from_docx(str(invalid_file))

    def test_empty_document(self, temp_dir: Path) -> None:
        """Test returns empty string from document with no paragraphs."""
        import zipfile

        docx_path = temp_dir / "empty.docx"
        doc_content = (
             '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<w:document xmlns:w="http://schemas.openxmlformats.org/'
             'wordprocessingml/2006/main">'
             "<w:body></w:body></w:document>"
        )
        content_types = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/'
            'package/2006/content-types">'
            '<Default Extension="rels" '
            'ContentType="application/vnd.openxmlformats-package.'
            'relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'wordprocessingml.document.main+xml"/>'
            "</Types>"
        )

        rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/'
            'package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument'
            '/2006/relationships/officeDocument" '
            'Target="word/document.xml"/>'
            "</Relationships>"
        )
        with zipfile.ZipFile(str(docx_path), "w") as zf:
            zf.writestr("[Content_Types].xml", content_types)
            zf.writestr("_rels/.rels", rels)
            zf.writestr("word/document.xml", doc_content)

        text = extract_text_from_docx(str(docx_path))
        assert text == ""
