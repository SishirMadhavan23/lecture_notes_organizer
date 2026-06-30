# SPDX-License-Identifier: GPL-3.0-or-later
"""TXT file reader with encoding detection."""

from src.utils.exceptions import ExtractionError


def extract_text_from_txt(file_path: str, encoding: str | None = None) -> str:
    """Read text from a plain text file.

    Tries multiple encodings if not specified.

    Args:
        file_path: Path to the TXT file
        encoding: Text encoding (auto-detected if None)

    Returns:
        File contents

    Raises:
        ExtractionError: If reading fails
    """
    encodings = [encoding] if encoding else ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
    for enc in encodings:
        try:
            with open(file_path, encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception as exc:
            raise ExtractionError(f"Failed to read TXT file: {exc}") from exc

    raise ExtractionError(f"Could not decode {file_path} with any known encoding")
