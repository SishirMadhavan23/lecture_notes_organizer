# SPDX-License-Identifier: GPL-3.0-or-later
"""Note card display component."""

from html import escape
from typing import Any, Dict

import streamlit as st


def _difficulty_tone(difficulty: str) -> str:
    tones = {
        "Beginner": "meta-pill",
        "Intermediate": "meta-pill meta-pill--accent",
        "Advanced": "meta-pill",
    }
    return tones.get(difficulty, "meta-pill")


def render_note_card(note: Dict[str, Any], expanded: bool = False) -> None:
    """Render a single note card with expandable details.

    Args:
        note: Note dictionary with metadata fields
        expanded: Whether to show the card expanded by default
    """
    title = note.get("title") or note.get("filename", "Untitled")
    subject = note.get("subject", "")
    difficulty = note.get("difficulty", "")
    summary = note.get("summary", "")
    topics = note.get("topics", [])
    keywords = note.get("keywords", [])
    questions = note.get("possible_exam_questions", [])
    points = note.get("important_points", [])

    with st.container(border=True):
        meta_items = []
        if subject:
            meta_items.append(f'<span class="meta-pill">{escape(subject)}</span>')
        if difficulty:
            meta_items.append(
                f'<span class="{_difficulty_tone(difficulty)}">{escape(difficulty)}</span>'
            )
        meta_items.append(
            f'<span class="meta-pill">{escape(note.get("file_type", "N/A").upper())}</span>'
        )

        summary_text = summary[:300] + ("..." if len(summary) > 300 else "")
        topic_markup = "".join(
            f'<span class="topic-badge">{escape(str(topic))}</span>'
            for topic in topics[:6]
        )
        keyword_markup = "".join(
            f'<span class="keyword-badge">{escape(str(keyword))}</span>'
            for keyword in keywords[:8]
        )

        st.markdown(
            f"""
            <h3 class="page-title" style="font-size: 1.25rem; margin-bottom: 0.2rem;">
                {escape(title)}
            </h3>
            <div class="meta-row">{''.join(meta_items)}</div>
            <p class="note-summary">{escape(summary_text) if summary_text else "No summary available yet."}</p>
            """,
            unsafe_allow_html=True,
        )

        if topic_markup:
            st.markdown(
                f'<div class="section-label">Topics</div><div class="badge-row">{topic_markup}</div>',
                unsafe_allow_html=True,
            )
        if keyword_markup:
            st.markdown(
                f'<div class="section-label">Keywords</div><div class="badge-row">{keyword_markup}</div>',
                unsafe_allow_html=True,
            )

        with st.expander("Document details", expanded=expanded):
            if topics:
                st.markdown("**Topics:** " + ", ".join(f"`{t}`" for t in topics))
            if keywords:
                st.markdown("**Keywords:** " + ", ".join(f"`{k}`" for k in keywords))
            if points:
                st.markdown("**Key points:**")
                for pt in points:
                    st.markdown(f"- {pt}")
            if questions:
                st.markdown("**Possible exam questions:**")
                for q in questions:
                    st.markdown(f"- {q}")

            st.caption(f"Processed: {note.get('created_at', 'N/A')}")
            st.caption(
                f"File: {note.get('filename', 'N/A')} ({note.get('file_type', 'N/A')})"
            )
