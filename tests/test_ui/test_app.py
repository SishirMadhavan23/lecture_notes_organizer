"""Tests for the Streamlit app entrypoint."""

from __future__ import annotations

from typing import Any

import pytest

import src.app as app
from src.utils.config import AppConfig


def test_init_session_state_respects_query_params(
    mock_streamlit_session_state: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    mock_config: AppConfig,
) -> None:
    """Session initialization should accept valid page query params and defaults."""
    import streamlit as st

    mock_streamlit_session_state.clear()
    monkeypatch.setattr(st, "query_params", {"page": "Search"})

    app.init_session_state(mock_config)

    assert st.session_state.current_page == "Search"
    assert st.session_state["language"] == "en"
    assert st.session_state["config"]["ollama_model"] == mock_config.ollama_model

    mock_streamlit_session_state.clear()
    monkeypatch.setattr(st, "query_params", {"page": "Unknown"})
    app.init_session_state(mock_config)
    assert st.session_state.current_page == "Upload"


def test_main_initializes_database_and_routes_pages(
    mock_streamlit: Any,
    mock_config: AppConfig,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The app should initialize once and dispatch each supported page."""
    monkeypatch.setattr(app, "t", lambda key: "Lecture Notes Organizer")
    monkeypatch.setattr(app, "apply_theme", lambda: None)
    monkeypatch.setattr(app, "load_config", lambda: mock_config)
    monkeypatch.setattr(app, "render_sidebar", lambda: None)
    monkeypatch.setattr(app, "render_footer", lambda: None)
    monkeypatch.setattr(app, "get_engine", lambda: "engine")

    page_calls: list[str] = []
    monkeypatch.setattr(
        app, "render_upload_page", lambda cfg: page_calls.append("Upload")
    )
    monkeypatch.setattr(
        app, "render_view_notes", lambda cfg: page_calls.append("View Notes")
    )
    monkeypatch.setattr(
        app, "render_flashcards", lambda cfg: page_calls.append("Flashcards")
    )
    monkeypatch.setattr(app, "render_search", lambda cfg: page_calls.append("Search"))
    monkeypatch.setattr(
        app, "render_settings", lambda cfg: page_calls.append("Settings")
    )
    monkeypatch.setattr(
        app, "render_system_status", lambda cfg: page_calls.append("System Status")
    )

    for page in (
        "Upload",
        "View Notes",
        "Flashcards",
        "Search",
        "Settings",
        "System Status",
    ):
        mock_streamlit.session_state.clear()
        mock_streamlit.session_state.update({"current_page": page, "config": {}})
        app.main()

    assert page_calls == [
        "Upload",
        "View Notes",
        "Flashcards",
        "Search",
        "Settings",
        "System Status",
    ]
    assert mock_streamlit.set_page_config.call_count == 6


def test_main_updates_session_config_after_settings(
    mock_streamlit: Any,
    mock_config: AppConfig,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Settings routing should sync editable session values back into config."""
    monkeypatch.setattr(app, "t", lambda key: "Lecture Notes Organizer")
    monkeypatch.setattr(app, "apply_theme", lambda: None)
    monkeypatch.setattr(app, "load_config", lambda: mock_config)
    monkeypatch.setattr(app, "render_sidebar", lambda: None)
    monkeypatch.setattr(app, "render_footer", lambda: None)
    monkeypatch.setattr(app, "get_engine", lambda: "engine")
    monkeypatch.setattr(app, "render_settings", lambda cfg: None)

    mock_streamlit.session_state.clear()
    mock_streamlit.session_state.update(
        {
            "current_page": "Settings",
            "config": {"ollama_model": "old"},
            "temperature": 0.2,
            "context_length": 2048,
            "tesseract_enabled": True,
            "ollama_base_url": "http://new-host",
            "ollama_model": "new-model",
            "tesseract_path": "/new/path",
            "database_url": "sqlite:///new.db",
        }
    )

    app.main()

    assert mock_streamlit.session_state["config"]["ollama_model"] == "new-model"
    assert mock_streamlit.session_state["config"]["database_url"] == "sqlite:///new.db"
