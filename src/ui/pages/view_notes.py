# SPDX-License-Identifier: GPL-3.0-or-later
"""View organized notes page."""

from typing import Any, Dict

import streamlit as st

from src.storage.database import get_all_documents, delete_document
from src.ui.components.note_card import render_note_card


def render_view_notes(config: Dict[str, Any]) -> None:
    """Render the view organized notes page."""
    st.header("📚 Organized Notes")
    st.markdown("Browse all processed lecture notes.")

    notes = get_all_documents()

    if not notes:
        st.info("No notes yet. Upload some lecture notes to get started!")
        return

    st.caption(f"Total: {len(notes)} note(s)")

    for note in notes:
        col1, col2 = st.columns([5, 1])
        with col2:
            doc_id = note.get("id")
            if doc_id and st.button("🗑️", key=f"del_{doc_id}"):
                if delete_document(doc_id):
                    st.rerun()
        with col1:
            render_note_card(note, expanded=False)
