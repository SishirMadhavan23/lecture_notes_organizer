# SPDX-License-Identifier: GPL-3.0-or-later
"""Sidebar navigation component."""

import streamlit as st


def render_sidebar() -> None:
    """Render the sidebar navigation."""
    with st.sidebar:
        st.title("🎓 Notes Organizer")
        st.markdown("---")

        pages = {
            "Upload": "📤",
            "View Notes": "📚",
            "Search": "🔍",
            "Settings": "⚙️",
            "System Status": "📊",
        }

        for page_name, icon in pages.items():
            if st.sidebar.button(
                f"{icon} {page_name}",
                use_container_width=True,
                key=f"nav_{page_name}",
            ):
                st.session_state.current_page = page_name

        st.markdown("---")
        st.caption("CPU-First Hackathon 2026")
