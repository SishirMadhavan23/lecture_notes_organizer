# SPDX-License-Identifier: AGPL-3.0-only
"""Multilingual translation system for the Lecture Notes Organizer.

Provides a dictionary-based translation helper with support for English,
Telugu, and Hindi. Language preference persists via Streamlit session state.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import streamlit as st

logger = logging.getLogger(__name__)

# Supported languages with their display names and locale codes
LANGUAGES: dict[str, dict[str, str]] = {
    "en": {"name": "English", "native_name": "English"},
    "te": {"name": "Telugu", "native_name": "తెలుగు"},
    "hi": {"name": "Hindi", "native_name": "हिन्दी"},
}

DEFAULT_LANGUAGE = "en"

_translations: dict[str, dict[str, str]] = {}


def _load_translation_file(lang: str) -> dict[str, str]:
    """Load a single translation JSON file from the translations directory."""
    path = (
        Path(__file__).resolve().parent.parent.parent / "translations" / f"{lang}.json"
    )
    if not path.exists():
        logger.warning("Translation file not found: %s", path)
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to load translation %s: %s", path, exc)
        return {}


def _load_all_translations() -> dict[str, dict[str, str]]:
    """Pre-load all translation files on first access."""
    if not _translations:
        for lang in LANGUAGES:
            _translations[lang] = _load_translation_file(lang)
    return _translations


def get_language() -> str:
    """Return the currently selected language code from session state."""
    _load_all_translations()
    lang = st.session_state.get("language", DEFAULT_LANGUAGE)
    if lang not in LANGUAGES:
        lang = DEFAULT_LANGUAGE
    return lang


def set_language(lang: str) -> None:
    """Set the active language in session state."""
    if lang in LANGUAGES:
        st.session_state["language"] = lang
    else:
        st.session_state["language"] = DEFAULT_LANGUAGE


def t(key: str, default: str | None = None, **kwargs: Any) -> str:
    """Translate a key into the currently selected language.

    Args:
        key: The translation key (dot-notation supported, e.g. 'nav.upload')
        default: Fallback text if key is not found
        kwargs: Optional placeholder values for string interpolation

    Returns:
        The translated string or the default/fallback key
    """
    lang = get_language()
    translations = _load_all_translations()
    lang_dict = translations.get(lang, {})

    # Support dot-notation for nested keys
    value: Any = lang_dict
    for part in key.split("."):
        if isinstance(value, dict):
            value = value.get(part)
        else:
            value = None
            break

    if value is not None and isinstance(value, str):
        if kwargs:
            try:
                return value.format(**kwargs)
            except (KeyError, IndexError, ValueError):
                return value
        return value

    # Fallback to English
    if lang != DEFAULT_LANGUAGE:
        en_dict = translations.get(DEFAULT_LANGUAGE, {})
        value = en_dict
        for part in key.split("."):
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break
        if value is not None and isinstance(value, str):
            if kwargs:
                try:
                    return value.format(**kwargs)
                except (KeyError, IndexError, ValueError):
                    return value
            return value

    return default or key


def has_translation(key: str) -> bool:
    """Check if a translation key exists for the current language."""
    lang = get_language()
    translations = _load_all_translations()
    lang_dict = translations.get(lang, {})

    value: Any = lang_dict
    for part in key.split("."):
        if isinstance(value, dict):
            value = value.get(part)
        else:
            return False

    return value is not None and isinstance(value, str)


def render_language_selector() -> None:
    """Render a language selector dropdown in the sidebar."""
    current = get_language()
    options = {
        code: f"{info['native_name']} ({info['name']})"
        for code, info in LANGUAGES.items()
    }

    selected = st.selectbox(
        label=t("sidebar.language", "Language"),
        options=list(options.keys()),
        format_func=lambda code: options.get(code, code),
        index=list(options.keys()).index(current) if current in options else 0,
        key="language_selector",
    )

    if selected != current:
        set_language(selected)
        st.rerun()
