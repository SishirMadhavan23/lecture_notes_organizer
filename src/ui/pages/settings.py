"""Settings page for Streamlit UI."""

from __future__ import annotations

import logging
from typing import Any, Dict

import streamlit as st

from src.ai.model_manager import is_llama_cpp_available
from src.ui.components.page_header import render_page_header
from src.utils.config import (
    AppConfig,
    get_default_tesseract_path,
    load_config,
    reset_config,
    save_config,
)
from src.utils.integrations import (
    detect_ollama_host,
    detect_tesseract_path,
    get_ollama_models,
    test_ollama_connection,
    test_tesseract_connection,
)

logger = logging.getLogger(__name__)

TESSERACT_STATUS_KEY = "settings_tesseract_status"
OLLAMA_STATUS_KEY = "settings_ollama_status"
OLLAMA_MODELS_KEY = "settings_ollama_models"


def _ensure_settings_state(config: Dict[str, Any]) -> None:
    """Initialize settings-related session state."""
    st.session_state.setdefault("llm_backend", config.get("llm_backend", "ollama"))
    st.session_state.setdefault(
        "ollama_base_url", config.get("ollama_base_url", "http://localhost:11434")
    )
    st.session_state.setdefault(
        "ollama_model", config.get("ollama_model", "phi3:mini")
    )
    st.session_state.setdefault(
        "llama_cpp_model_path", config.get("llama_cpp_model_path", "")
    )
    st.session_state.setdefault("temperature", config.get("temperature", 0.1))
    st.session_state.setdefault("context_length", config.get("context_length", 4096))
    st.session_state.setdefault(
        "tesseract_enabled", config.get("tesseract_enabled", False)
    )
    st.session_state.setdefault(
        "tesseract_path", config.get("tesseract_path", get_default_tesseract_path())
    )
    st.session_state.setdefault(
        "database_url", config.get("database_url", "sqlite:///data/lecture_notes.db")
    )

    current_model = st.session_state.get("ollama_model", "phi3:mini")
    if OLLAMA_MODELS_KEY not in st.session_state:
        detected_models = get_ollama_models(st.session_state.get("ollama_base_url", ""))
        st.session_state[OLLAMA_MODELS_KEY] = (
            detected_models or ([current_model] if current_model else [])
        )
    st.session_state.setdefault(TESSERACT_STATUS_KEY, {})
    st.session_state.setdefault(OLLAMA_STATUS_KEY, {})


def _store_models(models: list[str], fallback_model: str) -> None:
    """Store detected Ollama models in session state."""
    unique_models = list(dict.fromkeys(model for model in models if model))
    if not unique_models and fallback_model:
        unique_models = [fallback_model]
    st.session_state[OLLAMA_MODELS_KEY] = unique_models
    if unique_models and st.session_state.get("ollama_model") not in unique_models:
        st.session_state["ollama_model"] = unique_models[0]


def _render_status_panels() -> None:
    """Render connection and version status panels."""
    tesseract_status = st.session_state.get(TESSERACT_STATUS_KEY, {})
    ollama_status = st.session_state.get(OLLAMA_STATUS_KEY, {})

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Connection Status**")
            if tesseract_status:
                message = (
                    "Connected" if tesseract_status.get("ok") else tesseract_status.get("message", "Not tested")
                )
                level = st.success if tesseract_status.get("ok") else st.error
                level(f"Tesseract: {message}")
            else:
                st.info("Tesseract connection has not been tested yet.")

            if ollama_status:
                message = (
                    "Ollama Connected"
                    if ollama_status.get("ok")
                    else ollama_status.get("message", "Not tested")
                )
                level = st.success if ollama_status.get("ok") else st.error
                level(f"Ollama: {message}")
            else:
                st.info("Ollama connection has not been tested yet.")

    with col2:
        with st.container(border=True):
            st.markdown("**Version Information**")
            st.caption(
                f"Tesseract: {tesseract_status.get('version', 'Unavailable') or 'Unavailable'}"
            )
            st.caption(
                f"Ollama: {ollama_status.get('version', 'Unavailable') or 'Unavailable'}"
            )
            models = ollama_status.get("models", [])
            if models:
                st.caption(f"Model Status: {len(models)} installed model(s) detected")
            else:
                st.caption("Model Status: No detected models yet")


def _save_settings() -> None:
    """Persist settings to disk and sync session config."""
    current = load_config()
    updated = AppConfig(
        base_dir=current.base_dir,
        data_dir=current.data_dir,
        model_dir=current.model_dir,
        log_dir=current.log_dir,
        database_url=st.session_state.get("database_url", current.database_url),
        ollama_base_url=st.session_state.get(
            "ollama_base_url", current.ollama_base_url
        ),
        ollama_model=st.session_state.get("ollama_model", current.ollama_model),
        llama_cpp_model_path=st.session_state.get(
            "llama_cpp_model_path", current.llama_cpp_model_path
        ),
        llm_backend=st.session_state.get("llm_backend", current.llm_backend),
        context_length=int(
            st.session_state.get("context_length", current.context_length)
        ),
        temperature=float(st.session_state.get("temperature", current.temperature)),
        tesseract_enabled=bool(
            st.session_state.get("tesseract_enabled", current.tesseract_enabled)
        ),
        tesseract_path=st.session_state.get("tesseract_path", current.tesseract_path),
        tesseract_lang=current.tesseract_lang,
        tesseract_timeout=current.tesseract_timeout,
        max_file_size_mb=current.max_file_size_mb,
        supported_formats=current.supported_formats,
        cache_enabled=current.cache_enabled,
        page_title=current.page_title,
        config_filename=current.config_filename,
    )
    save_config(updated)

    st.session_state.config.update(
        {
            "llm_backend": updated.llm_backend,
            "ollama_base_url": updated.ollama_base_url,
            "ollama_model": updated.ollama_model,
            "llama_cpp_model_path": updated.llama_cpp_model_path,
            "temperature": updated.temperature,
            "context_length": updated.context_length,
            "tesseract_enabled": updated.tesseract_enabled,
            "tesseract_path": updated.tesseract_path,
            "database_url": updated.database_url,
        }
    )
    st.success("Settings saved successfully.")


def _reset_settings() -> None:
    """Reset persisted settings to defaults."""
    defaults = reset_config()
    st.session_state["llm_backend"] = defaults.llm_backend
    st.session_state["ollama_base_url"] = defaults.ollama_base_url
    st.session_state["ollama_model"] = defaults.ollama_model
    st.session_state["llama_cpp_model_path"] = defaults.llama_cpp_model_path or ""
    st.session_state["temperature"] = defaults.temperature
    st.session_state["context_length"] = defaults.context_length
    st.session_state["tesseract_enabled"] = defaults.tesseract_enabled
    st.session_state["tesseract_path"] = defaults.tesseract_path
    st.session_state["database_url"] = defaults.database_url
    st.session_state[TESSERACT_STATUS_KEY] = {}
    st.session_state[OLLAMA_STATUS_KEY] = {}
    _store_models([], defaults.ollama_model)
    st.session_state.config.update(
        {
            "llm_backend": defaults.llm_backend,
            "ollama_base_url": defaults.ollama_base_url,
            "ollama_model": defaults.ollama_model,
            "llama_cpp_model_path": defaults.llama_cpp_model_path,
            "temperature": defaults.temperature,
            "context_length": defaults.context_length,
            "tesseract_enabled": defaults.tesseract_enabled,
            "tesseract_path": defaults.tesseract_path,
            "database_url": defaults.database_url,
        }
    )
    st.success("Settings reset to defaults.")
    st.rerun()


def render_settings(config: Dict[str, Any]) -> None:
    """Render the settings page."""
    _ensure_settings_state(config)

    render_page_header(
        "System Settings",
        (
            "Configure local model behavior, OCR support, and storage preferences "
            "for your offline study workflow."
        ),
        "Configuration",
    )

    with st.expander("AI & OCR Configuration", expanded=True):
        st.markdown("### OCR Configuration")
        st.text_input(
            "Tesseract executable path",
            key="tesseract_path",
            help="Enter the full path to the Tesseract executable on this machine.",
        )
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            st.button(
                "Browse",
                disabled=True,
                help=(
                    "Native executable browsing is not available in standard "
                    "Streamlit browser deployments."
                ),
            )
        with t_col2:
            if st.button("Auto-detect Tesseract", use_container_width=True):
                detected_path = detect_tesseract_path()
                if detected_path:
                    st.session_state["tesseract_path"] = detected_path
                    st.success(f"Detected Tesseract at {detected_path}")
                else:
                    st.warning("No Tesseract installation detected in common locations.")
        with t_col3:
            if st.button("Test Tesseract", use_container_width=True):
                st.session_state[TESSERACT_STATUS_KEY] = test_tesseract_connection(
                    st.session_state.get("tesseract_path", "")
                )

        st.markdown("---")
        st.markdown("### AI Configuration")
        st.text_input(
            "Ollama Host",
            key="ollama_base_url",
            help="Example: http://localhost:11434",
        )

        host = st.session_state.get("ollama_base_url", "http://localhost:11434")
        detect_col, refresh_col, test_col = st.columns(3)
        with detect_col:
            if st.button("Detect Ollama", use_container_width=True):
                detected_host = detect_ollama_host(host)
                if detected_host:
                    st.session_state["ollama_base_url"] = detected_host
                    models = get_ollama_models(detected_host)
                    _store_models(models, st.session_state.get("ollama_model", ""))
                    st.success("Ollama server detected.")
                else:
                    st.error("Unable to detect an Ollama server at the configured host.")
        with refresh_col:
            if st.button("Refresh Models", use_container_width=True):
                models = get_ollama_models(host)
                _store_models(models, st.session_state.get("ollama_model", ""))
                if models:
                    st.success("Installed models refreshed.")
                else:
                    st.warning("No installed models were detected.")
        with test_col:
            if st.button("Test Ollama", use_container_width=True):
                result = test_ollama_connection(
                    host,
                    st.session_state.get("ollama_model", ""),
                )
                st.session_state[OLLAMA_STATUS_KEY] = result
                _store_models(result.get("models", []), st.session_state.get("ollama_model", ""))

        detected_models = st.session_state.get(OLLAMA_MODELS_KEY, [])
        current_model = st.session_state.get("ollama_model", "phi3:mini")
        model_options = list(detected_models)
        if current_model and current_model not in model_options:
            model_options.append(current_model)
        if not model_options:
            model_options = ["No models detected"]

        st.selectbox(
            "Model Dropdown",
            options=model_options,
            index=model_options.index(current_model) if current_model in model_options else 0,
            key="ollama_model",
            disabled=model_options == ["No models detected"],
            help="Detected from `ollama list` or the Ollama API.",
        )

        _render_status_panels()

    with st.expander("Processing Preferences", expanded=True):
        backend = st.selectbox(
            "LLM Backend",
            options=["ollama", "llama.cpp"],
            index=0 if st.session_state.get("llm_backend", "ollama") == "ollama" else 1,
            key="llm_backend",
            help="Ollama: easier setup. llama.cpp: direct GGUF support.",
        )

        if backend == "llama.cpp":
            st.text_input(
                "GGUF Model Path",
                key="llama_cpp_model_path",
                help="Full path to the .gguf model file",
            )
            model_path = st.session_state.get("llama_cpp_model_path", "")
            if model_path and is_llama_cpp_available(model_path):
                st.success("Model file found")
            elif model_path:
                st.error("Model file not found")

        st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            step=0.05,
            key="temperature",
            help="Lower = more deterministic, Higher = more creative",
        )
        st.number_input(
            "Context Length (tokens)",
            min_value=512,
            max_value=8192,
            step=512,
            key="context_length",
        )
        st.toggle(
            "Enable OCR",
            key="tesseract_enabled",
            help="Requires a working Tesseract installation",
        )

    with st.expander("Storage", expanded=False):
        st.text_input(
            "Database Path",
            key="database_url",
        )

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("Save Settings", use_container_width=True):
            _save_settings()
    with action_col2:
        if st.button("Reset Defaults", use_container_width=True):
            _reset_settings()
