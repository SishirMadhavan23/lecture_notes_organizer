# SPDX-License-Identifier: GPL-3.0-or-later
"""Note card display component."""

import re
from collections.abc import Iterable
from html import escape
from typing import Any

import streamlit as st


def _difficulty_tone(difficulty: str) -> str:
    tones = {
        "Beginner": "meta-pill",
        "Intermediate": "meta-pill meta-pill--accent",
        "Advanced": "meta-pill",
    }
    return tones.get(difficulty, "meta-pill")


def _format_file_size(size_bytes: int) -> str:
    """Format file size for UI display."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / 1024 / 1024:.2f} MB"


def _is_presentation(note: dict[str, Any]) -> bool:
    """Return whether the note originated from a PowerPoint upload."""
    return str(note.get("file_type", "")).lower() in {"pptx", "ppt"}


def _normalize_study_items(
    items: Iterable[Any],
) -> tuple[list[str], list[dict[str, str]]]:
    """Split stored study items into exam questions and flashcards."""
    questions: list[str] = []
    flashcards: list[dict[str, str]] = []

    for item in items or []:
        if isinstance(item, dict):
            item_type = str(item.get("type", "")).lower()
            if item_type == "flashcard":
                front = str(item.get("front", "")).strip()
                back = str(item.get("back", "")).strip()
                if front or back:
                    flashcards.append({"front": front, "back": back})
                continue

            text = str(item.get("text", "")).strip()
            if text:
                questions.append(text)
            continue

        text = str(item).strip()
        if text:
            questions.append(text)

    return questions, flashcards


def _parse_presentation_details(raw_text: str) -> dict[str, Any]:
    """Parse presentation metadata and slide sections from stored raw text."""
    metadata = {
        "title": "",
        "author": "",
        "created": "",
        "slide_count": 0,
        "slides": [],
        "has_speaker_notes": False,
    }
    if not raw_text.startswith("Presentation Metadata"):
        return metadata

    title_match = re.search(r"^Title:\s*(.*)$", raw_text, re.MULTILINE)
    author_match = re.search(r"^Author:\s*(.*)$", raw_text, re.MULTILINE)
    created_match = re.search(r"^Created:\s*(.*)$", raw_text, re.MULTILINE)
    slide_count_match = re.search(r"^Slides:\s*(\d+)$", raw_text, re.MULTILINE)

    metadata["title"] = title_match.group(1).strip() if title_match else ""
    metadata["author"] = author_match.group(1).strip() if author_match else ""
    metadata["created"] = created_match.group(1).strip() if created_match else ""
    metadata["slide_count"] = (
        int(slide_count_match.group(1)) if slide_count_match else 0
    )

    slide_pattern = re.compile(
        r"(?ms)^Slide (?P<number>\d+)\s*$\n(?P<body>.*?)(?=^Slide \d+\s*$|\Z)"
    )
    slides = []
    for match in slide_pattern.finditer(raw_text):
        number = int(match.group("number"))
        body = match.group("body").strip()
        if "Speaker Notes:" in body:
            metadata["has_speaker_notes"] = True
        slides.append({"number": number, "content": body})
    metadata["slides"] = slides
    return metadata


def _render_general_tab(note: dict[str, Any]) -> None:
    """Render general note metadata."""
    st.markdown(f"**Filename:** `{note.get('filename', 'N/A')}`")
    st.markdown(f"**File type:** `{str(note.get('file_type', 'N/A')).upper()}`")
    st.markdown(
        f"**File size:** {_format_file_size(int(note.get('file_size', 0) or 0))}"
    )
    st.markdown(f"**Upload time:** `{note.get('created_at', 'N/A')}`")
    st.markdown(f"**Subject:** `{note.get('subject') or 'General'}`")


def _render_intermediate_tab(note: dict[str, Any]) -> None:
    """Render AI-generated summary information."""
    topics = note.get("topics", [])
    keywords = note.get("keywords", [])
    points = note.get("important_points", [])
    summary = note.get("summary", "")

    st.markdown("**Summary**")
    st.write(summary or "No summary available yet.")

    st.markdown("**Topics**")
    if topics:
        for topic in topics:
            st.markdown(f"- {topic}")
    else:
        st.caption("No topics available.")

    st.markdown("**Keywords**")
    if keywords:
        st.write(", ".join(str(keyword) for keyword in keywords))
    else:
        st.caption("No keywords available.")

    st.markdown("**Important points**")
    if points:
        for point in points:
            st.markdown(f"- {point}")
    else:
        st.caption("No important points available.")


def _render_presentation_metadata_tab(note: dict[str, Any]) -> None:
    """Render PowerPoint-specific metadata."""
    presentation = _parse_presentation_details(note.get("raw_text", ""))
    st.markdown(
        f"**Presentation title:** "
        f"`{presentation['title'] or note.get('title') or 'Unknown'}`"
    )
    st.markdown(f"**Author:** `{presentation['author'] or 'Unknown'}`")
    st.markdown(f"**Number of slides:** `{presentation['slide_count'] or 0}`")
    st.markdown(f"**Created date:** `{presentation['created'] or 'Unknown'}`")

    st.markdown("**Slide metadata**")
    if presentation["slides"]:
        slide_labels = ", ".join(
            f"Slide {slide['number']}" for slide in presentation["slides"]
        )
        st.write(slide_labels)
    else:
        st.caption("No slide metadata available.")

    st.markdown("**Extraction information**")
    st.write(
        "Extracted locally with the offline PowerPoint parser and stored in SQLite."
    )
    st.write(
        "Speaker notes detected: "
        f"{'Yes' if presentation['has_speaker_notes'] else 'No'}"
    )


def _render_content_tabs(note: dict[str, Any]) -> None:
    """Render the document detail tabs."""
    questions, flashcards = _normalize_study_items(
        note.get("possible_exam_questions", [])
    )
    presentation = _parse_presentation_details(note.get("raw_text", ""))

    labels = ["Overview", "Summary", "Topics"]
    if _is_presentation(note):
        labels.append("Slides")
    labels.extend(["Flashcards", "Questions"])
    tabs = st.tabs(labels)
    tab_map = dict(zip(labels, tabs))

    with tab_map["Overview"]:
        st.markdown(
            f"**Title:** {note.get('title') or note.get('filename', 'Untitled')}"
        )
        st.markdown(f"**Subject:** {note.get('subject') or 'General'}")
        st.markdown(f"**Difficulty:** {note.get('difficulty') or 'Intermediate'}")
        st.markdown(f"**Processed:** `{note.get('created_at', 'N/A')}`")
        st.markdown(
            f"**File:** "
            f"`{note.get('filename', 'N/A')} "
            f"({str(note.get('file_type', 'N/A')).upper()})`"
        )
        st.write(note.get("summary") or "No summary available yet.")

    with tab_map["Summary"]:
        st.write(note.get("summary") or "No summary available yet.")
        points = note.get("important_points", [])
        if points:
            st.markdown("**Important points**")
            for point in points:
                st.markdown(f"- {point}")

    with tab_map["Topics"]:
        topics = note.get("topics", [])
        keywords = note.get("keywords", [])
        if topics:
            st.markdown("**Topics**")
            for topic in topics:
                st.markdown(f"- {topic}")
        else:
            st.caption("No topics available.")

        if keywords:
            st.markdown("**Keywords**")
            st.write(", ".join(str(keyword) for keyword in keywords))
        else:
            st.caption("No keywords available.")

    if "Slides" in tab_map:
        with tab_map["Slides"]:
            st.markdown(
                f"**Presentation title:** "
                f"{presentation['title'] or note.get('title') or 'Unknown'}"
            )
            st.markdown(f"**Author:** {presentation['author'] or 'Unknown'}")
            st.markdown(f"**Created date:** {presentation['created'] or 'Unknown'}")
            st.markdown(f"**Slide count:** {presentation['slide_count'] or 0}")

            if presentation["slides"]:
                for slide in presentation["slides"]:
                    with st.expander(f"Slide {slide['number']}", expanded=False):
                        st.text(slide["content"])
            else:
                st.caption("No slide content available.")

    with tab_map["Flashcards"]:
        if flashcards:
            for index, flashcard in enumerate(flashcards, start=1):
                with st.expander(f"Flashcard {index}", expanded=False):
                    st.markdown(f"**Front:** {flashcard['front'] or 'N/A'}")
                    st.markdown(f"**Back:** {flashcard['back'] or 'N/A'}")
        else:
            st.caption("No flashcards available.")

    with tab_map["Questions"]:
        if questions:
            for question in questions:
                st.markdown(f"- {question}")
        else:
            st.caption("No exam questions available.")


def render_note_card(note: dict[str, Any], expanded: bool = False) -> None:
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

    with st.container(border=True):
        meta_items = []
        if subject:
            meta_items.append(f'<span class="meta-pill">{escape(subject)}</span>')
        if difficulty:
            meta_items.append(
                f'<span class="{_difficulty_tone(difficulty)}">'
                f"{escape(difficulty)}</span>"
            )
        meta_items.append(
            f'<span class="meta-pill">'
            f"{escape(note.get('file_type', 'N/A').upper())}</span>"
        )

        summary_text = summary[:300] + ("..." if len(summary) > 300 else "")
        topic_markup = "".join(
            f'<span class="topic-badge">{escape(str(topic))}</span>'
            for topic in topics[:6]
        )
        keyword_markup = "".join(
            f'<span class="keyword-badge">{escape(str(keyword))}</span>'
            for keyword in keywords[:8]
        )

        st.markdown(
            f"""
            <h3 class="page-title" style="font-size: 1.25rem; margin-bottom: 0.2rem;">
                {escape(title)}
            </h3>
            <div class="meta-row">{"".join(meta_items)}</div>
            <p class="note-summary">
                {escape(summary_text) if summary_text else "No summary available yet."}
            </p>
            """,
            unsafe_allow_html=True,
        )

        if topic_markup:
            st.markdown(
                (
                    f'<div class="section-label">Topics</div>'
                    f'<div class="badge-row">{topic_markup}</div>'
                ),
                unsafe_allow_html=True,
            )
        if keyword_markup:
            st.markdown(
                (
                    f'<div class="section-label">Keywords</div>'
                    f'<div class="badge-row">{keyword_markup}</div>'
                ),
                unsafe_allow_html=True,
            )

        with st.expander("Document details", expanded=expanded):
            if _is_presentation(note):
                general_label = note.get("subject") or "General"
                intermediate_label = note.get("difficulty") or "Intermediate"
                pptx_label = str(note.get("file_type", "PPTX")).upper()
                general_tab, intermediate_tab, pptx_tab = st.tabs(
                    [general_label, intermediate_label, pptx_label]
                )
                with general_tab:
                    _render_general_tab(note)
                with intermediate_tab:
                    _render_intermediate_tab(note)
                with pptx_tab:
                    _render_presentation_metadata_tab(note)

            _render_content_tabs(note)
