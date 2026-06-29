# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for validators module."""

import tempfile
from pathlib import Path

import pytest

from src.utils.exceptions import UnsupportedFormatError
from src.utils.validators import (
    SUPPORTED_EXTENSIONS,
    get_supported_extensions,
    validate_file_path,
    validate_file_size,
)


class TestValidators:
    """Test file validation utilities."""

    def test_validate_file_path_valid_txt(self):
        """Test validation of a valid .txt file."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test content")
            path = f.name

        try:
            result = validate_file_path(path)
            assert isinstance(result, Path)
            assert result.exists()
        finally:
            Path(path).unlink()

    def test_validate_file_path_valid_pdf(self):
        """Test validation of a valid .pdf file."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4 test")
            path = f.name

        try:
            result = validate_file_path(path)
            assert result.suffix == ".pdf"
        finally:
            Path(path).unlink()

    def test_validate_file_path_unsupported_format(self):
        """Test that unsupported formats raise UnsupportedFormatError."""
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            f.write(b"test")
            path = f.name

        try:
            with pytest.raises(UnsupportedFormatError):
                validate_file_path(path)
        finally:
            Path(path).unlink()

    def test_validate_file_path_not_found(self):
        """Test that missing files raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            validate_file_path("/nonexistent/file.txt")

    def test_validate_file_size_under_limit(self):
        """Test that small files pass validation."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"small file")
            path = Path(f.name)

        try:
            validate_file_size(path)  # Should not raise
        finally:
            path.unlink()

    def test_get_supported_extensions(self):
        """Test that supported extensions are returned."""
        extensions = get_supported_extensions()
        assert ".pdf" in extensions
        assert ".docx" in extensions
        assert ".txt" in extensions
        assert len(extensions) == len(SUPPORTED_EXTENSIONS)
