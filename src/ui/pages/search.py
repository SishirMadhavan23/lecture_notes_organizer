# SPDX-License-Identifier: GPL-3.0-or-later
"""Search page for Streamlit UI with FTS5 full-text search."""

from typing import Any, Dict

import streamlit as st

from src.storage.database import search_notes
from src.ui.components.page_header import render_page_header
from src.ui.components.note_card import render_note_card


def render_search(config: Dict[str, Any]) -> None:
    """Render the search page."""
    render_page_header(
        "Search Organized Notes",
        (
            "Search across titles, subjects, summaries, topics, and extracted "
            "content to quickly recover relevant study material."
        ),
        "Research Retrieval",
    )

    query = st.text_input(
        "Search query",
        placeholder="e.g., machine learning, calculus, biology...",
        help="Searches titles, subjects, topics, keywords, and content",
    )

    if query:
        results = search_notes(query)

        if not results:
            st.info("No results found. Try a different search term.")
            return

        st.caption(f"Found {len(results)} result(s) for '{query}'")

        for note in results:
            render_note_card(note, expanded=True)
    else:
        st.info("Enter a search query above to explore your organized notes.")
