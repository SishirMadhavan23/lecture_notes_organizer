"""Reusable dashboard presentation components."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from html import escape
from urllib.parse import quote

import streamlit as st


def render_status_card(
    title: str,
    status: str,
    detail: str,
    level: str,
    icon: str,
    destination: str = "Settings",
) -> None:
    """Render a clickable integration status card."""
    safe_level = level if level in {"success", "warning", "error"} else "warning"
    destination_url = f"?page={quote(destination)}"
    st.markdown(
        f"""
        <a class="status-card status-card--{safe_level}" href="{destination_url}"
           target="_self" aria-label="Configure {escape(title)}">
            <div class="status-card__top">
                <span class="status-card__icon" aria-hidden="true">{escape(icon)}</span>
                <span class="status-badge status-badge--{safe_level}">
                    {escape(status)}
                </span>
            </div>
            <div class="status-card__title">{escape(title)}</div>
            <div class="status-card__detail">{escape(detail)}</div>
            <div class="status-card__action">
                Open configuration <span aria-hidden="true">-&gt;</span>
            </div>
        </a>
        """,
        unsafe_allow_html=True,
    )


def render_stat_cards(stats: Iterable[Mapping[str, str]]) -> None:
    """Render a responsive row of processing statistics."""
    cards = "".join(f"""
        <article class="stat-card">
            <div class="stat-card__label">{escape(item["label"])}</div>
            <div class="stat-card__value">{escape(item["value"])}</div>
            <div class="stat-card__hint">{escape(item.get("hint", ""))}</div>
        </article>
        """ for item in stats)
    st.markdown(
        f'<section class="stats-grid">{cards}</section>', unsafe_allow_html=True
    )


def render_processing_stepper(active_step: int = 0, failed: bool = False) -> None:
    """Render the four-stage processing sequence."""
    steps = (
        ("OCR", "Extract"),
        ("Text Cleaning", "Refine"),
        ("AI Structuring", "Organize"),
        ("SQLite Storage", "Save"),
    )
    markup = []
    for index, (title, subtitle) in enumerate(steps, start=1):
        if failed and index == active_step:
            state = "error"
        elif index < active_step or active_step > len(steps):
            state = "complete"
        elif index == active_step:
            state = "active"
        else:
            state = "pending"
        marker = (
            "!" if state == "error" else ("OK" if state == "complete" else str(index))
        )
        markup.append(f"""
            <div class="process-step process-step--{state}">
                <span class="process-step__marker">{marker}</span>
                <span class="process-step__copy">
                    <strong>{escape(title)}</strong>
                    <small>{escape(subtitle)}</small>
                </span>
            </div>
            """)
    st.markdown(
        (
            f'<section class="process-stepper" '
            f'aria-label="Processing progress">{"".join(markup)}</section>'
        ),
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    """Render the application capability footer."""
    labels = ("Offline Mode", "CPU Only", "SQLite", "Ollama", "Tesseract")
    chips = "".join(f'<span class="footer-chip">{label}</span>' for label in labels)
    st.markdown(
        f"""
        <footer class="app-footer">
            <span class="app-footer__label">Local research stack</span>
            <div class="app-footer__chips">{chips}</div>
        </footer>
        """,
        unsafe_allow_html=True,
    )
