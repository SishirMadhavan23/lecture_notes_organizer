# SPDX-License-Identifier: GPL-3.0-or-later
"""Upload page for Streamlit UI - handles file upload and processing."""

import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

from src.ai.model_manager import generate_structured_notes
from src.ingestion.docx_extractor import extract_text_from_docx
from src.ingestion.ocr_processor import is_tesseract_available, ocr_pdf
from src.ingestion.pdf_extractor import extract_text_from_pdf
from src.ingestion.txt_extractor import extract_text_from_txt
from src.preprocessing.text_cleaner import clean_text
from src.storage.database import save_document
from src.utils.exceptions import IngestionError


def render_upload_page(config: Dict[str, Any]) -> None:
    """Render the upload page."""
    st.header("📤 Upload Lecture Notes")
    st.markdown("Upload PDF, DOCX, or TXT files to convert into structured notes.")

    uploaded_files = st.file_uploader(
        "Choose files",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="Drag and drop files here. Supported: PDF, DOCX, TXT, PNG, JPG",
    )

    if not uploaded_files:
        st.info("Upload files to get started.")
        return

    for uploaded_file in uploaded_files:
        process_uploaded_file(uploaded_file, config)


def process_uploaded_file(uploaded_file, config: Dict[str, Any]) -> None:
    """Process a single uploaded file through the pipeline."""
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
            # Step 1: Save to temp file
            progress_bar.progress(10, text="Saving file...")
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=ext
            ) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            # Step 2: Extract text
            progress_bar.progress(30, text="Extracting text...")
            raw_text = extract_text(tmp_path, ext, config)

            if not raw_text or len(raw_text.strip()) < 10:
                st.warning("Very little text extracted. File may be scanned.")
                raw_text = raw_text or ""

            # Step 3: Clean text
            progress_bar.progress(50, text="Cleaning text...")
            cleaned = clean_text(raw_text)

            # Step 4: AI processing
            progress_bar.progress(70, text="AI processing (this may take a while)...")
            metadata = generate_structured_notes(cleaned, config)

            # Step 5: Save to database
            progress_bar.progress(90, text="Saving to database...")
            doc_id = save_document(uploaded_file.name, raw_text, cleaned, metadata)

            progress_bar.progress(100, text="✅ Complete!")
            st.success(f"Processed! (ID: {doc_id})")

        except IngestionError as e:
            progress_bar.empty()
            st.error(f"📄 Ingestion error: {e}")
        except Exception as e:
            progress_bar.empty()
            st.error(f"❌ Error: {e}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)


def extract_text(file_path: str, ext: str, config: Dict[str, Any]) -> str:
    """Extract text based on file extension."""
    if ext == ".pdf":
        try:
            return extract_text_from_pdf(file_path)
        except Exception:
            if config.get("tesseract_enabled", False) and is_tesseract_available():
                return ocr_pdf(file_path)
            raise
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    elif ext in (".png", ".jpg", ".jpeg"):
        if config.get("tesseract_enabled", False):
            from src.ingestion.ocr_processor import ocr_image
            return ocr_image(file_path)
        else:
            raise IngestionError(
                "Image files require OCR. Enable OCR in Settings."
            )
    else:
        raise IngestionError(f"Unsupported format: {ext}")
