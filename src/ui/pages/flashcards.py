# SPDX-License-Identifier: AGPL-3.0-only
"""Flashcard review page generated from saved local note metadata with multilingual support."""

from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st

from src.storage.database import get_all_documents
from src.ui.components.page_header import render_page_header
from src.utils.translations import t


def _build_flashcards(notes: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Build flashcards from saved notes."""
    cards: list[dict[str, str]] = []
    for note in notes:
        title = note.get("title") or note.get("filename", t("note_card.label_untitled_note"))
        summary = note.get("summary", "")
        points = note.get("important_points", [])
        questions = note.get("possible_exam_questions", [])

        for question in questions:
            answer_parts = []
            if summary:
                answer_parts.append(summary)
            if points:
                answer_parts.append(
                    t("flashcards.default_question", title=str(title))
                    + " "
                                    + "; ".join(str(p) for p in points[:3])
                )
            cards.append(
                {
                    "source": str(title),
                    "front": str(question.get("text", str(question)) if isinstance(question, dict) else str(question)),
                    "back": (
                        " ".join(answer_parts) or t("flashcards.default_answer")
                    ),
                }
            )

        if points and not questions:
            for point in points:
                cards.append(
                    {
                        "source": str(title),
                        "front": t("flashcards.default_question", title=str(title)),
                        "back": str(point),
                    }
                )
    return cards


def render_flashcards(_: dict[str, Any]) -> None:
    """Render generated flashcards from existing offline notes."""
    render_page_header(
        t("flashcards.page_title"),
        t("flashcards.page_description"),
        t("flashcards.page_eyebrow"),
    )

    notes = get_all_documents()
    cards = _build_flashcards(notes)
    if not cards:
        st.info(t("flashcards.info_empty"))
        return

    if "flashcard_index" not in st.session_state:
        st.session_state.flashcard_index = 0
    if "flashcard_show_answer" not in st.session_state:
        st.session_state.flashcard_show_answer = False

    index = int(st.session_state.flashcard_index) % len(cards)
    card = cards[index]

    st.caption(
        t("flashcards.card_count", current=index + 1, total=len(cards), source=card["source"])
    )
    st.markdown(
        f"""
        <section class="upload-preview">
            <div class="section-label">{t('flashcards.label_question')}</div>
            <p class="page-title" style="font-size: 1.2rem;">{escape(card["front"])}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.flashcard_show_answer:
        st.markdown(
            f"""
            <section class="upload-preview">
                <div class="section-label">{t('flashcards.label_answer')}</div>
                <p class="note-summary">{escape(card["back"])}</p>
            </section>
            """,
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(t("flashcards.button_previous"), use_container_width=True):
            st.session_state.flashcard_index = (index - 1) % len(cards)
            st.session_state.flashcard_show_answer = False
            st.rerun()
    with col2:
        label = (
            t("flashcards.button_hide_answer")
            if st.session_state.flashcard_show_answer
            else t("flashcards.button_show_answer")
        )
        if st.button(label, use_container_width=True, type="primary"):
            st.session_state.flashcard_show_answer = (
                not st.session_state.flashcard_show_answer
            )
            st.rerun()
    with col3:
        if st.button(t("flashcards.button_next"), use_container_width=True):
            st.session_state.flashcard_index = (index + 1) % len(cards)
            st.session_state.flashcard_show_answer = False
            st.rerun()