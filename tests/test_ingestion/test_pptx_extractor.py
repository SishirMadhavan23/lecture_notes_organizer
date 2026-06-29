# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for PowerPoint extraction."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from src.ingestion.pptx_extractor import (
    extract_presentation,
    extract_presentation_metadata,
    extract_text_from_pptx,
)
from src.utils.exceptions import ExtractionError

pptx = pytest.importorskip("pptx")
Presentation = pptx.Presentation


def _build_sample_presentation(path: Path) -> None:
    """Create a sample presentation for extraction tests."""
    presentation = Presentation()
    slide = presentation.slides.add_slide(presentation.slide_layouts[1])
    slide.shapes.title.text = "Week 1 Overview"

    body = slide.placeholders[1].text_frame
    body.text = "Introduction to AI"
    bullet = body.add_paragraph()
    bullet.text = "History of machine learning"
    bullet.level = 1

    table = slide.shapes.add_table(2, 2, 0, 0, 5_000_000, 1_500_000).table
    table.cell(0, 0).text = "Topic"
    table.cell(0, 1).text = "Weight"
    table.cell(1, 0).text = "Neural Networks"
    table.cell(1, 1).text = "40%"

    notes_frame = slide.notes_slide.notes_text_frame
    notes_frame.text = "Mention the Turing test."

    properties = presentation.core_properties
    properties.title = "Intro Lecture"
    properties.author = "Research Faculty"
    properties.created = datetime(2025, 1, 2, 3, 4, 5)
    presentation.save(path)


def test_extract_text_from_pptx_includes_slides_bullets_tables_and_notes(
    tmp_path: Path,
) -> None:
    """PPTX extraction should preserve presentation ordering and content."""
    pptx_path = tmp_path / "lecture.pptx"
    _build_sample_presentation(pptx_path)

    extracted = extract_text_from_pptx(str(pptx_path))

    assert "Presentation Metadata" in extracted
    assert "Title: Intro Lecture" in extracted
    assert "Slide 1" in extracted
    assert "Title: Week 1 Overview" in extracted
    assert "Introduction to AI" in extracted
    assert "- History of machine learning" in extracted
    assert "Topic | Weight" in extracted
    assert "Neural Networks | 40%" in extracted
    assert "Speaker Notes:" in extracted
    assert "Mention the Turing test." in extracted


def test_extract_presentation_metadata_reports_slide_count(tmp_path: Path) -> None:
    """Metadata inspection should expose upload preview information."""
    pptx_path = tmp_path / "lecture.pptx"
    _build_sample_presentation(pptx_path)

    metadata = extract_presentation_metadata(pptx_path)

    assert metadata["slide_count"] == 1
    assert metadata["title"] == "Intro Lecture"
    assert metadata["author"] == "Research Faculty"
    assert metadata["created"].startswith("2025-01-02T03:04:05")
    assert "Week 1 Overview" in metadata["preview"]


def test_extract_presentation_rejects_corrupt_file(tmp_path: Path) -> None:
    """Corrupt PowerPoint files should raise a friendly extraction error."""
    broken_path = tmp_path / "broken.pptx"
    broken_path.write_bytes(b"not a presentation")

    with pytest.raises(ExtractionError):
        extract_presentation(broken_path)


def test_legacy_ppt_requires_converter(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Legacy PPT uploads should fail cleanly when no converter is available."""
    legacy_path = tmp_path / "legacy.ppt"
    legacy_path.write_bytes(b"legacy presentation")
    monkeypatch.setattr(
        "src.ingestion.pptx_extractor._find_office_converter",
        lambda: None,
    )

    with pytest.raises(ExtractionError, match="LibreOffice"):
        extract_text_from_pptx(str(legacy_path))
