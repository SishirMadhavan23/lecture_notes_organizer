# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for custom exceptions."""

import pytest

from src.utils.exceptions import (
    AIError,
    ConfigurationError,
    ExtractionError,
    IngestionError,
    LectureNotesError,
    ModelNotFoundError,
    ModelTimeoutError,
    OCRError,
    PreprocessingError,
    StorageError,
    UnsupportedFormatError,
)


class TestExceptions:
    """Test custom exception hierarchy."""

    def test_all_exceptions_inherit_from_base(self):
        """Test that all exceptions inherit from LectureNotesError."""
        exceptions = [
            IngestionError(),
            UnsupportedFormatError(),
            ExtractionError(),
            OCRError(),
            PreprocessingError(),
            AIError(),
            ModelNotFoundError(),
            ModelTimeoutError(),
            StorageError(),
            ConfigurationError(),
        ]
        for exc in exceptions:
            assert isinstance(exc, LectureNotesError)
            assert isinstance(exc, Exception)

    def test_exception_message(self):
        """Test that exceptions carry messages."""
        msg = "Test error message"
        exc = IngestionError(msg)
        assert str(exc) == msg

    def test_exception_hierarchy(self):
        """Test specific exception hierarchy."""
        assert issubclass(UnsupportedFormatError, IngestionError)
        assert issubclass(ExtractionError, IngestionError)
        assert issubclass(OCRError, IngestionError)
        assert issubclass(ModelNotFoundError, AIError)
        assert issubclass(ModelTimeoutError, AIError)
