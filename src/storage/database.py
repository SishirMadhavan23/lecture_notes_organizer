"""SQLite database operations using SQLAlchemy with optional FTS5 search."""

from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from src.storage.models import Document, NoteMetadata, get_session, init_db
from src.utils.config import load_config
from src.utils.exceptions import StorageError

logger = logging.getLogger(__name__)

_engine: Engine | None = None
_fts_ready = False


def _resolve_database_url(database_url: str | None = None) -> str:
    """Resolve a deployment-safe database URL."""
    config = load_config()
    raw_url = database_url or config.database_url

    if not raw_url.startswith("sqlite:///"):
        return raw_url

    db_path = Path(raw_url.removeprefix("sqlite:///"))
    if not db_path.is_absolute():
        db_path = config.base_dir / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path.as_posix()}"


def get_engine() -> Engine:
    """Return the singleton SQLAlchemy engine and initialize storage."""
    global _engine, _fts_ready

    if _engine is None:
        _engine = init_db(_resolve_database_url())
        _fts_ready = _create_fts_table(_engine)
    elif not _fts_ready:
        _fts_ready = _create_fts_table(_engine)

    return _engine


def _create_fts_table(engine: Engine) -> bool:
    """Create the FTS5 index table if SQLite supports it."""
    create_sql = """
        CREATE VIRTUAL TABLE IF NOT EXISTS fts_notes USING fts5(
            document_id UNINDEXED,
            filename,
            title,
            subject,
            topics,
            keywords,
            summary,
            content
        )
    """
    try:
        with engine.begin() as connection:
            connection.execute(text(create_sql))
        return True
    except SQLAlchemyError as exc:
        logger.warning(
            "FTS5 initialization failed; falling back to LIKE search: %s",
            exc,
        )
        return False


def _serialize_list(values: Any) -> str:
    if not values:
        return json.dumps([])
    if isinstance(values, str):
        return json.dumps([values])
    if isinstance(values, Iterable):
        return json.dumps(list(values))
    return json.dumps([str(values)])


def _document_file_size(source_name: str, raw_text: str) -> int:
    source_path = Path(source_name)
    if source_path.exists() and source_path.is_file():
        return source_path.stat().st_size
    return len(raw_text.encode("utf-8"))


def _build_note_dict(document: Document) -> dict[str, Any]:
    metadata = document.metadata_rel.to_dict() if document.metadata_rel else {}
    return {
        "id": document.id,
        "filename": document.filename,
        "file_type": document.file_type,
        "file_size": document.file_size,
        "raw_text": document.raw_text or "",
        "cleaned_text": document.cleaned_text or "",
        "status": document.status,
        "error_message": document.error_message,
        "created_at": document.created_at.isoformat() if document.created_at else "",
        "processed_at": (
            document.processed_at.isoformat() if document.processed_at else ""
        ),
        "title": metadata.get("title", ""),
        "subject": metadata.get("subject", ""),
        "topics": metadata.get("topics", []),
        "keywords": metadata.get("keywords", []),
        "summary": metadata.get("summary", ""),
        "important_points": metadata.get("important_points", []),
        "possible_exam_questions": metadata.get("possible_exam_questions", []),
        "difficulty": metadata.get("difficulty", ""),
    }


def _sync_fts_row(
    document_id: int,
    filename: str,
    cleaned_text: str,
    metadata: dict[str, Any],
) -> None:
    if not _fts_ready:
        return

    engine = get_engine()
    topics = " ".join(metadata.get("topics", []))
    keywords = " ".join(metadata.get("keywords", []))

    with engine.begin() as connection:
        connection.execute(
            text("DELETE FROM fts_notes WHERE document_id = :document_id"),
            {"document_id": document_id},
        )
        connection.execute(
            text(
                "INSERT INTO fts_notes ("
                "document_id, filename, title, subject, "
                "topics, keywords, summary, content"
                ") VALUES ("
                ":document_id, :filename, :title, :subject, "
                ":topics, :keywords, :summary, :content"
                ")"
            ),
            {
                "document_id": document_id,
                "filename": filename,
                "title": metadata.get("title", ""),
                "subject": metadata.get("subject", ""),
                "topics": topics,
                "keywords": keywords,
                "summary": metadata.get("summary", ""),
                "content": cleaned_text,
            },
        )


def save_document(
    source_name: str,
    raw_text: str,
    cleaned_text: str,
    metadata: dict[str, Any] | None = None,
) -> int:
    """Persist a processed document and its extracted metadata."""
    engine = get_engine()
    note_metadata = metadata or {}
    filename = Path(source_name).name
    file_type = Path(filename).suffix.lower().lstrip(".") or "unknown"

    session = get_session(engine)
    try:
        document = Document(
            filename=filename,
            file_type=file_type,
            file_size=_document_file_size(source_name, raw_text),
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            processed_at=datetime.now(UTC),
            status="processed",
        )
        session.add(document)
        session.flush()

        session.add(
            NoteMetadata(
                document_id=document.id,
                title=note_metadata.get("title", ""),
                subject=note_metadata.get("subject", ""),
                topics=_serialize_list(note_metadata.get("topics")),
                keywords=_serialize_list(note_metadata.get("keywords")),
                summary=note_metadata.get("summary", ""),
                important_points=_serialize_list(note_metadata.get("important_points")),
                possible_exam_questions=_serialize_list(
                    note_metadata.get("possible_exam_questions")
                ),
                difficulty=note_metadata.get("difficulty", ""),
            )
        )
        session.commit()

        _sync_fts_row(document.id, filename, cleaned_text, note_metadata)
        return int(document.id)
    except SQLAlchemyError as exc:
        session.rollback()
        raise StorageError(f"Failed to save document: {exc}") from exc
    finally:
        session.close()


def get_all_documents() -> list[dict[str, Any]]:
    """Return all processed documents with their metadata."""
    engine = get_engine()
    session = get_session(engine)
    try:
        stmt = (
            select(Document)
            .options(selectinload(Document.metadata_rel))
            .order_by(Document.created_at.desc())
        )
        documents = session.execute(stmt).scalars().all()
        return [_build_note_dict(document) for document in documents]
    except SQLAlchemyError as exc:
        raise StorageError(f"Failed to load documents: {exc}") from exc
    finally:
        session.close()


def _fts_search(query: str) -> list[dict[str, Any]]:
    engine = get_engine()
    session = get_session(engine)
    try:
        stmt = text("""
            SELECT d.id
            FROM fts_notes f
            JOIN documents d ON d.id = f.document_id
            WHERE fts_notes MATCH :query
            ORDER BY bm25(fts_notes), d.created_at DESC
            """)
        ids = [row[0] for row in session.execute(stmt, {"query": query}).all()]
        if not ids:
            return []

        documents = (
            session.execute(
                select(Document)
                .options(selectinload(Document.metadata_rel))
                .where(Document.id.in_(ids))
            )
            .scalars()
            .all()
        )
        documents_by_id = {document.id: document for document in documents}
        ordered_documents = [
            documents_by_id[document_id]
            for document_id in ids
            if document_id in documents_by_id
        ]
        return [_build_note_dict(document) for document in ordered_documents]
    finally:
        session.close()


def _fallback_search(query: str) -> list[dict[str, Any]]:
    engine = get_engine()
    session = get_session(engine)
    pattern = f"%{query}%"
    try:
        stmt = (
            select(Document)
            .options(selectinload(Document.metadata_rel))
            .join(NoteMetadata, NoteMetadata.document_id == Document.id, isouter=True)
            .where(
                (Document.filename.ilike(pattern))
                | (Document.cleaned_text.ilike(pattern))
                | (NoteMetadata.title.ilike(pattern))
                | (NoteMetadata.subject.ilike(pattern))
                | (NoteMetadata.summary.ilike(pattern))
                | (NoteMetadata.topics.ilike(pattern))
                | (NoteMetadata.keywords.ilike(pattern))
            )
            .order_by(Document.created_at.desc())
        )
        documents = session.execute(stmt).scalars().unique().all()
        return [_build_note_dict(document) for document in documents]
    finally:
        session.close()


def search_notes(query: str) -> list[dict[str, Any]]:
    """Search across stored notes, preferring FTS5 when available."""
    cleaned_query = query.strip()
    if not cleaned_query:
        return []

    if _fts_ready:
        try:
            return _fts_search(cleaned_query)
        except SQLAlchemyError as exc:
            logger.warning("FTS search failed; falling back to LIKE search: %s", exc)

    try:
        return _fallback_search(cleaned_query)
    except SQLAlchemyError as exc:
        raise StorageError(f"Failed to search notes: {exc}") from exc


def delete_document(document_id: int) -> bool:
    """Delete a document and its associated metadata."""
    engine = get_engine()
    session = get_session(engine)
    try:
        document = session.get(Document, document_id)
        if document is None:
            return False

        session.delete(document)
        session.commit()

        if _fts_ready:
            with engine.begin() as connection:
                connection.execute(
                    text("DELETE FROM fts_notes WHERE document_id = :document_id"),
                    {"document_id": document_id},
                )
        return True
    except SQLAlchemyError as exc:
        session.rollback()
        raise StorageError(f"Failed to delete document: {exc}") from exc
    finally:
        session.close()


def get_stats() -> dict[str, Any]:
    """Return basic database statistics for the status dashboard."""
    engine = get_engine()
    session = get_session(engine)
    try:
        total_documents = session.scalar(select(func.count(Document.id))) or 0
        processed = (
            session.scalar(
                select(func.count(Document.id)).where(Document.status == "processed")
            )
            or 0
        )
        errors = (
            session.scalar(
                select(func.count(Document.id)).where(Document.status == "error")
            )
            or 0
        )
    except SQLAlchemyError as exc:
        raise StorageError(f"Failed to collect database stats: {exc}") from exc
    finally:
        session.close()

    database_path = Path(engine.url.database or "")
    database_size = database_path.stat().st_size if database_path.exists() else 0
    return {
        "total_documents": int(total_documents),
        "processed": int(processed),
        "errors": int(errors),
        "database_size_bytes": int(database_size),
    }
