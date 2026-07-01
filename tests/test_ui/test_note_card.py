"""Tests for the note card UI component."""

from __future__ import annotations

from typing import Any

import pytest

from src.ui.components import note_card


@pytest.fixture
def sample_note() -> dict[str, Any]:
    """Return a representative note payload."""
    return {
        "id": 7,
        "filename": "lecture.pptx",
        "file_type": "pptx",
        "file_size": 4096,
        "created_at": "2026-07-01T10:30:00",
        "title": "Intro to ML",
        "subject": "AI",
        "difficulty": "Intermediate",
        "summary": "A" * 320,
        "topics": ["Models", "Training"],
        "keywords": ["ml", "ai"],
        "important_points": ["Point 1", "Point 2"],
        "possible_exam_questions": [
            "What is a model?",
            {"type": "flashcard", "front": "Q1", "back": "A1"},
        ],
        "raw_text": (
            "Presentation Metadata\n"
            "Title: Intro Deck\n"
            "Author: Ada\n"
            "Created: 2026-07-01\n"
            "Slides: 2\n\n"
            "Slide 1\nOverview\nSpeaker Notes: hello\n\n"
            "Slide 2\nDetails"
        ),
    }


def test_difficulty_tone_and_file_size_helpers() -> None:
    """Helper functions should map values to stable UI tokens."""
    assert note_card._difficulty_tone("Intermediate") == "meta-pill meta-pill--accent"
    assert note_card._difficulty_tone("Unknown") == "meta-pill"
    assert note_card._format_file_size(512) == "512 B"
    assert note_card._format_file_size(2048) == "2.0 KB"
    assert note_card._format_file_size(3 * 1024 * 1024) == "3.00 MB"


def test_is_presentation_and_study_item_normalization() -> None:
    """Presentation detection and study-item normalization should split content."""
    assert note_card._is_presentation({"file_type": "PPT"}) is True
    assert note_card._is_presentation({"file_type": "pdf"}) is False

    questions, flashcards = note_card._normalize_study_items(
        [
            "Explain supervised learning",
            {"text": "Define overfitting"},
            {"type": "flashcard", "front": "Front", "back": "Back"},
            {"type": "flashcard", "front": "", "back": ""},
            "",
        ]
    )

    assert questions == ["Explain supervised learning", "Define overfitting"]
    assert flashcards == [{"front": "Front", "back": "Back"}]


def test_parse_presentation_details_with_and_without_metadata(
    sample_note: dict[str, Any],
) -> None:
    """Presentation parsing should support both metadata and plain text."""
    details = note_card._parse_presentation_details(sample_note["raw_text"])
    assert details["title"] == "Intro Deck"
    assert details["author"] == "Ada"
    assert details["slide_count"] == 2
    assert details["has_speaker_notes"] is True
    assert len(details["slides"]) == 2

    empty = note_card._parse_presentation_details("Plain content")
    assert empty["slides"] == []
    assert empty["slide_count"] == 0


def test_render_general_and_intermediate_tabs_show_empty_states(
    mock_streamlit: Any,
) -> None:
    """General and summary tabs should render fallback copy for missing metadata."""
    note_card._render_general_tab(
        {
            "filename": "note.txt",
            "file_type": "txt",
            "file_size": 12,
            "created_at": "today",
            "subject": "",
        }
    )
    note_card._render_intermediate_tab(
        {"summary": "", "topics": [], "keywords": [], "important_points": []}
    )

    assert mock_streamlit.markdown.call_count >= 5
    mock_streamlit.caption.assert_any_call("No topics available.")
    mock_streamlit.caption.assert_any_call("No keywords available.")
    mock_streamlit.caption.assert_any_call("No important points available.")


def test_render_presentation_metadata_tab_with_no_slide_data(
    mock_streamlit: Any,
) -> None:
    """Presentation metadata tab should surface empty-state copy when needed."""
    note_card._render_presentation_metadata_tab(
        {"title": "Fallback", "raw_text": "Presentation Metadata\nTitle: \nSlides: 0"}
    )

    mock_streamlit.caption.assert_called_with("No slide metadata available.")
    assert mock_streamlit.write.call_count >= 2


def test_render_content_tabs_for_presentation_and_empty_content(
    mock_streamlit: Any,
    sample_note: dict[str, Any],
) -> None:
    """Content tabs should render slide, flashcard, and question sections."""
    note_card._render_content_tabs(sample_note)

    labels = mock_streamlit.tabs.call_args.args[0]
    assert labels == [
        "Overview",
        "Summary",
        "Topics",
        "Slides",
        "Flashcards",
        "Questions",
    ]
    mock_streamlit.text.assert_called()

    mock_streamlit.caption.reset_mock()
    note_card._render_content_tabs(
        {
            "filename": "note.pdf",
            "file_type": "pdf",
            "summary": "",
            "topics": [],
            "keywords": [],
            "important_points": [],
            "possible_exam_questions": [],
            "raw_text": "",
        }
    )
    mock_streamlit.caption.assert_any_call("No topics available.")
    mock_streamlit.caption.assert_any_call("No keywords available.")
    mock_streamlit.caption.assert_any_call("No flashcards available.")
    mock_streamlit.caption.assert_any_call("No exam questions available.")


def test_render_note_card_for_presentation_and_standard_note(
    mock_streamlit: Any,
    sample_note: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The main note-card renderer should handle both PPT and non-PPT notes."""
    general = []
    intermediate = []
    presentation = []
    content = []
    monkeypatch.setattr(
        note_card, "_render_general_tab", lambda note: general.append(note["filename"])
    )
    monkeypatch.setattr(
        note_card,
        "_render_intermediate_tab",
        lambda note: intermediate.append(note["filename"]),
    )
    monkeypatch.setattr(
        note_card,
        "_render_presentation_metadata_tab",
        lambda note: presentation.append(note["filename"]),
    )
    monkeypatch.setattr(
        note_card, "_render_content_tabs", lambda note: content.append(note["filename"])
    )

    note_card.render_note_card(sample_note, expanded=True)
    note_card.render_note_card(
        {
            "filename": "summary.pdf",
            "file_type": "pdf",
            "summary": "",
            "topics": [],
            "keywords": [],
        }
    )

    assert general == ["lecture.pptx"]
    assert intermediate == ["lecture.pptx"]
    assert presentation == ["lecture.pptx"]
    assert content == ["lecture.pptx", "summary.pdf"]
    assert mock_streamlit.expander.call_args_list[0].args[0] == "Document details"
