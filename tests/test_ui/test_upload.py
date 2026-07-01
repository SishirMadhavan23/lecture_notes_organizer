"""Tests for the upload page and processing flow."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from src.ui.pages import upload
from src.utils.exceptions import IngestionError


def test_upload_helpers_validate_extensions_and_sizes(
    mock_streamlit: Any,
    mock_uploaded_file: Any,
) -> None:
    """Upload helpers should validate file type, file size, and timestamps."""
    uploaded = mock_uploaded_file("notes.pdf", b"x" * 16)
    assert upload._get_supported_extensions() == [
        ".pdf",
        ".docx",
        ".txt",
        ".pptx",
        ".ppt",
    ]
    assert upload._validate_uploaded_file(None, 5) is None
    assert upload._validate_uploaded_file(mock_uploaded_file("notes.exe", b"x"), 5)
    assert upload._validate_uploaded_file(mock_uploaded_file("notes.pdf", b"x" * 10), 0)

    timestamp = upload._get_upload_timestamp(uploaded)
    assert isinstance(timestamp, str)
    assert mock_streamlit.session_state["upload_signature"] == "notes.pdf:16"
    assert upload._get_upload_timestamp(uploaded) == timestamp


def test_render_upload_dropzone_and_preview(
    mock_streamlit: Any, mock_uploaded_file: Any
) -> None:
    """The upload page should render informative HTML for the dropzone and preview."""
    upload._render_upload_dropzone()
    upload._render_upload_preview(
        mock_uploaded_file("deck.pptx", b"abc"), "2026-07-01 12:00:00"
    )

    assert mock_streamlit.markdown.call_count == 2
    html = mock_streamlit.markdown.call_args_list[1].args[0]
    assert "deck.pptx" in html
    assert "Ready for processing" in html


def test_render_upload_page_empty_state(
    mock_streamlit: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When no file is selected, the page should stay in instructional mode."""
    header_calls: list[tuple[str, str, str]] = []
    monkeypatch.setattr(
        upload, "render_page_header", lambda *args: header_calls.append(args)
    )
    monkeypatch.setattr(
        upload, "render_processing_stepper", lambda *args, **kwargs: None
    )

    upload.render_upload_page({"max_file_size_mb": 5})

    assert header_calls
    mock_streamlit.info.assert_called_with(
        "Drag your lecture notes here or click to browse for a file."
    )


def test_render_upload_page_validation_error_blocks_processing(
    mock_streamlit: Any,
    mock_uploaded_file: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Validation errors should surface and disable processing."""
    monkeypatch.setattr(upload, "render_page_header", lambda *args: None)
    monkeypatch.setattr(
        upload, "render_processing_stepper", lambda *args, **kwargs: None
    )
    mock_streamlit.file_uploader.return_value = mock_uploaded_file(
        "notes.pdf", b"x" * 20
    )
    mock_streamlit.button.return_value = False
    monkeypatch.setattr(upload, "_validate_uploaded_file", lambda *args: "bad file")

    upload.render_upload_page({"max_file_size_mb": 5})

    mock_streamlit.error.assert_called_with("bad file")
    assert mock_streamlit.button.call_args.kwargs["disabled"] is True


def test_render_upload_page_processes_valid_file(
    mock_streamlit: Any,
    mock_uploaded_file: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A valid upload should show a preview and invoke processing when requested."""
    processed: list[tuple[str, dict[str, Any]]] = []
    monkeypatch.setattr(upload, "render_page_header", lambda *args: None)
    monkeypatch.setattr(
        upload, "render_processing_stepper", lambda *args, **kwargs: None
    )
    mock_streamlit.file_uploader.return_value = mock_uploaded_file(
        "notes.pdf", b"x" * 20
    )
    mock_streamlit.button.return_value = True
    monkeypatch.setattr(upload, "_validate_uploaded_file", lambda *args: None)
    monkeypatch.setattr(
        upload,
        "_render_upload_preview",
        lambda *args: processed.append(("preview", {})),
    )
    monkeypatch.setattr(
        upload,
        "process_uploaded_file",
        lambda file, config, placeholder: processed.append((file.name, config)),
    )

    upload.render_upload_page({"max_file_size_mb": 5, "tesseract_enabled": False})

    assert ("preview", {}) in processed
    assert (
        "notes.pdf",
        {"max_file_size_mb": 5, "tesseract_enabled": False},
    ) in processed


def test_estimate_page_count_handles_ppt_pdf_and_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Page estimation should cover PPT metadata, PDFs, and exceptions."""
    monkeypatch.setattr(
        upload,
        "extract_presentation_metadata",
        lambda path, ext: {"slide_count": 7},
    )
    assert upload._estimate_page_count("deck.pptx", ".pptx") == 7

    monkeypatch.setattr(
        upload,
        "extract_presentation_metadata",
        lambda path, ext: (_ for _ in ()).throw(IngestionError("boom")),
    )
    assert upload._estimate_page_count("deck.pptx", ".pptx") == 1

    class DummyPDF:
        def __len__(self) -> int:
            return 4

        def __enter__(self) -> DummyPDF:
            return self

        def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
            return False

    monkeypatch.setattr("fitz.open", lambda path: DummyPDF())
    assert upload._estimate_page_count("notes.pdf", ".pdf") == 4
    monkeypatch.setattr(
        "fitz.open", lambda path: (_ for _ in ()).throw(RuntimeError("bad"))
    )
    assert upload._estimate_page_count("notes.pdf", ".pdf") == 1
    assert upload._estimate_page_count("notes.txt", ".txt") == 1


def test_show_stepper_uses_placeholder_container(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Stepper rendering should happen inside the placeholder container."""
    calls: list[tuple[int, bool]] = []
    monkeypatch.setattr(
        upload,
        "render_processing_stepper",
        lambda step=0, failed=False: calls.append((step, failed)),
    )

    placeholder = type(
        "Placeholder", (), {"container": lambda self: upload.st.container()}
    )()
    upload._show_stepper(placeholder, 3, failed=True)

    assert calls == [(3, True)]


def test_process_uploaded_file_success_updates_session(
    mock_streamlit: Any,
    mock_uploaded_file: Any,
    monkeypatch: pytest.MonkeyPatch,
    temp_dir: Path,
) -> None:
    """Successful processing should update progress, stats, and success state."""
    uploaded = mock_uploaded_file("notes.pdf", b"example content")
    stepper = mock_streamlit.empty()
    step_calls: list[tuple[int, bool]] = []
    monkeypatch.setattr(upload, "_estimate_page_count", lambda *args: 3)
    monkeypatch.setattr(
        upload,
        "_show_stepper",
        lambda placeholder, step, failed=False: step_calls.append((step, failed)),
    )
    monkeypatch.setattr(
        upload, "extract_text", lambda *args: "Extracted text long enough"
    )
    monkeypatch.setattr(upload, "clean_text", lambda text: "Clean text")
    monkeypatch.setattr(
        upload, "generate_structured_notes", lambda text, config: {"title": "T"}
    )
    monkeypatch.setattr(upload, "save_document", lambda *args: 42)
    monkeypatch.setattr(
        upload.time, "perf_counter", lambda: 10.0 if not step_calls else 12.5
    )

    upload.process_uploaded_file(uploaded, {"tesseract_enabled": False}, stepper)

    assert step_calls == [(1, False), (2, False), (3, False), (4, False), (5, False)]
    assert mock_streamlit.session_state["pages_processed"] == 3
    assert mock_streamlit.session_state["processing_durations"] == [2.5]
    mock_streamlit.success.assert_called_with("Processed successfully in 2.5s (ID: 42)")


def test_process_uploaded_file_handles_ingestion_and_generic_errors(
    mock_streamlit: Any,
    mock_uploaded_file: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Failures should surface the correct error messages and clear progress."""
    uploaded = mock_uploaded_file("notes.pdf", b"example content")
    stepper = mock_streamlit.empty()
    step_calls: list[tuple[int, bool]] = []
    monkeypatch.setattr(upload, "_estimate_page_count", lambda *args: 1)
    monkeypatch.setattr(
        upload,
        "_show_stepper",
        lambda placeholder, step, failed=False: step_calls.append((step, failed)),
    )
    monkeypatch.setattr(
        upload,
        "extract_text",
        lambda *args: (_ for _ in ()).throw(IngestionError("ocr failed")),
    )

    upload.process_uploaded_file(uploaded, {}, stepper)
    mock_streamlit.error.assert_called_with("Ingestion error: ocr failed")
    assert step_calls[-1] == (1, True)

    mock_streamlit.error.reset_mock()
    step_calls.clear()
    monkeypatch.setattr(upload, "extract_text", lambda *args: "long enough text")
    monkeypatch.setattr(upload, "clean_text", lambda text: "clean")
    monkeypatch.setattr(
        upload,
        "generate_structured_notes",
        lambda *args: (_ for _ in ()).throw(RuntimeError("ai failed")),
    )

    upload.process_uploaded_file(uploaded, {}, stepper)
    mock_streamlit.error.assert_called_with("Error: ai failed")
    assert step_calls[-1] == (3, True)


def test_process_uploaded_file_warns_for_short_text(
    mock_streamlit: Any,
    mock_uploaded_file: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Short extracted text should warn before continuing."""
    uploaded = mock_uploaded_file("notes.pdf", b"example content")
    stepper = mock_streamlit.empty()
    monkeypatch.setattr(upload, "_estimate_page_count", lambda *args: 1)
    monkeypatch.setattr(upload, "_show_stepper", lambda *args, **kwargs: None)
    monkeypatch.setattr(upload, "extract_text", lambda *args: "short")
    monkeypatch.setattr(upload, "clean_text", lambda text: "clean")
    monkeypatch.setattr(
        upload, "generate_structured_notes", lambda *args: {"title": "T"}
    )
    monkeypatch.setattr(upload, "save_document", lambda *args: 1)
    monkeypatch.setattr(
        upload.time,
        "perf_counter",
        lambda: (
            1.0 if "processing_durations" not in mock_streamlit.session_state else 2.0
        ),
    )

    upload.process_uploaded_file(uploaded, {}, stepper)

    mock_streamlit.warning.assert_called_with(
        "Very little text extracted. File may be scanned."
    )


def test_extract_text_routes_to_supported_extractors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Extraction should route by extension, including OCR fallbacks."""
    monkeypatch.setattr(upload, "extract_text_from_pdf", lambda path: "pdf text")
    assert upload.extract_text("note.pdf", ".pdf", {}) == "pdf text"

    monkeypatch.setattr(
        upload,
        "extract_text_from_pdf",
        lambda path: (_ for _ in ()).throw(RuntimeError("pdf bad")),
    )
    monkeypatch.setattr(upload, "is_tesseract_available", lambda path: True)
    monkeypatch.setattr(upload, "ocr_pdf", lambda *args, **kwargs: "ocr text")
    assert (
        upload.extract_text("note.pdf", ".pdf", {"tesseract_enabled": True})
        == "ocr text"
    )

    monkeypatch.setattr(upload, "extract_text_from_docx", lambda path: "docx")
    monkeypatch.setattr(upload, "extract_text_from_txt", lambda path: "txt")
    monkeypatch.setattr(upload, "extract_text_from_pptx", lambda path: "pptx")
    assert upload.extract_text("note.docx", ".docx", {}) == "docx"
    assert upload.extract_text("note.txt", ".txt", {}) == "txt"
    assert upload.extract_text("deck.pptx", ".pptx", {}) == "pptx"

    ocr_calls: list[tuple[str, str, str | None]] = []

    def fake_ocr_image(path: str, lang: str, tesseract_path: str | None) -> str:
        ocr_calls.append((path, lang, tesseract_path))
        return "image text"

    monkeypatch.setattr("src.ingestion.ocr_processor.ocr_image", fake_ocr_image)
    assert (
        upload.extract_text(
            "scan.png",
            ".png",
            {
                "tesseract_enabled": True,
                "tesseract_lang": "eng",
                "tesseract_path": "/bin/tesseract",
            },
        )
        == "image text"
    )
    assert ocr_calls == [("scan.png", "eng", "/bin/tesseract")]

    with pytest.raises(IngestionError, match="Image files require OCR"):
        upload.extract_text("scan.png", ".png", {"tesseract_enabled": False})

    with pytest.raises(IngestionError, match="Unsupported format"):
        upload.extract_text("archive.zip", ".zip", {})
