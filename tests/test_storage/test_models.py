# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for database models."""

import json
from datetime import datetime, timezone

import pytest

from src.storage.models import Document, NoteMetadata


class TestDocumentModel:
    """Test Document ORM model."""

    def test_document_default_status(self):
        """Test that new documents have 'pending' status."""
        doc = Document()
        assert doc.status == "pending"

    def test_document_with_fields(self):
        """Test document creation with fields."""
        now = datetime.now(timezone.utc)
        doc = Document(
            filename="test.pdf",
            file_type="pdf",
            file_size=1024,
            raw_text="raw content",
            cleaned_text="cleaned content",
            status="done",
            created_at=now,
        )
        assert doc.filename == "test.pdf"
        assert doc.file_type == "pdf"
        assert doc.file_size == 1024
        assert doc.raw_text == "raw content"
        assert doc.cleaned_text == "cleaned content"
        assert doc.status == "done"
        assert doc.created_at == now


class TestNoteMetadataModel:
    """Test NoteMetadata ORM model."""

    def test_note_metadata_defaults(self):
        """Test that new metadata has empty defaults."""
        meta = NoteMetadata()
        assert meta.title is None
        assert meta.subject is None
        assert meta.topics is None
        assert meta.keywords is None

    def test_note_metadata_to_dict_with_data(self):
        """Test conversion to dict with populated data."""
        meta = NoteMetadata(
            id=1,
            document_id=1,
            title="Test Lecture",
            subject="Computer Science",
            topics=json.dumps(["AI", "ML"]),
            keywords=json.dumps(["neural", "deep"]),
            summary="A test summary",
            important_points=json.dumps(["Point 1"]),
            possible_exam_questions=json.dumps(["Question 1?"]),
            difficulty="Intermediate",
        )
        result = meta.to_dict()
        assert result["title"] == "Test Lecture"
        assert result["subject"] == "Computer Science"
        assert result["topics"] == ["AI", "ML"]
        assert result["keywords"] == ["neural", "deep"]
        assert result["summary"] == "A test summary"
        assert result["important_points"] == ["Point 1"]
        assert result["possible_exam_questions"] == ["Question 1?"]
        assert result["difficulty"] == "Intermediate"

    def test_note_metadata_to_dict_empty(self):
        """Test conversion to dict with empty data."""
        meta = NoteMetadata(document_id=1)
        result = meta.to_dict()
        assert result["title"] == ""
        assert result["subject"] == ""
        assert result["topics"] == []
        assert result["keywords"] == []
        assert result["summary"] == ""
        assert result["difficulty"] == ""
