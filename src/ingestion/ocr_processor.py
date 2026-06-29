# SPDX-License-Identifier: GPL-3.0-or-later
"""OCR processing for scanned documents."""

import shutil
from typing import Optional

from src.utils.exceptions import OCRError


def is_tesseract_available() -> bool:
    """Check if Tesseract OCR is installed."""
    return shutil.which("tesseract") is not None


def ocr_image(image_path: str, lang: str = "eng") -> str:
    """Perform OCR on an image file.

    Raises:
        OCRError: If pytesseract is missing or OCR fails
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        raise OCRError(
            "pytesseract/Pillow not installed. "
            "Install: pip install pytesseract Pillow"
        )
    if not is_tesseract_available():
        raise OCRError("Tesseract OCR engine not found on system.")
    try:
        image = Image.open(image_path)
        return pytesseract.image_to_string(image, lang=lang).strip()
    except Exception as exc:
        raise OCRError(f"OCR processing failed: {exc}") from exc


def ocr_pdf(pdf_path: str, lang: str = "eng", dpi: int = 300) -> str:
    """Perform OCR on a scanned PDF.

    Raises:
        OCRError: If dependencies are missing or OCR fails
    """
    try:
        import pytesseract
        from pdf2image import convert_from_path
    except ImportError:
        raise OCRError(
            "pytesseract/pdf2image not installed. "
            "Install: pip install pytesseract pdf2image Pillow"
        )
    if not is_tesseract_available():
        raise OCRError("Tesseract OCR engine not found on system.")
    try:
        images = convert_from_path(pdf_path, dpi=dpi)
        texts = [pytesseract.image_to_string(img, lang=lang).strip()
                 for img in images]
        return "\n\n".join(texts)
    except Exception as exc:
        raise OCRError(f"PDF OCR failed: {exc}") from exc
