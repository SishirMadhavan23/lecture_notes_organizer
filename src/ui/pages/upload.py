# SPDX-License-Identifier: GPL-3.0-or-later
"""Upload page for Streamlit UI - handles file upload and processing."""

import os
import tempfile
import time
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st

from src.ai.model_manager import generate_structured_notes
from src.ingestion.docx_extractor import extract_text_from_docx
from src.ingestion.ocr_processor import is_tesseract_available, ocr_pdf
from src.ingestion.pdf_extractor import extract_text_from_pdf
from src.ingestion.pptx_extractor import (
    extract_presentation_metadata,
    extract_text_from_pptx,
)
from src.ingestion.txt_extractor import extract_text_from_txt
from src.preprocessing.text_cleaner import clean_text
from src.storage.database import save_document
from src.ui.components.dashboard import render_processing_stepper
from src.ui.components.page_header import render_page_header
from src.utils.exceptions import IngestionError
from src.utils.validators import MAX_FILE_SIZE_BYTES, get_supported_extensions

UPLOAD_KEY = "lecture_notes_upload"
UPLOAD_TIMESTAMP_KEY = "upload_timestamp"


def _format_file_size(size_bytes: int) -> str:
    """Format file size for UI display."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / 1024 / 1024:.2f} MB"


def _get_supported_extensions() -> list[str]:
    """Return supported extensions in a stable order."""
    ordered = [".pdf", ".docx", ".txt", ".pptx", ".ppt"]
    known = set(get_supported_extensions())
    return [ext for ext in ordered if ext in known]


def _validate_uploaded_file(uploaded_file, max_file_size_mb: int) -> Optional[str]:
    """Validate a Streamlit uploaded file before processing."""
    if uploaded_file is None:
        return None

    extension = Path(uploaded_file.name).suffix.lower()
    supported_extensions = set(_get_supported_extensions())
    if extension not in supported_extensions:
        return (
            "Unsupported file type. Please upload a PDF, DOCX, TXT, PPTX, "
            "or PPT file."
        )

    file_size_bytes = len(uploaded_file.getvalue())
    max_size_bytes = min(max_file_size_mb * 1024 * 1024, MAX_FILE_SIZE_BYTES)
    if file_size_bytes > max_size_bytes:
        return (
            f"File is too large. Please upload a file under {max_file_size_mb} MB."
        )

    return None


@st.cache_data(show_spinner=False)
def _inspect_presentation(file_bytes: bytes, extension: str) -> Dict[str, Any]:
    """Validate and inspect a PowerPoint file for upload preview metadata."""
    return extract_presentation_metadata(file_bytes, extension)


def _get_upload_timestamp(uploaded_file) -> str:
    """Track the timestamp for the currently selected upload."""
    signature = f"{uploaded_file.name}:{uploaded_file.size}"
    current_signature = st.session_state.get("upload_signature")
    if current_signature != signature:
        st.session_state["upload_signature"] = signature
        st.session_state[UPLOAD_TIMESTAMP_KEY] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    return st.session_state.get(UPLOAD_TIMESTAMP_KEY, "")


def _render_upload_dropzone() -> None:
    """Render instructional content above the native uploader."""
    st.markdown(
        """
        <section class="upload-panel">
            <div class="upload-intro">
                <div class="upload-icon" aria-hidden="true">↑</div>
                <p class="upload-title">Drag your lecture notes here</p>
                <p class="upload-subtitle">or click to browse</p>
                <p class="upload-supported">
                    Supported formats: PDF • DOCX • TXT • PPTX • PPT
                </p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_upload_preview(
    uploaded_file,
    timestamp: str,
    presentation_metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Render the selected file preview panel."""
    file_type = Path(uploaded_file.name).suffix.lower().lstrip(".").upper()
    file_size = _format_file_size(len(uploaded_file.getvalue()))
    preview_items = [
        ("File type", escape(file_type)),
        ("File size", escape(file_size)),
    ]

    if presentation_metadata:
        preview_items.append(
            ("Slides", str(int(presentation_metadata.get("slide_count", 0))))
        )
    preview_items.extend(
        [
            ("Upload timestamp", escape(timestamp)),
            ("Status", "Validated and queued"),
        ]
    )
    if presentation_metadata and presentation_metadata.get("author"):
        preview_items.append(("Author", escape(str(presentation_metadata["author"]))))
    if presentation_metadata and presentation_metadata.get("created"):
        preview_items.append(("Created", escape(str(presentation_metadata["created"]))))

    preview_grid = "".join(
        f"""
        <div>
            <div class="upload-preview-label">{escape(label)}</div>
            <div class="upload-preview-value">{value}</div>
        </div>
        """
        for label, value in preview_items
    )

    preview_text = ""
    if presentation_metadata and presentation_metadata.get("preview"):
        preview_text = f"""
        <div class="upload-preview-note">
            <div class="upload-preview-label">Preview</div>
            <div class="page-description" style="margin-top: 0.35rem;">
                {escape(str(presentation_metadata["preview"]))}
            </div>
        </div>
        """

    st.markdown(
        f"""
        <section class="upload-preview">
            <div class="meta-row">
                <span class="meta-pill meta-pill--accent">Ready for processing</span>
            </div>
            <p class="page-title" style="font-size: 1.1rem; margin-bottom: 0;">
                {escape(uploaded_file.name)}
            </p>
            <p class="page-description" style="margin-top: 0.45rem;">
                File uploaded successfully and ready for processing.
            </p>
            <div class="upload-preview-grid">
                {preview_grid}
            </div>
            {preview_text}
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_upload_page(config: Dict[str, Any]) -> None:
    """Render the upload page."""
    render_page_header(
        "Upload Source Material",
        (
            "Import lecture notes, reading packets, or scanned class material and "
            "convert them into structured study references."
        ),
        "Ingestion Workspace",
    )

    _render_upload_dropzone()

    supported_extensions = [ext.lstrip(".") for ext in _get_supported_extensions()]
    max_file_size_mb = int(config.get("max_file_size_mb", 50))
    supported_label = "PDF, DOCX, TXT, PPTX, PPT"
    uploaded_file = st.file_uploader(
        "Upload a lecture note file",
        type=supported_extensions,
        accept_multiple_files=False,
        help=f"Accepted formats: {supported_label}",
        key=UPLOAD_KEY,
    )

    st.caption("Supported formats: PDF • DOCX • TXT • PPTX • PPT")

    if not uploaded_file:
        st.info("Drag your lecture notes here or click to browse for a file.")
        return

    validation_error = _validate_uploaded_file(uploaded_file, max_file_size_mb)
    upload_timestamp = _get_upload_timestamp(uploaded_file)
    presentation_metadata: Optional[Dict[str, Any]] = None
    extension = Path(uploaded_file.name).suffix.lower()
    if validation_error is None and extension in {".pptx", ".ppt"}:
        try:
            presentation_metadata = _inspect_presentation(
                uploaded_file.getvalue(),
                extension,
            )
        except IngestionError as exc:
            validation_error = str(exc)

    if validation_error:
        st.error(validation_error)
    else:
        _render_upload_preview(
            uploaded_file,
            upload_timestamp,
            presentation_metadata,
        )

    stepper_placeholder = st.empty()
    with stepper_placeholder.container():
        render_processing_stepper()

    action_columns = st.columns([1, 1.6, 1])
    with action_columns[1]:
        should_process = st.button(
            "Generate Structured Notes",
            use_container_width=True,
            disabled=validation_error is not None,
        )

    if should_process:
        with st.spinner("Processing your lecture notes..."):
            process_uploaded_file(uploaded_file, config, stepper_placeholder)


def _estimate_page_count(file_path: str, extension: str) -> int:
    """Estimate pages for session-level UI statistics."""
    if extension in {".pptx", ".ppt"}:
        try:
            metadata = extract_presentation_metadata(file_path, extension)
            return max(1, int(metadata.get("slide_count", 1)))
        except IngestionError:
            return 1
    if extension != ".pdf":
        return 1
    try:
        import fitz

        with fitz.open(file_path) as document:
            return max(1, len(document))
    except Exception:
        return 1


def _show_stepper(placeholder: Any, active_step: int, failed: bool = False) -> None:
    """Update the processing stepper in place."""
    with placeholder.container():
        render_processing_stepper(active_step, failed)


def process_uploaded_file(
    uploaded_file: Any,
    config: Dict[str, Any],
    stepper_placeholder: Any,
) -> None:
    """Process a single uploaded file through the pipeline."""
    started_at = time.perf_counter()
    active_step = 1
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{uploaded_file.name}**")
        with col2:
            file_size = len(uploaded_file.getvalue()) / 1024
            st.caption(f"{file_size:.1f} KB")
        with col3:
            ext = Path(uploaded_file.name).suffix.lower()
            st.caption(ext)

        progress_bar = st.progress(0, text="Starting...")

        tmp_path = ""
        try:
            progress_bar.progress(10, text="Saving file...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            page_count = _estimate_page_count(tmp_path, ext)

            _show_stepper(stepper_placeholder, active_step)
            progress_bar.progress(30, text="Extracting text...")
            raw_text = extract_text(tmp_path, ext, config)

            if not raw_text or len(raw_text.strip()) < 10:
                st.warning("Very little text extracted. File may be scanned.")
                raw_text = raw_text or ""

            active_step = 2
            _show_stepper(stepper_placeholder, active_step)
            progress_bar.progress(50, text="Cleaning text...")
            cleaned = clean_text(raw_text)

            active_step = 3
            _show_stepper(stepper_placeholder, active_step)
            progress_bar.progress(70, text="AI processing (this may take a while)...")
            metadata = generate_structured_notes(cleaned, config)

            active_step = 4
            _show_stepper(stepper_placeholder, active_step)
            progress_bar.progress(90, text="Saving to database...")
            doc_id = save_document(uploaded_file.name, raw_text, cleaned, metadata)

            duration = time.perf_counter() - started_at
            durations = st.session_state.setdefault("processing_durations", [])
            durations.append(duration)
            st.session_state["pages_processed"] = (
                int(st.session_state.get("pages_processed", 0)) + page_count
            )
            _show_stepper(stepper_placeholder, 5)
            progress_bar.progress(100, text="Processing complete")
            st.success(f"Processed successfully in {duration:.1f}s (ID: {doc_id})")

        except IngestionError as exc:
            _show_stepper(stepper_placeholder, active_step, failed=True)
            progress_bar.empty()
            st.error(f"Ingestion error: {exc}")
        except Exception as exc:
            _show_stepper(stepper_placeholder, active_step, failed=True)
            progress_bar.empty()
            st.error(f"Error: {exc}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)


def extract_text(file_path: str, ext: str, config: Dict[str, Any]) -> str:
    """Extract text based on file extension."""
    if ext == ".pdf":
        try:
            return extract_text_from_pdf(file_path)
        except Exception:
            if config.get("tesseract_enabled", False) and is_tesseract_available(
                config.get("tesseract_path")
            ):
                return ocr_pdf(
                    file_path,
                    lang=config.get("tesseract_lang", "eng"),
                    tesseract_path=config.get("tesseract_path"),
                )
            raise
    if ext == ".docx":
        return extract_text_from_docx(file_path)
    if ext == ".txt":
        return extract_text_from_txt(file_path)
    if ext in (".pptx", ".ppt"):
        return extract_text_from_pptx(file_path)
    if ext in (".png", ".jpg", ".jpeg"):
        if config.get("tesseract_enabled", False):
            from src.ingestion.ocr_processor import ocr_image

            return ocr_image(
                file_path,
                lang=config.get("tesseract_lang", "eng"),
                tesseract_path=config.get("tesseract_path"),
            )
        raise IngestionError("Image files require OCR. Enable OCR in Settings.")
    raise IngestionError(f"Unsupported format: {ext}")
