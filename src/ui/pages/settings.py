# SPDX-License-Identifier: AGPL-3.0-only
"""Settings page for Streamlit UI with multilingual support."""

from __future__ import annotations

import logging
from typing import Any

import streamlit as st

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
from src.utils.translations import t

logger = logging.getLogger(__name__)

TESSERACT_STATUS_KEY = "settings_tesseract_status"
OLLAMA_STATUS_KEY = "settings_ollama_status"
OLLAMA_MODELS_KEY = "settings_ollama_models"


def _ensure_settings_state(config: dict[str, Any]) -> None:
    """Initialize settings-related session state."""
    st.session_state.setdefault("llm_backend", config.get("llm_backend", "ollama"))
    st.session_state.setdefault(
        "ollama_base_url", config.get("ollama_base_url", "http://localhost:11434")
    )
    st.session_state.setdefault("ollama_model", config.get("ollama_model", "phi3:mini"))
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
        st.session_state[OLLAMA_MODELS_KEY] = detected_models or (
            [current_model] if current_model else []
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
            st.markdown(f"**{t('settings.label_connection_status')}**")
            if tesseract_status:
                message = (
                    t("settings.status_connected")
                    if tesseract_status.get("ok")
                    else tesseract_status.get("message", t("settings.status_not_tested"))
                )
                level = st.success if tesseract_status.get("ok") else st.error
                level(t("settings.status_tesseract_connected", message=message))
            else:
                st.info(t("settings.status_tesseract_not_tested"))

            if ollama_status:
                message = (
                    t("settings.status_connected")
                    if ollama_status.get("ok")
                    else ollama_status.get("message", t("settings.status_not_tested"))
                )
                level = st.success if ollama_status.get("ok") else st.error
                level(t("settings.status_ollama_connected", message=message))
            else:
                st.info(t("settings.status_ollama_not_tested"))

    with col2:
        with st.container(border=True):
            st.markdown(f"**{t('settings.label_version_info')}**")
            tesseract_version = (
                tesseract_status.get("version", t("common.not_available"))
                or t("common.not_available")
            )
            ollama_version = (
                ollama_status.get("version", t("common.not_available"))
                or t("common.not_available")
            )
            st.caption(t("settings.label_tesseract_version", version=tesseract_version))
            st.caption(t("settings.label_ollama_version", version=ollama_version))
            models = ollama_status.get("models", [])
            if models:
                st.caption(
                    t("settings.label_model_status", count=len(models))
                )
            else:
                st.caption(t("settings.label_no_models"))


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
        llm_backend="ollama",
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
            "temperature": updated.temperature,
            "context_length": updated.context_length,
            "tesseract_enabled": updated.tesseract_enabled,
            "tesseract_path": updated.tesseract_path,
            "database_url": updated.database_url,
        }
    )
    st.success(t("settings.success_saved"))


def _reset_settings() -> None:
    """Reset persisted settings to defaults."""
    defaults = reset_config()
    st.session_state["llm_backend"] = defaults.llm_backend
    st.session_state["ollama_base_url"] = defaults.ollama_base_url
    st.session_state["ollama_model"] = defaults.ollama_model
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
            "temperature": defaults.temperature,
            "context_length": defaults.context_length,
            "tesseract_enabled": defaults.tesseract_enabled,
            "tesseract_path": defaults.tesseract_path,
            "database_url": defaults.database_url,
        }
    )
    st.success(t("settings.success_reset"))
    st.rerun()


def render_settings(config: dict[str, Any]) -> None:
    """Render the settings page."""
    _ensure_settings_state(config)

    render_page_header(
        t("settings.page_title"),
        t("settings.page_description"),
        t("settings.page_eyebrow"),
    )

    with st.expander(t("settings.section_ai_ocr"), expanded=True):
        st.markdown(f"### {t('settings.section_ocr')}")
        st.text_input(
            t("settings.label_tesseract_path"),
            key="tesseract_path",
            help=t("settings.help_tesseract_path"),
        )
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            st.button(
                t("settings.button_browse"),
                disabled=True,
                help=t("settings.help_browse"),
            )
        with t_col2:
            if st.button(t("settings.button_auto_detect"), use_container_width=True):
                detected_path = detect_tesseract_path()
                if detected_path:
                    st.session_state["tesseract_path"] = detected_path
                    st.success(
                        t("settings.success_tesseract_detected", path=detected_path)
                    )
                else:
                    st.warning(t("settings.warning_tesseract_not_found"))
        with t_col3:
            if st.button(t("settings.button_test_tesseract"), use_container_width=True):
                st.session_state[TESSERACT_STATUS_KEY] = test_tesseract_connection(
                    st.session_state.get("tesseract_path", "")
                )

        st.markdown("---")
        st.markdown(f"### {t('settings.section_ai')}")
        st.text_input(
            t("settings.label_ollama_host"),
            key="ollama_base_url",
            help=t("settings.help_ollama_host"),
        )

        host = st.session_state.get("ollama_base_url", "http://localhost:11434")
        detect_col, refresh_col, test_col = st.columns(3)
        with detect_col:
            if st.button(t("settings.button_detect_ollama"), use_container_width=True):
                detected_host = detect_ollama_host(host)
                if detected_host:
                    st.session_state["ollama_base_url"] = detected_host
                    models = get_ollama_models(detected_host)
                    _store_models(models, st.session_state.get("ollama_model", ""))
                    st.success(t("settings.success_ollama_detected"))
                else:
                    st.error(t("settings.error_ollama_not_found"))
        with refresh_col:
            if st.button(t("settings.button_refresh_models"), use_container_width=True):
                models = get_ollama_models(host)
                _store_models(models, st.session_state.get("ollama_model", ""))
                if models:
                    st.success(t("settings.success_models_refreshed"))
                else:
                    st.warning(t("settings.warning_no_models"))
        with test_col:
            if st.button(t("settings.button_test_ollama"), use_container_width=True):
                result = test_ollama_connection(
                    host,
                    st.session_state.get("ollama_model", ""),
                )
                st.session_state[OLLAMA_STATUS_KEY] = result
                _store_models(
                    result.get("models", []),
                    st.session_state.get("ollama_model", ""),
                )

        detected_models = st.session_state.get(OLLAMA_MODELS_KEY, [])
        current_model = st.session_state.get("ollama_model", "phi3:mini")
        model_options = list(detected_models)
        if current_model and current_model not in model_options:
            model_options.append(current_model)
        if not model_options:
            model_options = [t("settings.no_models_detected")]

        st.selectbox(
            t("settings.label_model"),
            options=model_options,
            index=(
                model_options.index(current_model)
                if current_model in model_options
                else 0
            ),
            key="ollama_model",
            disabled=model_options == [t("settings.no_models_detected")],
            help=t("settings.help_model"),
        )

        _render_status_panels()

    with st.expander(t("settings.section_processing"), expanded=True):
        st.session_state["llm_backend"] = "ollama"
        st.info(t("settings.label_backend_info"))

        st.slider(
            t("settings.label_temperature"),
            min_value=0.0,
            max_value=1.0,
            step=0.05,
            key="temperature",
            help=t("settings.help_temperature"),
        )
        st.number_input(
            t("settings.label_context_length"),
            min_value=512,
            max_value=8192,
            step=512,
            key="context_length",
        )
        st.toggle(
            t("settings.label_enable_ocr"),
            key="tesseract_enabled",
            help=t("settings.help_enable_ocr"),
        )

    with st.expander(t("settings.section_storage"), expanded=False):
        st.text_input(
            t("settings.label_database_path"),
            key="database_url",
        )

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button(t("settings.button_save"), use_container_width=True):
            _save_settings()
    with action_col2:
        if st.button(t("settings.button_reset"), use_container_width=True):
            _reset_settings()