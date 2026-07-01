"""Tests for OCR processing."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.ingestion.ocr_processor import (
    _resolve_tesseract_path,
    is_tesseract_available,
    ocr_image,
    ocr_pdf,
)
from src.utils.exceptions import OCRError


class TestResolveTesseractPath:
    """Tests for _resolve_tesseract_path function."""

    def test_returns_provided_path(self) -> None:
        """Test returns the path when explicitly provided."""
        result = _resolve_tesseract_path("/custom/tesseract")
        assert result == "/custom/tesseract"

    def test_returns_config_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns path from config when not provided."""
        from src.utils.config import AppConfig

        config = AppConfig()
        config.tesseract_path = "/config/tesseract"

        def mock_load_config() -> AppConfig:
            return config

        monkeypatch.setattr("src.ingestion.ocr_processor.load_config", mock_load_config)
        result = _resolve_tesseract_path()
        assert result == "/config/tesseract"

    def test_falls_back_to_which(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test falls back to shutil.which when no path configured."""
        from src.utils.config import AppConfig

        config = AppConfig()
        config.tesseract_path = ""

        def mock_load_config() -> AppConfig:
            return config

        monkeypatch.setattr("src.ingestion.ocr_processor.load_config", mock_load_config)
        monkeypatch.setattr(
            "src.ingestion.ocr_processor.shutil.which", lambda x: "/usr/bin/tesseract"
        )
        result = _resolve_tesseract_path()
        assert result == "/usr/bin/tesseract"


class TestIsTesseractAvailable:
    """Tests for is_tesseract_available function."""

    def test_available_with_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns True when tesseract is found at given path."""
        monkeypatch.setattr("src.ingestion.ocr_processor.shutil.which", lambda x: x)
        assert is_tesseract_available("/usr/bin/tesseract") is True

    def test_not_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns False when tesseract is not found."""
        monkeypatch.setattr("src.ingestion.ocr_processor.shutil.which", lambda x: None)
        assert is_tesseract_available("/nonexistent/tesseract") is False

    def test_available_without_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test checks config and which when no path provided."""
        from src.utils.config import AppConfig

        config = AppConfig()
        config.tesseract_path = ""

        def mock_load_config() -> AppConfig:
            return config

        monkeypatch.setattr("src.ingestion.ocr_processor.load_config", mock_load_config)
        monkeypatch.setattr(
            "src.ingestion.ocr_processor.shutil.which",
            lambda x: x if x == "tesseract" else None,
        )
        assert is_tesseract_available() is True


class TestOcrImage:
    """Tests for ocr_image function."""

    def test_tesseract_not_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test raises OCRError when tesseract not installed."""
        monkeypatch.setattr("src.ingestion.ocr_processor.shutil.which", lambda x: None)

        # Mock pytesseract and PIL imports to succeed
        mock_pytesseract = MagicMock()
        mock_pil = MagicMock()

        with patch.dict(
            "sys.modules", {"pytesseract": mock_pytesseract, "PIL": mock_pil}
        ):
            with pytest.raises(OCRError) as exc:
                ocr_image("test.png")
        assert "Tesseract OCR engine" in str(exc.value)

    def test_ocr_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test successful OCR processing."""
        monkeypatch.setattr("src.ingestion.ocr_processor.shutil.which", lambda x: x)

        mock_pytesseract = MagicMock()
        mock_pytesseract.image_to_string.return_value = "Extracted text"
        mock_pytesseract.pytesseract.tesseract_cmd = ""

        mock_pil = MagicMock()
        mock_pil.Image = MagicMock()
        mock_pil.Image.open.return_value = MagicMock()

        with patch.dict(
            "sys.modules", {"pytesseract": mock_pytesseract, "PIL": mock_pil}
        ):
            result = ocr_image(
                "test.png", lang="eng", tesseract_path="/usr/bin/tesseract"
            )
        assert result == "Extracted text"

    def test_ocr_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test raises OCRError when OCR processing fails."""
        monkeypatch.setattr("src.ingestion.ocr_processor.shutil.which", lambda x: x)

        mock_pytesseract = MagicMock()
        mock_pytesseract.image_to_string.side_effect = Exception("OCR failed")
        mock_pytesseract.pytesseract.tesseract_cmd = ""

        mock_pil = MagicMock()
        mock_pil.Image = MagicMock()
        mock_pil.Image.open.return_value = MagicMock()

        with patch.dict(
            "sys.modules", {"pytesseract": mock_pytesseract, "PIL": mock_pil}
        ):
            with pytest.raises(OCRError) as exc:
                ocr_image("test.png")
        assert "OCR processing failed" in str(exc.value)


class TestOcrPdf:
    """Tests for ocr_pdf function."""

    def test_tesseract_not_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test raises OCRError when tesseract not installed."""
        monkeypatch.setattr("src.ingestion.ocr_processor.shutil.which", lambda x: None)

        mock_pytesseract = MagicMock()
        mock_pdf2image = MagicMock()

        with patch.dict(
            "sys.modules",
            {"pytesseract": mock_pytesseract, "pdf2image": mock_pdf2image},
        ):
            with pytest.raises(OCRError) as exc:
                ocr_pdf("test.pdf")
        assert "Tesseract OCR engine" in str(exc.value)

    def test_ocr_pdf_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test successful PDF OCR processing."""
        monkeypatch.setattr("src.ingestion.ocr_processor.shutil.which", lambda x: x)

        mock_pytesseract = MagicMock()
        mock_pytesseract.image_to_string.return_value = "Page text"
        mock_pytesseract.pytesseract.tesseract_cmd = ""

        mock_pdf2image = MagicMock()
        mock_pdf2image.convert_from_path.return_value = [MagicMock(), MagicMock()]

        with patch.dict(
            "sys.modules",
            {"pytesseract": mock_pytesseract, "pdf2image": mock_pdf2image},
        ):
            result = ocr_pdf(
                "test.pdf", lang="eng", dpi=300, tesseract_path="/usr/bin/tesseract"
            )
        assert "Page text" in result

    def test_ocr_pdf_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test raises OCRError when PDF OCR fails."""
        monkeypatch.setattr("src.ingestion.ocr_processor.shutil.which", lambda x: x)

        mock_pytesseract = MagicMock()
        mock_pytesseract.pytesseract.tesseract_cmd = ""

        mock_pdf2image = MagicMock()
        mock_pdf2image.convert_from_path.side_effect = Exception(
            "PDF conversion failed"
        )

        with patch.dict(
            "sys.modules",
            {"pytesseract": mock_pytesseract, "pdf2image": mock_pdf2image},
        ):
            with pytest.raises(OCRError) as exc:
                ocr_pdf("test.pdf")
        assert "PDF OCR failed" in str(exc.value)
