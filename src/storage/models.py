# SPDX-License-Identifier: GPL-3.0-or-later
"""SQLAlchemy ORM models for SQLite database."""

import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, relationship, sessionmaker


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""


class Document(Base):
    """Represents an uploaded document with raw and cleaned text."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(Text, nullable=False)
    file_type = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=False)
    raw_text = Column(Text, nullable=True)
    cleaned_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    processed_at = Column(DateTime, nullable=True)
    status = Column(Text, default="pending")
    error_message = Column(Text, nullable=True)

    metadata_rel = relationship(
        "NoteMetadata",
        back_populates="document",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs: Any) -> None:
        """Apply Python-side defaults expected by the app and tests."""
        super().__init__(**kwargs)
        if self.status is None:
            self.status = "pending"
        if self.created_at is None:
            self.created_at = datetime.now(UTC)


class NoteMetadata(Base):
    """Structured metadata extracted from lecture notes via AI."""

    __tablename__ = "note_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    title = Column(Text, nullable=True)
    subject = Column(Text, nullable=True)
    topics = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    important_points = Column(Text, nullable=True)
    possible_exam_questions = Column(Text, nullable=True)
    difficulty = Column(Text, nullable=True)

    document = relationship("Document", back_populates="metadata_rel")

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary matching output schema."""
        topics_value = str(self.topics or "[]")
        keywords_value = str(self.keywords or "[]")
        important_points_value = str(self.important_points or "[]")
        possible_exam_questions_value = str(self.possible_exam_questions or "[]")
        return {
            "title": self.title or "",
            "subject": self.subject or "",
            "topics": json.loads(topics_value) if topics_value else [],
            "keywords": json.loads(keywords_value) if keywords_value else [],
            "summary": self.summary or "",
            "important_points": (
                json.loads(important_points_value) if important_points_value else []
            ),
            "possible_exam_questions": (
                json.loads(possible_exam_questions_value)
                if possible_exam_questions_value
                else []
            ),
            "difficulty": self.difficulty or "",
            "created_at": (
                self.document.created_at.isoformat()
                if self.document and self.document.created_at
                else ""
            ),
        }


def init_db(database_url: str = "sqlite:///data/lecture_notes.db") -> Any:
    """Initialize database connection and create all tables."""
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return engine


def get_session(engine: Any) -> Session:
    """Create a new database session."""
    session_factory = sessionmaker(bind=engine)
    return session_factory()
