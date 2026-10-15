"""AI Chat, retrieval log, and citation models."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, default="New Study Session")
    is_archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    subject = relationship("Subject", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.id")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    intent_classification = Column(String(50), nullable=True)  # "concept_explanation", "pyq_solution", "out_of_scope", etc.
    is_within_scope = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    retrieval_records = relationship("RetrievalRecord", back_populates="message", cascade="all, delete-orphan")
    citations = relationship("Citation", back_populates="message", cascade="all, delete-orphan")
    feedback = relationship("UserFeedback", back_populates="message", uselist=False, cascade="all, delete-orphan")


class RetrievalRecord(Base):
    __tablename__ = "retrieval_records"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False, index=True)
    retrieval_type = Column(String(50), nullable=False)  # "bm25", "semantic", "hybrid"
    query_text = Column(Text, nullable=False)
    results_count = Column(Integer, default=0, nullable=False)
    latency_ms = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    message = relationship("ChatMessage", back_populates="retrieval_records")


class Citation(Base):
    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type = Column(String(50), nullable=False)  # "syllabus_unit", "question_paper", "pyq"
    source_id = Column(Integer, nullable=True)
    document_title = Column(String(255), nullable=False)
    university_name = Column(String(100), default="RGPV", nullable=False)
    subject_code = Column(String(50), nullable=True)
    unit_number = Column(Integer, nullable=True)
    exam_year = Column(Integer, nullable=True)
    exam_session = Column(String(50), nullable=True)
    page_number = Column(Integer, nullable=True)
    question_number = Column(String(50), nullable=True)
    source_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    message = relationship("ChatMessage", back_populates="citations")
