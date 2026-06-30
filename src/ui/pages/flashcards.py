# SPDX-License-Identifier: GPL-3.0-or-later
"""Flashcard review page generated from saved local note metadata."""

from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st

from src.storage.database import get_all_documents
from src.ui.components.page_header import render_page_header


def _build_flashcards(notes: list[dict[str, Any]]) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    for note in notes:
        title = note.get("title") or note.get("filename", "Untitled note")
        summary = note.get("summary", "")
        points = note.get("important_points", [])
        questions = note.get("possible_exam_questions", [])

        for question in questions:
            answer_parts = []
            if summary:
                answer_parts.append(summary)
            if points:
                answer_parts.append(
                    "Key points: " + "; ".join(str(p) for p in points[:3])
                )
            cards.append(
                {
                    "source": str(title),
                    "front": str(question),
                    "back": (
                        " ".join(answer_parts) or "Review the source note for details."
                    ),
                }
            )

        if points and not questions:
            for point in points:
                cards.append(
                    {
                        "source": str(title),
                        "front": f"What should you remember from {title}?",
                        "back": str(point),
                    }
                )
    return cards


def render_flashcards(_: dict[str, Any]) -> None:
    """Render generated flashcards from existing offline notes."""
    render_page_header(
        "Flashcards",
        "Review locally generated exam questions and key points from saved notes.",
        "Study Mode",
    )

    notes = get_all_documents()
    cards = _build_flashcards(notes)
    if not cards:
        st.info("Upload and process lecture notes to generate flashcards.")
        return

    if "flashcard_index" not in st.session_state:
        st.session_state.flashcard_index = 0
    if "flashcard_show_answer" not in st.session_state:
        st.session_state.flashcard_show_answer = False

    index = int(st.session_state.flashcard_index) % len(cards)
    card = cards[index]

    st.caption(f"Card {index + 1} of {len(cards)} - {card['source']}")
    st.markdown(
        f"""
        <section class="upload-preview">
            <div class="section-label">Question</div>
            <p class="page-title" style="font-size: 1.2rem;">{escape(card["front"])}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.flashcard_show_answer:
        st.markdown(
            f"""
            <section class="upload-preview">
                <div class="section-label">Answer</div>
                <p class="note-summary">{escape(card["back"])}</p>
            </section>
            """,
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Previous", use_container_width=True):
            st.session_state.flashcard_index = (index - 1) % len(cards)
            st.session_state.flashcard_show_answer = False
            st.rerun()
    with col2:
        if st.button(
            "Hide Answer" if st.session_state.flashcard_show_answer else "Show Answer",
            use_container_width=True,
            type="primary",
        ):
            st.session_state.flashcard_show_answer = (
                not st.session_state.flashcard_show_answer
            )
            st.rerun()
    with col3:
        if st.button("Next", use_container_width=True):
            st.session_state.flashcard_index = (index + 1) % len(cards)
            st.session_state.flashcard_show_answer = False
            st.rerun()
