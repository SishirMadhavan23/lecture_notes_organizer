"""Reusable page header component."""

from __future__ import annotations

import streamlit as st


def render_page_header(title: str, description: str, eyebrow: str) -> None:
    """Render a consistent academic page header."""
    st.markdown(
        f"""
        <section class="page-shell">
            <p class="page-eyebrow">{eyebrow}</p>
            <h1 class="page-title">{title}</h1>
            <p class="page-description">{description}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
