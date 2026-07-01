"""Tests for shared UI components and smaller page modules."""

from __future__ import annotations

from typing import Any

import pytest

from src.ui import theme
from src.ui.components import dashboard, page_header, sidebar
from src.ui.pages import flashcards, search, system_status, view_notes


def test_theme_css_and_application(mock_streamlit: Any) -> None:
    """Theme helpers should expose CSS and inject it into Streamlit."""
    css = theme.get_theme_css()
    assert "--lno-primary" in css
    assert "IBM Plex Sans" in css

    theme.apply_theme()
    mock_streamlit.markdown.assert_called_with(css, unsafe_allow_html=True)


def test_dashboard_components_render_expected_markup(mock_streamlit: Any) -> None:
    """Dashboard helpers should render status cards, stats, steppers, and footer."""
    dashboard.render_status_card(
        "Ollama", "Running", "Ready", "invalid", "AI", "System Status"
    )
    dashboard.render_stat_cards([{"label": "Docs", "value": "5", "hint": "Stored"}])
    dashboard.render_processing_stepper(active_step=2, failed=False)
    dashboard.render_processing_stepper(active_step=3, failed=True)
    dashboard.render_footer()

    rendered = "\n".join(
        call.args[0] for call in mock_streamlit.markdown.call_args_list
    )
    assert "?page=System%20Status" in rendered
    assert "status-card--warning" in rendered
    assert "process-step--active" in rendered
    assert "process-step--error" in rendered
    assert "Offline Mode" in rendered


def test_page_header_renders_html(mock_streamlit: Any) -> None:
    """The page header should render the expected shell markup."""
    page_header.render_page_header("Title", "Description", "Eyebrow")
    html = mock_streamlit.markdown.call_args.args[0]
    assert "Title" in html
    assert "Description" in html
    assert "Eyebrow" in html


def test_sidebar_renders_navigation_and_handles_click(
    mock_streamlit: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sidebar navigation should update current page and rerun when clicked."""
    monkeypatch.setattr(sidebar, "t", lambda key: key)
    language_calls: list[str] = []
    monkeypatch.setattr(
        sidebar, "render_language_selector", lambda: language_calls.append("language")
    )
    mock_streamlit.session_state["current_page"] = "Upload"

    button_values = iter([False, True, False, False, False, False])
    mock_streamlit.button.side_effect = lambda *args, **kwargs: next(button_values)
    sidebar.render_sidebar()

    assert mock_streamlit.session_state.current_page == "View Notes"
    assert language_calls == ["language"]
    assert mock_streamlit.query_params == {}
    mock_streamlit.rerun.assert_called_once()


def test_search_page_handles_empty_results_and_matches(
    mock_streamlit: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Search should cover empty query, no results, and result rendering."""
    monkeypatch.setattr(search, "render_page_header", lambda *args: None)
    rendered: list[dict[str, Any]] = []
    monkeypatch.setattr(
        search, "render_note_card", lambda note, expanded: rendered.append(note)
    )

    mock_streamlit.text_input.return_value = ""
    search.render_search({})
    mock_streamlit.info.assert_called_with(
        "Enter a search query above to explore your organized notes."
    )

    mock_streamlit.info.reset_mock()
    mock_streamlit.text_input.return_value = "ml"
    monkeypatch.setattr(search, "search_notes", lambda query: [])
    search.render_search({})
    mock_streamlit.info.assert_called_with(
        "No results found. Try a different search term."
    )

    mock_streamlit.info.reset_mock()
    monkeypatch.setattr(search, "search_notes", lambda query: [{"id": 1}, {"id": 2}])
    search.render_search({})
    assert len(rendered) == 2


def test_system_status_renders_stats_and_database_warning(
    mock_streamlit: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """System status should render healthy state and stats failure fallback."""
    monkeypatch.setattr(system_status, "render_page_header", lambda *args: None)
    status_cards: list[tuple[str, str]] = []
    stat_cards: list[Any] = []
    monkeypatch.setattr(
        system_status,
        "render_status_card",
        lambda title, status, detail, level, icon, destination="Settings": (
            status_cards.append((title, status))
        ),
    )
    monkeypatch.setattr(
        system_status, "render_stat_cards", lambda stats: stat_cards.append(list(stats))
    )
    monkeypatch.setattr(system_status, "is_ollama_available", lambda url: True)
    monkeypatch.setattr(system_status, "is_tesseract_available", lambda path: False)
    monkeypatch.setattr(system_status, "get_stats", lambda: {"processed": 5})
    mock_streamlit.session_state["processing_durations"] = [2.0, 4.0]
    mock_streamlit.session_state["pages_processed"] = 9

    system_status.render_system_status(
        {"ollama_model": "phi3", "tesseract_path": "/bin/tesseract"}
    )

    assert status_cards == [
        ("Ollama", "Running"),
        ("Tesseract OCR", "Not installed"),
        ("SQLite", "Ready"),
    ]
    assert stat_cards and stat_cards[0][0]["value"] == "5"

    monkeypatch.setattr(
        system_status,
        "get_stats",
        lambda: (_ for _ in ()).throw(RuntimeError("db unavailable")),
    )
    system_status.render_system_status({})
    mock_streamlit.warning.assert_called_with(
        "Could not read database stats: db unavailable"
    )


def test_view_notes_page_handles_empty_notes_and_deletion(
    mock_streamlit: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """View-notes should cover empty state, rendering, and delete callbacks."""
    monkeypatch.setattr(view_notes, "render_page_header", lambda *args: None)
    monkeypatch.setattr(view_notes, "get_all_documents", lambda: [])
    view_notes.render_view_notes({})
    mock_streamlit.info.assert_called_with(
        "No notes yet. Upload some lecture notes to get started!"
    )

    rendered: list[dict[str, Any]] = []
    monkeypatch.setattr(
        view_notes,
        "get_all_documents",
        lambda: [{"id": 1, "filename": "a.pdf"}, {"id": 2, "filename": "b.pdf"}],
    )
    monkeypatch.setattr(
        view_notes, "render_note_card", lambda note, expanded: rendered.append(note)
    )
    monkeypatch.setattr(view_notes, "delete_document", lambda doc_id: doc_id == 1)
    button_values = iter([True, False])
    mock_streamlit.button.side_effect = lambda *args, **kwargs: next(button_values)

    view_notes.render_view_notes({})

    assert len(rendered) == 2
    mock_streamlit.rerun.assert_called_once()


def test_flashcard_builder_and_page_navigation(
    mock_streamlit: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Flashcards should build from notes and handle navigation state changes."""
    monkeypatch.setattr(
        flashcards, "t", lambda key, **kwargs: f"{key}:{kwargs}" if kwargs else key
    )
    notes = [
        {
            "title": "ML",
            "summary": "Summary",
            "important_points": ["Point 1", "Point 2"],
            "possible_exam_questions": [{"text": "What is ML?"}],
        },
        {
            "filename": "fallback.txt",
            "important_points": ["Only point"],
            "possible_exam_questions": [],
        },
    ]
    cards = flashcards._build_flashcards(notes)
    assert len(cards) == 2
    assert cards[0]["front"] == "What is ML?"
    assert cards[1]["source"] == "fallback.txt"

    monkeypatch.setattr(flashcards, "render_page_header", lambda *args: None)
    monkeypatch.setattr(flashcards, "get_all_documents", lambda: [])
    flashcards.render_flashcards({})
    mock_streamlit.info.assert_called_with("flashcards.info_empty")

    mock_streamlit.info.reset_mock()
    monkeypatch.setattr(flashcards, "get_all_documents", lambda: notes)

    button_values = iter([True, True, True])
    mock_streamlit.button.side_effect = lambda *args, **kwargs: next(button_values)
    flashcards.render_flashcards({})

    assert mock_streamlit.session_state.flashcard_index == 1
    assert mock_streamlit.session_state.flashcard_show_answer is False
    assert mock_streamlit.rerun.call_count >= 1
