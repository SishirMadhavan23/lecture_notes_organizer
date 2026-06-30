# SPDX-License-Identifier: AGPL-3.0-only
"""Offline AI Lecture Notes Organizer entry point with multilingual support."""

from __future__ import annotations

import os
import sys

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from src.storage.database import get_engine
from src.ui.components.dashboard import render_footer
from src.ui.components.sidebar import render_sidebar
from src.ui.pages.flashcards import render_flashcards
from src.ui.pages.search import render_search
from src.ui.pages.settings import render_settings
from src.ui.pages.system_status import render_system_status
from src.ui.pages.upload import render_upload_page
from src.ui.pages.view_notes import render_view_notes
from src.ui.theme import apply_theme
from src.utils.config import load_config
from src.utils.translations import t


def init_session_state(config: object) -> None:
    """Initialize Streamlit session state."""
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Upload"
    requested_page = st.query_params.get("page")
    valid_pages: set[str] = {
        "Upload",
        "View Notes",
        "Flashcards",
        "Search",
        "Settings",
        "System Status",
    }
    if requested_page in valid_pages:
        st.session_state.current_page = requested_page
    if "config" not in st.session_state:
        # Build config dict from AppConfig
        st.session_state.config = {
            "llm_backend": config.llm_backend,
            "ollama_base_url": config.ollama_base_url,
            "ollama_model": config.ollama_model,
            "temperature": config.temperature,
            "context_length": config.context_length,
            "tesseract_enabled": config.tesseract_enabled,
            "tesseract_path": config.tesseract_path,
            "tesseract_lang": config.tesseract_lang,
            "database_url": config.database_url,
            "cache_enabled": config.cache_enabled,
        }
    # Initialize language preference
    if "language" not in st.session_state:
        st.session_state["language"] = "en"


def main() -> None:
    """Application entry point."""
    st.set_page_config(
        page_title=t("app.title"),
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_theme()

    config = load_config()
    init_session_state(config)

    # Initialize database on first run
    if "db_initialized" not in st.session_state:
        get_engine()
        st.session_state.db_initialized = True

    render_sidebar()

    # Page routing
    page = st.session_state.get("current_page", "Upload")
    cfg = st.session_state.get("config", {})

    if page == "Upload":
        render_upload_page(cfg)
    elif page == "View Notes":
        render_view_notes(cfg)
    elif page == "Flashcards":
        render_flashcards(cfg)
    elif page == "Search":
        render_search(cfg)
    elif page == "Settings":
        render_settings(cfg)
        # Update config from session state
        for key in (
            "llm_backend",
            "temperature",
            "context_length",
            "tesseract_enabled",
            "ollama_base_url",
            "ollama_model",
            "tesseract_path",
            "database_url",
        ):
            if key in st.session_state:
                cfg[key] = st.session_state[key]
    elif page == "System Status":
        render_system_status(cfg)

    render_footer()


if __name__ == "__main__":
    main()
