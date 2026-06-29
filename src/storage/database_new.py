# SPDX-License-Identifier: GPL-3.0-or-later
"""SQLite database operations using SQLAlchemy with FTS5 search."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import text

from src.storage.models import Document, NoteMetadata, get_session, init_db

_engine = None


def get_engine():
    """Get or create the database engine singleton."""
    global _engine
    if _engine is None:
        _engine = init_db("sqlite:///data/lecture_notes.db")
        _create_fts_table()
    return _engine


def _create_fts_table() -> None:
    """Create FTS5 virtual table for full-text search."""
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text(
            "CREATE VIRTUAL TABLE IF NOT EXISTS fts_notes USING fts5("
            "title, subject, topics, keywords, content, document_id UNINDEXED)"
        ))
        conn.commit()
}
