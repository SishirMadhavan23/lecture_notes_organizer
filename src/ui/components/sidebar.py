# SPDX-License-Identifier: AGPL-3.0-only
"""Sidebar navigation component with multilingual support."""

from __future__ import annotations

import streamlit as st

from src.utils.translations import render_language_selector, t


def render_sidebar() -> None:
    """Render the sidebar navigation with language selector."""
    with st.sidebar:
        st.markdown(
            f"""
            <section class="sidebar-brand">
                <p class="sidebar-title">{t("app.title")}</p>
                <p class="sidebar-subtitle">{t("app.subtitle")}</p>
            </section>
            """,
            unsafe_allow_html=True,
        )

        pages = [
            ("Upload", "\u21e7", "sidebar.nav.upload"),
            ("View Notes", "\u25a4", "sidebar.nav.view_notes"),
            ("Flashcards", "\u25c7", "sidebar.nav.flashcards"),
            ("Search", "\u2315", "sidebar.nav.search"),
            ("Settings", "\u2699", "sidebar.nav.settings"),
            ("System Status", "\u25c8", "sidebar.nav.system_status"),
        ]
        current_page = st.session_state.get("current_page", "Upload")
        st.markdown(
            f'<p class="sidebar-nav-label">{t("sidebar.workspace")}</p>',
            unsafe_allow_html=True,
        )
        for page, icon, key in pages:
            if st.button(
                f"{icon}  {t(key)}",
                key=f"nav_{page.lower().replace(' ', '_')}",
                type="primary" if page == current_page else "secondary",
                use_container_width=True,
            ):
                st.session_state.current_page = page
                st.query_params.clear()
                st.rerun()

        st.markdown("---")
        render_language_selector()

        st.markdown(
            f"""
            <p class="sidebar-footer">
                {t("sidebar.footer").replace(chr(10), "<br>")}
            </p>
            """,
            unsafe_allow_html=True,
        )
