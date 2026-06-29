# SPDX-License-Identifier: GPL-3.0-or-later
"""System status dashboard page."""

import platform
import sys
from typing import Any, Dict

import streamlit as st

from src.ai.model_manager import is_ollama_available, is_llama_cpp_available
from src.ingestion.ocr_processor import is_tesseract_available
from src.storage.database import get_stats


def render_system_status(config: Dict[str, Any]) -> None:
    """Render the system status dashboard."""
    st.header("📊 System Status")
    st.markdown("Real-time status of models, storage, and system health.")

    col1, col2, col3 = st.columns(3)

    with col1:
        ollama_ok = is_ollama_available(
            config.get("ollama_base_url", "http://localhost:11434")
        )
        if ollama_ok:
            st.metric("Ollama", "✅ Running")
        else:
            st.metric("Ollama", "❌ Not detected")

    with col2:
        tesseract_ok = is_tesseract_available()
        if tesseract_ok:
            st.metric("Tesseract OCR", "✅ Available")
        else:
            st.metric("Tesseract OCR", "⚠️ Not installed")

    with col3:
        model_path = config.get("llama_cpp_model_path", "")
        llama_ok = is_llama_cpp_available(model_path) if model_path else False
        if llama_ok:
            st.metric("llama.cpp", "✅ Model ready")
        elif model_path:
            st.metric("llama.cpp", "❌ Model not found")
        else:
            st.metric("llama.cpp", "⏸️ Not configured")

    st.markdown("---")

    try:
        stats = get_stats()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Documents", stats.get("total_documents", 0))
        with col2:
            st.metric("Processed", stats.get("processed", 0))
        with col3:
            st.metric("Errors", stats.get("errors", 0))
        with col4:
            db_size = stats.get("database_size_bytes", 0)
            st.metric("DB Size", f"{db_size / 1024:.1f} KB" if db_size else "0 KB")
    except Exception as e:
        st.warning(f"Could not read database stats: {e}")

    st.markdown("---")

    with st.expander("🖥️ System Information"):
        st.json({
            "Platform": platform.platform(),
            "Python": sys.version,
            "Architecture": platform.machine(),
            "Processor": platform.processor(),
        })

    with st.expander("📦 Installed Packages Check"):
        packages = {
            "PyMuPDF (fitz)": False,
            "python-docx": False,
            "streamlit": False,
            "SQLAlchemy": False,
            "requests": False,
            "pytesseract": False,
            "Pillow": False,
            "llama-cpp-python": False,
            "unidecode": False,
        }
        for pkg in packages:
            try:
                __import__(pkg.split()[0].replace("-", "_"))
                packages[pkg] = True
            except ImportError:
                pass

        for pkg, installed in packages.items():
            icon = "✅" if installed else "❌"
            st.markdown(f"{icon} **{pkg}**")
