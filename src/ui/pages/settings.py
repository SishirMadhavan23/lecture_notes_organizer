# SPDX-License-Identifier: GPL-3.0-or-later
"""Settings page for Streamlit UI."""

from typing import Any, Dict

import streamlit as st

from src.ai.model_manager import is_ollama_available, is_llama_cpp_available
from src.ingestion.ocr_processor import is_tesseract_available


def render_settings(config: Dict[str, Any]) -> None:
    """Render the settings page."""
    st.header("⚙️ Settings")
    st.markdown("Configure application preferences.")

    with st.expander("🤖 AI / LLM Settings", expanded=True):
        backend = st.selectbox(
            "LLM Backend",
            options=["ollama", "llama.cpp"],
            index=0 if config.get("llm_backend", "ollama") == "ollama" else 1,
            help="Ollama: easier setup. llama.cpp: direct GGUF support.",
        )
        st.session_state["llm_backend"] = backend

        if backend == "ollama":
            st.text_input(
                "Ollama Base URL",
                value=config.get("ollama_base_url", "http://localhost:11434"),
                key="ollama_base_url",
            )
            st.text_input(
                "Model Name",
                value=config.get("ollama_model", "phi3:mini"),
                key="ollama_model",
                help="e.g., phi3:mini, qwen2.5:1.5b",
            )
            available = is_ollama_available(
                config.get("ollama_base_url", "http://localhost:11434")
            )
            if available:
                st.success("✅ Ollama is running")
            else:
                st.warning("⚠️ Ollama not detected. Start it with: ollama serve")
        else:
            st.text_input(
                "GGUF Model Path",
                value=config.get("llama_cpp_model_path", ""),
                key="llama_cpp_model_path",
                help="Full path to .gguf model file",
            )
            path = config.get("llama_cpp_model_path", "")
            if path and is_llama_cpp_available(path):
                st.success("✅ Model file found")
            elif path:
                st.error("❌ Model file not found")

        temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0, value=config.get("temperature", 0.1),
            step=0.05,
            help="Lower = more deterministic, Higher = more creative",
        )
        st.session_state["temperature"] = temperature

        context = st.number_input(
            "Context Length (tokens)",
            min_value=512, max_value=8192, value=config.get("context_length", 4096),
            step=512,
        )
        st.session_state["context_length"] = context

    with st.expander("📷 OCR Settings", expanded=True):
        ocr_enabled = st.toggle(
            "Enable OCR",
            value=config.get("tesseract_enabled", False),
            help="Requires Tesseract OCR installed on system",
        )
        st.session_state["tesseract_enabled"] = ocr_enabled

        if ocr_enabled:
            if is_tesseract_available():
                st.success("✅ Tesseract OCR is installed")
            else:
                st.error(
                    "❌ Tesseract not found. Download from: "
                    "https://github.com/UB-Mannheim/tesseract/wiki"
                )

    with st.expander("💾 Storage", expanded=False):
        st.text_input(
            "Database Path",
            value=config.get("database_url", "sqlite:///data/lecture_notes.db"),
            key="database_url",
        )

    st.markdown("---")
    st.info("Settings are saved in the current session. "
            "Set environment variables for permanent configuration.")
