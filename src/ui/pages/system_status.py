# SPDX-License-Identifier: GPL-3.0-or-later
"""System status dashboard page."""

import platform
import sys
from html import escape
from typing import Any

import streamlit as st

from src.ai.model_manager import is_ollama_available
from src.ingestion.ocr_processor import is_tesseract_available
from src.storage.database import get_stats
from src.ui.components.dashboard import render_stat_cards, render_status_card
from src.ui.components.page_header import render_page_header


def render_system_status(config: dict[str, Any]) -> None:
    """Render the system status dashboard."""
    render_page_header(
        "System Status",
        (
            "Review local model readiness, OCR availability, storage volume, and "
            "environment health before processing new material."
        ),
        "Operations",
    )

    ollama_ok = is_ollama_available(
        config.get("ollama_base_url", "http://localhost:11434")
    )
    tesseract_ok = is_tesseract_available(config.get("tesseract_path"))

    st.markdown("### Configuration health")
    col1, col2, col3 = st.columns(3)
    with col1:
        render_status_card(
            "Ollama",
            "Running" if ollama_ok else "Unavailable",
            (
                "Local model server is ready."
                if ollama_ok
                else "Server could not be reached."
            ),
            "success" if ollama_ok else "error",
            "AI",
        )
    with col2:
        render_status_card(
            "Tesseract OCR",
            "Configured" if tesseract_ok else "Not installed",
            (
                "OCR is available for scanned notes."
                if tesseract_ok
                else "Install or select an executable."
            ),
            "success" if tesseract_ok else "error",
            "OCR",
        )
    with col3:
        render_status_card(
            "SQLite",
            "Ready",
            "Local storage is initialized on this machine.",
            "success",
            "DB",
        )

    st.markdown("### Processing statistics")

    try:
        stats = get_stats()
        durations = st.session_state.get("processing_durations", [])
        average_duration = sum(durations) / len(durations) if durations else 0.0
        current_model = config.get("ollama_model", "Not selected")
        render_stat_cards(
            (
                {
                    "label": "Documents processed",
                    "value": str(stats.get("processed", 0)),
                    "hint": "Stored in SQLite",
                },
                {
                    "label": "Pages processed",
                    "value": str(st.session_state.get("pages_processed", 0)),
                    "hint": "This session",
                },
                {
                    "label": "Average processing time",
                    "value": f"{average_duration:.1f}s" if durations else "--",
                    "hint": "This session",
                },
                {
                    "label": "Current AI model",
                    "value": str(current_model),
                    "hint": "Ollama",
                },
            )
        )
    except Exception as e:
        st.warning(f"Could not read database stats: {e}")

    st.markdown("---")

    with st.expander("System information"):
        st.json(
            {
                "Platform": platform.platform(),
                "Python": sys.version,
                "Architecture": platform.machine(),
                "Processor": platform.processor(),
            }
        )

    with st.expander("Installed packages"):
        packages = {
            "PyMuPDF (fitz)": "fitz",
            "python-docx": "docx",
            "streamlit": "streamlit",
            "SQLAlchemy": "sqlalchemy",
            "requests": "requests",
            "pytesseract": "pytesseract",
            "Pillow": "PIL",
            "unidecode": "unidecode",
        }
        package_status = {label: False for label in packages}
        for label, module_name in packages.items():
            try:
                __import__(module_name)
                package_status[label] = True
            except ImportError:
                pass

        rows = "".join(
            f'<div class="status-list-row"><span>{escape(pkg)}</span>'
            f'<span class="status-badge '
            f'status-badge--{"success" if installed else "error"}">'
            f"{'Configured' if installed else 'Not installed'}</span></div>"
            for pkg, installed in package_status.items()
        )
        st.markdown(f'<div class="status-list">{rows}</div>', unsafe_allow_html=True)
