# SPDX-License-Identifier: GPL-3.0-or-later
"""Note card display component."""

from typing import Any, Dict

import streamlit as st


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
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"### {title}")
        with col2:
            if difficulty:
                color = {"Beginner": "green", "Intermediate": "orange",
                         "Advanced": "red"}.get(difficulty, "gray")
                st.markdown(f":{color}[**{difficulty}**]")
        with col3:
            if subject:
                st.markdown(f"*{subject}*")

        if summary:
            st.markdown(summary[:300] + ("..." if len(summary) > 300 else ""))

        with st.expander("📋 Details", expanded=expanded):
            if topics:
                st.markdown("**Topics:** " + ", ".join(f"`{t}`" for t in topics))
            if keywords:
                st.markdown("**Keywords:** " + ", ".join(f"`{k}`" for k in keywords))
            if points:
                st.markdown("**Key Points:**")
                for pt in points:
                    st.markdown(f"- {pt}")
            if questions:
                st.markdown("**Possible Exam Questions:**")
                for q in questions:
                    st.markdown(f"- ❓ {q}")

            st.caption(f"Processed: {note.get('created_at', 'N/A')}")
            st.caption(f"File: {note.get('filename', 'N/A')} ({note.get('file_type', 'N/A')})")
