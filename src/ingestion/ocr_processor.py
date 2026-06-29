# SPDX-License-Identifier: GPL-3.0-or-later
"""OCR processing for scanned documents."""

import shutil
from typing import Optional

from src.utils.exceptions import OCRError
from src.utils.config import load_config


def _resolve_tesseract_path(tesseract_path: Optional[str] = None) -> Optional[str]:
    """Resolve the configured Tesseract executable path."""
    if tesseract_path:
        return tesseract_path
    config = load_config()
    if config.tesseract_path:
        return config.tesseract_path
    return shutil.which("tesseract")


def is_tesseract_available(tesseract_path: Optional[str] = None) -> bool:
    """Check if Tesseract OCR is installed."""
    resolved_path = _resolve_tesseract_path(tesseract_path)
    if tesseract_path:
        return bool(resolved_path and shutil.which(resolved_path))
    if resolved_path and shutil.which(resolved_path):
        return True
    return bool(resolved_path and shutil.which("tesseract"))


def ocr_image(
    image_path: str,
    lang: str = "eng",
    tesseract_path: Optional[str] = None,
) -> str:
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
    resolved_path = _resolve_tesseract_path(tesseract_path)
    if resolved_path:
        pytesseract.pytesseract.tesseract_cmd = resolved_path
    if not is_tesseract_available(resolved_path):
        raise OCRError("Tesseract OCR engine not found on system.")
    try:
        image = Image.open(image_path)
        return pytesseract.image_to_string(image, lang=lang).strip()
    except Exception as exc:
        raise OCRError(f"OCR processing failed: {exc}") from exc


def ocr_pdf(
    pdf_path: str,
    lang: str = "eng",
    dpi: int = 300,
    tesseract_path: Optional[str] = None,
) -> str:
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
    resolved_path = _resolve_tesseract_path(tesseract_path)
    if resolved_path:
        pytesseract.pytesseract.tesseract_cmd = resolved_path
    if not is_tesseract_available(resolved_path):
        raise OCRError("Tesseract OCR engine not found on system.")
    try:
        images = convert_from_path(pdf_path, dpi=dpi)
        texts = [pytesseract.image_to_string(img, lang=lang).strip()
                 for img in images]
        return "\n\n".join(texts)
    except Exception as exc:
        raise OCRError(f"PDF OCR failed: {exc}") from exc
