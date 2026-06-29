# SPDX-License-Identifier: GPL-3.0-or-later
"""SQLAlchemy ORM models for SQLite database."""

import json
from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class Document(Base):
    """Represents an uploaded document with raw and cleaned text."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(Text, nullable=False)
    file_type = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=False)
    raw_text = Column(Text, nullable=True)
    cleaned_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    processed_at = Column(DateTime, nullable=True)
    status = Column(Text, default="pending")
    error_message = Column(Text, nullable=True)

    metadata_rel = relationship(
        "NoteMetadata", back_populates="document",
        uselist=False, cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs: Any) -> None:
        """Apply Python-side defaults expected by the app and tests."""
        super().__init__(**kwargs)
        if self.status is None:
            self.status = "pending"
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)


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

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary matching output schema."""
        return {
            "title": self.title or "",
            "subject": self.subject or "",
            "topics": json.loads(self.topics) if self.topics else [],
            "keywords": json.loads(self.keywords) if self.keywords else [],
            "summary": self.summary or "",
            "important_points": (
                json.loads(self.important_points) if self.important_points else []
            ),
            "possible_exam_questions": (
                json.loads(self.possible_exam_questions)
                if self.possible_exam_questions else []
            ),
            "difficulty": self.difficulty or "",
            "created_at": (
                self.document.created_at.isoformat()
                if self.document and self.document.created_at else ""
            ),
        }


def init_db(database_url: str = "sqlite:///data/lecture_notes.db") -> Any:
    """Initialize database connection and create all tables."""
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return engine


def get_session(engine: Any):
    """Create a new database session."""
    Session = sessionmaker(bind=engine)
    return Session()
