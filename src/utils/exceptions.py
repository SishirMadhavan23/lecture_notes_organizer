# SPDX-License-Identifier: GPL-3.0-or-later
"""Custom exceptions for the application."""


class LectureNotesError(Exception):
    """Base exception for all application errors."""


class IngestionError(LectureNotesError):
    """Raised when document ingestion fails."""


class UnsupportedFormatError(IngestionError):
    """Raised when file format is not supported."""


class ExtractionError(IngestionError):
    """Raised when text extraction fails."""


class OCRError(IngestionError):
    """Raised when OCR processing fails."""


class PreprocessingError(LectureNotesError):
    """Raised when text preprocessing fails."""


class AIError(LectureNotesError):
    """Raised when AI model operations fail."""


class ModelNotFoundError(AIError):
    """Raised when model is not available."""


class ModelTimeoutError(AIError):
    """Raised when model inference times out."""


class StorageError(LectureNotesError):
    """Raised when database operations fail."""


class ConfigurationError(LectureNotesError):
    """Raised when configuration is invalid."""
