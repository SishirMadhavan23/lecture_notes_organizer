# SPDX-License-Identifier: GPL-3.0-or-later
"""Sidebar navigation component."""

import streamlit as st


def render_sidebar() -> None:
    """Render the sidebar navigation."""
    with st.sidebar:
        st.markdown(
            """
            <section class="sidebar-brand">
                <p class="sidebar-title">Lecture Notes Organizer</p>
                <p class="sidebar-subtitle">
                    Offline note processing and research-ready study retrieval.
                </p>
            </section>
            """,
            unsafe_allow_html=True,
        )

        pages = [
            ("Upload", "\u21e7"),
            ("View Notes", "\u25a4"),
            ("Search", "\u2315"),
            ("Settings", "\u2699"),
            ("System Status", "\u25c8"),
        ]
        current_page = st.session_state.get("current_page", "Upload")
        st.markdown('<p class="sidebar-nav-label">Workspace</p>', unsafe_allow_html=True)
        for page, icon in pages:
            if st.button(
                f"{icon}  {page}",
                key=f"nav_{page.lower().replace(' ', '_')}",
                type="primary" if page == current_page else "secondary",
                use_container_width=True,
            ):
                st.session_state.current_page = page
                st.query_params.clear()
                st.rerun()

        st.markdown(
            """
            <p class="sidebar-footer">
                CPU-first workflow<br>
                Academic dark theme<br>
                Local processing only
            </p>
            """,
            unsafe_allow_html=True,
        )
