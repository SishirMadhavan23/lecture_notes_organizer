# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for TXT extractor."""

import os
import tempfile

import pytest

from src.ingestion.txt_extractor import extract_text_from_txt
from src.utils.exceptions import ExtractionError


class TestTxtExtractor:
    """Test TXT file extraction."""

    def test_extract_utf8_text(self):
        """Test extraction of UTF-8 encoded text file."""
        content = "Hello, World!\nThis is a test file."
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w",
                                          encoding="utf-8", delete=False) as f:
            f.write(content)
            path = f.name

        try:
            result = extract_text_from_txt(path)
            assert result == content
        finally:
            os.unlink(path)

    def test_extract_with_encoding(self):
        """Test extraction with explicit encoding."""
        content = "Café résumé naïve"
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w",
                                          encoding="latin-1", delete=False) as f:
            f.write(content)
            path = f.name

        try:
            result = extract_text_from_txt(path, encoding="latin-1")
            assert "Café" in result
        finally:
            os.unlink(path)

    def test_extract_file_not_found(self):
        """Test that missing file raises ExtractionError."""
        with pytest.raises(ExtractionError):
            extract_text_from_txt("/nonexistent/file.txt")
