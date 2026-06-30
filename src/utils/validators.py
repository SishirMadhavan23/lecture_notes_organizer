# SPDX-License-Identifier: GPL-3.0-or-later
"""Input validation utilities."""

from pathlib import Path

from src.utils.exceptions import UnsupportedFormatError

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".pptx", ".ppt"}
SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024


def validate_file_path(file_path: str) -> Path:
    """Validate file path exists and is supported format."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")
    if path.suffix.lower() not in (SUPPORTED_EXTENSIONS | SUPPORTED_IMAGE_EXTENSIONS):
        raise UnsupportedFormatError(f"Unsupported format: {path.suffix}")
    return path


def validate_file_size(file_path: Path) -> None:
    """Validate file size is within limits."""
    size = file_path.stat().st_size
    if size > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"File too large: {size / 1024 / 1024:.1f} MB "
            f"(max {MAX_FILE_SIZE_BYTES / 1024 / 1024:.0f} MB)"
        )


def get_supported_extensions() -> list[str]:
    """Return list of supported file extensions."""
    return list(SUPPORTED_EXTENSIONS)
