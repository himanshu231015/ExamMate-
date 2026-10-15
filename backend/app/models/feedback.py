"""Feedback and error reporting models."""

import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base


class FeedbackRating(str, enum.Enum):
    HELPFUL = "helpful"
    UNHELPFUL = "unhelpful"


class ErrorCategory(str, enum.Enum):
    INCORRECT_ANSWER = "incorrect_answer"
    IRRELEVANT_PYQ = "irrelevant_pyq"
    WRONG_SYLLABUS_MAPPING = "wrong_syllabus_mapping"
    UNSUPPORTED_CITATION = "unsupported_citation"
    MISSING_EXPLANATION = "missing_explanation"
    BROKEN_LINK = "broken_link"
    OTHER = "other"


class ReportStatus(str, enum.Enum):
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class UserFeedback(Base):
    __tablename__ = "user_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Enum(FeedbackRating), nullable=False)
    error_category = Column(Enum(ErrorCategory), nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    message = relationship("ChatMessage", back_populates="feedback")
    user = relationship("User", back_populates="feedbacks")


class ErrorReport(Base):
    __tablename__ = "error_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    report_category = Column(Enum(ErrorCategory), nullable=False, index=True)
    target_type = Column(String(50), nullable=False)  # "question_paper", "pyq", "syllabus_topic", "citation"
    target_id = Column(Integer, nullable=True)
    description = Column(Text, nullable=False)
    status = Column(Enum(ReportStatus), default=ReportStatus.OPEN, nullable=False, index=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="error_reports")
