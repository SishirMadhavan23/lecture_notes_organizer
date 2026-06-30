# SPDX-License-Identifier: AGPL-3.0-only
"""Reusable page header component with multilingual support."""

from __future__ import annotations

import streamlit as st


def render_page_header(title: str, description: str, eyebrow: str) -> None:
    """Render a consistent academic page header.

    Args:
        title: Page title (already translated)
        description: Page description (already translated)
        eyebrow: Section/category label (already translated)
    """
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
