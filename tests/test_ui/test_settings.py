"""Tests for the settings page."""

from __future__ import annotations

from typing import Any

import pytest

from src.ui.pages import settings
from src.utils.config import AppConfig


@pytest.fixture
def translated_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Use predictable translation strings in settings tests."""

    def fake_t(key: str, default: str | None = None, **kwargs: Any) -> str:
        if kwargs:
            return f"{key}:{kwargs}"
        return default or key

    monkeypatch.setattr(settings, "t", fake_t)


def test_ensure_settings_state_and_store_models(
    mock_streamlit: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Settings state should initialize defaults and normalize detected models."""
    monkeypatch.setattr(
        settings, "get_default_tesseract_path", lambda: "/usr/bin/tesseract"
    )
    monkeypatch.setattr(
        settings, "get_ollama_models", lambda url: ["phi3:mini", "llama3"]
    )

    settings._ensure_settings_state(
        {"llm_backend": "ollama", "ollama_base_url": "http://ollama"}
    )

    assert mock_streamlit.session_state["ollama_base_url"] == "http://ollama"
    assert mock_streamlit.session_state[settings.OLLAMA_MODELS_KEY] == [
        "phi3:mini",
        "llama3",
    ]

    settings._store_models(["llama3", "phi3:mini", "llama3"], "fallback")
    assert mock_streamlit.session_state[settings.OLLAMA_MODELS_KEY] == [
        "llama3",
        "phi3:mini",
    ]
    assert mock_streamlit.session_state["ollama_model"] == "phi3:mini"

    settings._store_models([], "fallback")
    assert mock_streamlit.session_state[settings.OLLAMA_MODELS_KEY] == ["fallback"]


def test_render_status_panels_show_connected_and_empty_states(
    mock_streamlit: Any,
    translated_settings: None,
) -> None:
    """Status panels should cover connected, failed, and not-tested states."""
    mock_streamlit.session_state[settings.TESSERACT_STATUS_KEY] = {
        "ok": True,
        "version": "5.0.0",
    }
    mock_streamlit.session_state[settings.OLLAMA_STATUS_KEY] = {
        "ok": False,
        "message": "offline",
        "version": "0.1.0",
        "models": ["phi3"],
    }

    settings._render_status_panels()

    mock_streamlit.success.assert_called_once()
    mock_streamlit.error.assert_called_once()
    assert mock_streamlit.caption.call_count >= 3

    mock_streamlit.success.reset_mock()
    mock_streamlit.error.reset_mock()
    mock_streamlit.info.reset_mock()
    mock_streamlit.session_state[settings.TESSERACT_STATUS_KEY] = {}
    mock_streamlit.session_state[settings.OLLAMA_STATUS_KEY] = {}
    settings._render_status_panels()
    assert mock_streamlit.info.call_count == 2


def test_save_settings_updates_config_and_persists(
    mock_streamlit: Any,
    mock_config: AppConfig,
    translated_settings: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Saving settings should persist the new config and sync session config."""
    saved: list[AppConfig] = []
    monkeypatch.setattr(settings, "load_config", lambda: mock_config)
    monkeypatch.setattr(settings, "save_config", lambda cfg: saved.append(cfg))
    mock_streamlit.session_state.update(
        {
            "database_url": "sqlite:///custom.db",
            "ollama_base_url": "http://custom",
            "ollama_model": "llama3",
            "context_length": 2048,
            "temperature": 0.5,
            "tesseract_enabled": True,
            "tesseract_path": "/custom/tesseract",
            "config": {},
        }
    )

    settings._save_settings()

    assert saved
    assert saved[0].database_url == "sqlite:///custom.db"
    assert mock_streamlit.session_state["config"]["ollama_model"] == "llama3"
    mock_streamlit.success.assert_called_with("settings.success_saved")


def test_reset_settings_restores_defaults_and_reruns(
    mock_streamlit: Any,
    mock_config: AppConfig,
    translated_settings: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resetting settings should restore defaults, clear statuses, and rerun."""
    mock_streamlit.session_state["config"] = {}
    monkeypatch.setattr(settings, "reset_config", lambda: mock_config)

    settings._reset_settings()

    assert mock_streamlit.session_state["ollama_model"] == mock_config.ollama_model
    assert mock_streamlit.session_state[settings.TESSERACT_STATUS_KEY] == {}
    assert mock_streamlit.session_state[settings.OLLAMA_STATUS_KEY] == {}
    mock_streamlit.rerun.assert_called_once()


def test_render_settings_executes_button_branches(
    mock_streamlit: Any,
    translated_settings: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The page renderer should cover detect, refresh, test, save, and reset."""
    monkeypatch.setattr(settings, "render_page_header", lambda *args: None)
    monkeypatch.setattr(settings, "_render_status_panels", lambda: None)
    monkeypatch.setattr(
        settings, "get_default_tesseract_path", lambda: "/usr/bin/tesseract"
    )
    monkeypatch.setattr(settings, "get_ollama_models", lambda url: ["phi3:mini"])
    monkeypatch.setattr(
        settings, "detect_tesseract_path", lambda: "/detected/tesseract"
    )
    monkeypatch.setattr(settings, "detect_ollama_host", lambda host: "http://detected")
    monkeypatch.setattr(
        settings,
        "test_tesseract_connection",
        lambda path: {"ok": True, "version": "5.0.0"},
    )
    monkeypatch.setattr(
        settings,
        "test_ollama_connection",
        lambda host, model: {"ok": True, "version": "0.1.0", "models": ["llama3"]},
    )
    saved: list[str] = []
    reset: list[str] = []
    monkeypatch.setattr(settings, "_save_settings", lambda: saved.append("saved"))
    monkeypatch.setattr(settings, "_reset_settings", lambda: reset.append("reset"))

    button_values = iter([False, True, True, True, True, True, True, True])
    mock_streamlit.button.side_effect = lambda *args, **kwargs: next(button_values)
    mock_streamlit.session_state["config"] = {}

    settings.render_settings({"ollama_model": "phi3:mini"})

    assert mock_streamlit.session_state["tesseract_path"] == "/detected/tesseract"
    assert mock_streamlit.session_state["ollama_base_url"] == "http://detected"
    assert mock_streamlit.session_state["ollama_model"] == "llama3"
    assert saved == ["saved"]
    assert reset == ["reset"]


def test_render_settings_handles_missing_detection_results(
    mock_streamlit: Any,
    translated_settings: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The page renderer should warn or error when detection finds nothing."""
    monkeypatch.setattr(settings, "render_page_header", lambda *args: None)
    monkeypatch.setattr(settings, "_render_status_panels", lambda: None)
    monkeypatch.setattr(
        settings, "get_default_tesseract_path", lambda: "/usr/bin/tesseract"
    )
    monkeypatch.setattr(settings, "get_ollama_models", lambda url: [])
    monkeypatch.setattr(settings, "detect_tesseract_path", lambda: "")
    monkeypatch.setattr(settings, "detect_ollama_host", lambda host: "")

    button_values = iter([False, True, False, True, False, False, False, False])
    mock_streamlit.button.side_effect = lambda *args, **kwargs: next(button_values)
    mock_streamlit.session_state["config"] = {}

    settings.render_settings({"ollama_model": "phi3:mini"})

    mock_streamlit.warning.assert_called_with("settings.warning_tesseract_not_found")
    mock_streamlit.error.assert_called_with("settings.error_ollama_not_found")
