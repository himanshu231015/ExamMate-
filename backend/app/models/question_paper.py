"""Question paper and extracted question models."""

import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.academic import VerificationStatus


class ExamType(str, enum.Enum):
    MAIN = "Main"
    BACKLOG = "Backlog"
    MID_SEM = "Mid-Sem"


class ExamSession(str, enum.Enum):
    DECEMBER = "December"
    JUNE = "June"
    NOVEMBER = "November"
    MAY = "May"


class QuestionPaper(Base):
    __tablename__ = "question_papers"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    scheme_id = Column(Integer, ForeignKey("academic_schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    exam_year = Column(Integer, nullable=False, index=True)  # e.g., 2023
    exam_session = Column(Enum(ExamSession), default=ExamSession.DECEMBER, nullable=False, index=True)
    exam_type = Column(Enum(ExamType), default=ExamType.MAIN, nullable=False)
    file_path = Column(String(500), nullable=True)
    source_url = Column(String(500), nullable=True)
    checksum = Column(String(64), nullable=True, unique=True, index=True)
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.VERIFIED, nullable=False, index=True)
    total_marks = Column(Integer, default=70, nullable=False)
    uploaded_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    subject = relationship("Subject", back_populates="question_papers")
    scheme = relationship("AcademicScheme")
    questions = relationship("ExtractedQuestion", back_populates="paper", cascade="all, delete-orphan", order_by="ExtractedQuestion.question_number")
    uploader = relationship("User", foreign_keys=[uploaded_by_id])
    approver = relationship("User", foreign_keys=[approved_by_id])


class ExtractedQuestion(Base):
    __tablename__ = "extracted_questions"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("question_papers.id", ondelete="CASCADE"), nullable=False, index=True)
    unit_id = Column(Integer, ForeignKey("syllabus_units.id", ondelete="SET NULL"), nullable=True, index=True)
    topic_id = Column(Integer, ForeignKey("syllabus_topics.id", ondelete="SET NULL"), nullable=True, index=True)
    question_number = Column(Integer, nullable=False)  # e.g., 1, 2, 3
    sub_question = Column(String(10), nullable=True)   # e.g., 'a', 'b', '(i)'
    question_text = Column(Text, nullable=False)
    marks = Column(Integer, nullable=True)             # e.g., 2, 7, 14
    page_number = Column(Integer, default=1, nullable=False)
    confidence_score = Column(Float, default=1.0, nullable=False)
    is_human_verified = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    paper = relationship("QuestionPaper", back_populates="questions")
    unit = relationship("SyllabusUnit", back_populates="questions")
    topic = relationship("SyllabusTopic", back_populates="questions")
