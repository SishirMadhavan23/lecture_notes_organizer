"""Tests for database operations."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.storage.database import (
    _build_note_dict,
    _create_fts_table,
    _document_file_size,
    _resolve_database_url,
    _serialize_list,
    delete_document,
    get_all_documents,
    get_engine,
    get_stats,
    save_document,
    search_notes,
)
from src.storage.models import Document, NoteMetadata, get_session, init_db


class TestResolveDatabaseUrl:
    """Tests for _resolve_database_url function."""

    def test_absolute_sqlite_url(self) -> None:
        """Test absolute SQLite URL is preserved."""
        url = _resolve_database_url("sqlite:////absolute/path/db.sqlite")
        assert url.startswith("sqlite:///")

    def test_non_sqlite_url(self) -> None:
        """Test non-SQLite URL is returned as-is."""
        url = _resolve_database_url("postgresql://localhost/db")
        assert url == "postgresql://localhost/db"

    def test_relative_sqlite_url_resolved(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test relative SQLite URL is resolved against base_dir."""
        from src.utils.config import AppConfig

        config = AppConfig()

        def mock_load_config() -> AppConfig:
            return config

        monkeypatch.setattr("src.storage.database.load_config", mock_load_config)
        url = _resolve_database_url("sqlite:///data/test.db")
        assert url.startswith("sqlite:///")


class TestCreateFtsTable:
    """Tests for _create_fts_table function."""

    def test_successful_creation(self) -> None:
        """Test FTS table is created successfully."""
        engine = init_db("sqlite:///:memory:")
        result = _create_fts_table(engine)
        assert result is True

    def test_idempotent_creation(self) -> None:
        """Test creating FTS table twice doesn't fail."""
        engine = init_db("sqlite:///:memory:")
        _create_fts_table(engine)
        result = _create_fts_table(engine)
        assert result is True


class TestSerializeList:
    """Tests for _serialize_list function."""

    def test_none_values(self) -> None:
        """Test returns empty JSON array for None."""
        assert _serialize_list(None) == json.dumps([])

    def test_empty_values(self) -> None:
        """Test returns empty JSON array for empty."""
        assert _serialize_list([]) == json.dumps([])
        assert _serialize_list("") == json.dumps([])

    def test_string_value(self) -> None:
        """Test wraps single string in list."""
        assert _serialize_list("test") == json.dumps(["test"])

    def test_list_value(self) -> None:
        """Test serializes list as-is."""
        assert _serialize_list(["a", "b"]) == json.dumps(["a", "b"])

    def test_non_iterable(self) -> None:
        """Test wraps non-iterable in list."""
        assert _serialize_list(42) == json.dumps(["42"])


class TestDocumentFileSize:
    """Tests for _document_file_size function."""

    def test_existing_file(self, temp_txt_file: Path) -> None:
        """Test returns file size for existing file."""
        size = _document_file_size(str(temp_txt_file), "fallback")
        assert size > 0

    def test_nonexistent_file(self) -> None:
        """Test returns text length for nonexistent file."""
        size = _document_file_size("/nonexistent/file.txt", "test text content")
        assert size == len(b"test text content")


class TestBuildNoteDict:
    """Tests for _build_note_dict function."""

    def test_build_from_document(self, in_memory_db) -> None:
        """Test building note dict from document with metadata."""
        engine = in_memory_db
        session = get_session(engine)

        doc = Document(
            filename="test.pdf",
            file_type="pdf",
            file_size=1024,
            raw_text="raw",
            cleaned_text="cleaned",
            status="processed",
        )
        session.add(doc)
        session.flush()

        meta = NoteMetadata(
            document_id=doc.id,
            title="Test Title",
            subject="CS",
            topics=json.dumps(["AI"]),
            keywords=json.dumps(["ML"]),
        )
        session.add(meta)
        session.commit()
        session.refresh(doc)

        result = _build_note_dict(doc)
        assert result["filename"] == "test.pdf"
        assert result["title"] == "Test Title"
        assert result["subject"] == "CS"
        assert result["status"] == "processed"
        session.close()


class TestSaveDocument:
    """Tests for save_document function."""

    def test_save_document_success(self, in_memory_db) -> None:
        """Test saving a document succeeds."""
        import src.storage.database as db_module

        original_engine = db_module._engine
        original_fts = db_module._fts_ready
        db_module._engine = in_memory_db
        db_module._fts_ready = False
        try:
            doc_id = save_document(
                "test.pdf",
                "raw text",
                "cleaned text",
                {
                    "title": "Test",
                    "subject": "CS",
                    "topics": ["AI"],
                    "keywords": ["ML"],
                },
            )
            assert isinstance(doc_id, int)
            assert doc_id > 0
        finally:
            db_module._engine = original_engine
            db_module._fts_ready = original_fts

    def test_save_document_minimal(self, in_memory_db) -> None:
        """Test saving document with minimal metadata."""
        import src.storage.database as db_module

        original_engine = db_module._engine
        original_fts = db_module._fts_ready
        db_module._engine = in_memory_db
        db_module._fts_ready = False
        try:
            doc_id = save_document("test.txt", "raw", "cleaned")
            assert isinstance(doc_id, int)
        finally:
            db_module._engine = original_engine
            db_module._fts_ready = original_fts

    def test_save_document_unknown_type(self, in_memory_db) -> None:
        """Test saving document with unknown file type."""
        import src.storage.database as db_module

        original_engine = db_module._engine
        original_fts = db_module._fts_ready
        db_module._engine = in_memory_db
        db_module._fts_ready = False
        try:
            doc_id = save_document("file.xyz", "content", "cleaned")
            assert isinstance(doc_id, int)
        finally:
            db_module._engine = original_engine
            db_module._fts_ready = original_fts

    def test_save_document_no_source_file(self, in_memory_db) -> None:
        """Test saving document when source file doesn't exist."""
        import src.storage.database as db_module

        original_engine = db_module._engine
        original_fts = db_module._fts_ready
        db_module._engine = in_memory_db
        db_module._fts_ready = False
        try:
            doc_id = save_document("/nonexistent/file.pdf", "raw content", "cleaned")
            assert isinstance(doc_id, int)
        finally:
            db_module._engine = original_engine
            db_module._fts_ready = original_fts


class TestGetAllDocuments:
    """Tests for get_all_documents function."""

    def test_empty_database(self, in_memory_db) -> None:
        """Test returns empty list when no documents."""
        import src.storage.database as db_module

        original_engine = db_module._engine
        original_fts = db_module._fts_ready
        db_module._engine = in_memory_db
        db_module._fts_ready = False
        try:
            docs = get_all_documents()
            assert docs == []
        finally:
            db_module._engine = original_engine
            db_module._fts_ready = original_fts

    def test_returns_documents(self, in_memory_db) -> None:
        """Test returns saved documents."""
        import src.storage.database as db_module

        original_engine = db_module._engine
        original_fts = db_module._fts_ready
        db_module._engine = in_memory_db
        db_module._fts_ready = False
        try:
            save_document("test.pdf", "raw", "cleaned", {"title": "Doc 1"})
            docs = get_all_documents()
            assert len(docs) == 1
            assert docs[0]["filename"] == "test.pdf"
        finally:
            db_module._engine = original_engine
            db_module._fts_ready = original_fts


class TestSearchNotes:
    """Tests for search_notes function."""

    def test_empty_query(self, in_memory_db) -> None:
        """Test returns empty list for empty query."""
        import src.storage.database as db_module

        original_engine = db_module._engine
        original_fts = db_module._fts_ready
        db_module._engine = in_memory_db
        db_module._fts_ready = False
        try:
            results = search_notes("")
            assert results == []
            results = search_notes("  ")
            assert results == []
        finally:
            db_module._engine = original_engine
            db_module._fts_ready = original_fts

    def test_fallback_search_works(self, in_memory_db) -> None:
        """Test fallback LIKE search finds matching documents."""
        import src.storage.database as db_module

        original_engine = db_module._engine
        original_fts = db_module._fts_ready
        db_module._engine = in_memory_db
        db_module._fts_ready = False
        try:
            # Save a document via save_document
            save_document(
                "test.pdf",
                "machine learning concepts",
                "machine learning concepts",
                {"title": "ML"},
            )
            results = search_notes("machine")
            assert len(results) >= 1
            assert results[0]["title"] == "ML"
        finally:
            db_module._engine = original_engine
            db_module._fts_ready = original_fts

    def test_fts_search(self, in_memory_db) -> None:
        """Test FTS search works when FTS is enabled."""
        import src.storage.database as db_module

        original_engine = db_module._engine
        original_fts = db_module._fts_ready
        db_module._engine = in_memory_db
        db_module._fts_ready = True  # Enable FTS
        try:
            # Ensure FTS table exists
            _create_fts_table(in_memory_db)
            # Save document - this triggers FTS sync
            save_document("test.pdf", "deep learning", "deep learning", {"title": "DL"})
            results = search_notes("deep")
            assert len(results) >= 1
            assert results[0]["title"] == "DL"
        finally:
            db_module._engine = original_engine
            db_module._fts_ready = original_fts


class TestDeleteDocument:
    """Tests for delete_document function."""

    def test_delete_existing(self, in_memory_db) -> None:
        """Test deleting an existing document."""
        import src.storage.database as db_module

        original_engine = db_module._engine
        original_fts = db_module._fts_ready
        db_module._engine = in_memory_db
        db_module._fts_ready = False
        try:
            doc_id = save_document("test.pdf", "raw", "cleaned")
            result = delete_document(doc_id)
            assert result is True
            docs = get_all_documents()
            assert len(docs) == 0
        finally:
            db_module._engine = original_engine
            db_module._fts_ready = original_fts

    def test_delete_nonexistent(self, in_memory_db) -> None:
        """Test deleting a nonexistent document returns False."""
        import src.storage.database as db_module

        original_engine = db_module._engine
        original_fts = db_module._fts_ready
        db_module._engine = in_memory_db
        db_module._fts_ready = False
        try:
            result = delete_document(999)
            assert result is False
        finally:
            db_module._engine = original_engine
            db_module._fts_ready = original_fts


class TestGetStats:
    """Tests for get_stats function."""

    def test_empty_stats(self, in_memory_db) -> None:
        """Test stats for empty database."""
        import src.storage.database as db_module

        original_engine = db_module._engine
        original_fts = db_module._fts_ready
        db_module._engine = in_memory_db
        db_module._fts_ready = False
        try:
            stats = get_stats()
            assert stats["total_documents"] == 0
            assert stats["processed"] == 0
            assert stats["errors"] == 0
        finally:
            db_module._engine = original_engine
            db_module._fts_ready = original_fts

    def test_stats_with_documents(self, in_memory_db) -> None:
        """Test stats with documents."""
        import src.storage.database as db_module

        original_engine = db_module._engine
        original_fts = db_module._fts_ready
        db_module._engine = in_memory_db
        db_module._fts_ready = False
        try:
            save_document("test.pdf", "raw", "cleaned")
            stats = get_stats()
            assert stats["total_documents"] >= 1
            assert stats["processed"] >= 1
        finally:
            db_module._engine = original_engine
            db_module._fts_ready = original_fts


class TestGetEngine:
    """Tests for get_engine function."""

    def test_engine_initialization(self) -> None:
        """Test engine is initialized."""
        import src.storage.database as db_module

        original_engine = db_module._engine
        db_module._engine = None
        db_module._fts_ready = False

        try:
            engine = get_engine()
            assert engine is not None
        finally:
            db_module._engine = original_engine

    def test_engine_singleton(self) -> None:
        """Test engine is a singleton."""
        import src.storage.database as db_module

        original_engine = db_module._engine
        db_module._engine = None
        db_module._fts_ready = False

        try:
            engine1 = get_engine()
            engine2 = get_engine()
            assert engine1 is engine2
        finally:
            db_module._engine = original_engine
