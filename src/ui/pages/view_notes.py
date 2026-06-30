# SPDX-License-Identifier: GPL-3.0-or-later
"""View organized notes page."""

from typing import Any

import streamlit as st

from src.storage.database import delete_document, get_all_documents
from src.ui.components.note_card import render_note_card
from src.ui.components.page_header import render_page_header


def render_view_notes(config: dict[str, Any]) -> None:
    """Render the view organized notes page."""
    render_page_header(
        "Organized Notes Archive",
        (
            "Browse processed lecture materials, review extracted summaries, and "
            "manage your local note collection."
        ),
        "Archive",
    )

    notes = get_all_documents()

    if not notes:
        st.info("No notes yet. Upload some lecture notes to get started!")
        return

    st.caption(f"Total: {len(notes)} note(s)")

    for note in notes:
        col1, col2 = st.columns([5, 1])
        with col2:
            doc_id = note.get("id")
            if doc_id and st.button("Remove", key=f"del_{doc_id}"):
                if delete_document(doc_id):
                    st.rerun()
        with col1:
            render_note_card(note, expanded=False)
