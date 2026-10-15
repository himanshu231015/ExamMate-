"""Paper submissions, review decisions, and document versioning models."""

import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.question_paper import ExamType, ExamSession


class SubmissionStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    RETURNED_FOR_CORRECTION = "returned_for_correction"


class PaperSubmission(Base):
    __tablename__ = "paper_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    scheme_id = Column(Integer, ForeignKey("academic_schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    exam_year = Column(Integer, nullable=False)
    exam_session = Column(Enum(ExamSession), nullable=False)
    exam_type = Column(Enum(ExamType), default=ExamType.MAIN, nullable=False)
    file_path = Column(String(500), nullable=False)
    checksum = Column(String(64), nullable=False, index=True)
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.PENDING, nullable=False, index=True)
    reviewer_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    submitter = relationship("User", foreign_keys=[user_id], back_populates="submissions")
    subject = relationship("Subject")
    scheme = relationship("AcademicScheme")
    reviews = relationship("PaperReview", back_populates="submission", cascade="all, delete-orphan")


class PaperReview(Base):
    __tablename__ = "paper_reviews"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("paper_submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    decision = Column(Enum(SubmissionStatus), nullable=False)
    remarks = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    submission = relationship("PaperSubmission", back_populates="reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviews")


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)
    document_type = Column(String(50), nullable=False)  # "question_paper", "syllabus"
    document_id = Column(Integer, nullable=False, index=True)
    version_number = Column(Integer, default=1, nullable=False)
    file_path = Column(String(500), nullable=False)
    checksum = Column(String(64), nullable=False)
    changed_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    change_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
