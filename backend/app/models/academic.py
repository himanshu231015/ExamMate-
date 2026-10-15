"""Academic context and syllabus models."""

import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    short_name = Column(String(50), unique=True, nullable=False, index=True)
    state = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    website = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    degrees = relationship("Degree", back_populates="university", cascade="all, delete-orphan")
    schemes = relationship("AcademicScheme", back_populates="university", cascade="all, delete-orphan")


class Degree(Base):
    __tablename__ = "degrees"

    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)  # e.g., "Bachelor of Technology"
    code = Column(String(50), nullable=False)   # e.g., "B.Tech"
    duration_years = Column(Integer, default=4, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    university = relationship("University", back_populates="degrees")
    branches = relationship("Branch", back_populates="degree", cascade="all, delete-orphan")


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    degree_id = Column(Integer, ForeignKey("degrees.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)  # e.g., "Computer Science & Engineering"
    code = Column(String(50), nullable=False, index=True)  # e.g., "CSE" or "AIML"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    degree = relationship("Degree", back_populates="branches")
    subjects = relationship("Subject", back_populates="branch", cascade="all, delete-orphan")


class AcademicScheme(Base):
    __tablename__ = "academic_schemes"

    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)  # e.g., "CBGS 2019", "CBCS 2015"
    code = Column(String(50), nullable=False, index=True)  # e.g., "CBGS"
    start_year = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    university = relationship("University", back_populates="schemes")
    subjects = relationship("Subject", back_populates="scheme", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True)
    scheme_id = Column(Integer, ForeignKey("academic_schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)  # e.g., "Data Structures"
    code = Column(String(50), nullable=False, index=True)  # e.g., "CS-301" or "AL-302"
    semester_number = Column(Integer, nullable=False, index=True)  # 1 to 8
    credits = Column(Integer, default=4, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    branch = relationship("Branch", back_populates="subjects")
    scheme = relationship("AcademicScheme", back_populates="subjects")
    syllabus_documents = relationship("SyllabusDocument", back_populates="subject", cascade="all, delete-orphan")
    units = relationship("SyllabusUnit", back_populates="subject", cascade="all, delete-orphan", order_by="SyllabusUnit.unit_number")
    question_papers = relationship("QuestionPaper", back_populates="subject", cascade="all, delete-orphan")
    study_plans = relationship("StudyPlan", back_populates="subject", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="subject", cascade="all, delete-orphan")


class SyllabusDocument(Base):
    __tablename__ = "syllabus_documents"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    academic_year = Column(String(20), nullable=False)  # e.g., "2023-2024"
    file_path = Column(String(500), nullable=True)
    source_url = Column(String(500), nullable=True)
    checksum = Column(String(64), nullable=True, index=True)
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.VERIFIED, nullable=False)
    raw_text = Column(Text, nullable=True)
    uploaded_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    subject = relationship("Subject", back_populates="syllabus_documents")


class SyllabusUnit(Base):
    __tablename__ = "syllabus_units"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    unit_number = Column(Integer, nullable=False)  # 1 to 5 usually in RGPV
    title = Column(String(255), nullable=False)    # e.g., "Unit I: Introduction to Data Structures"
    description = Column(Text, nullable=True)

    # Relationships
    subject = relationship("Subject", back_populates="units")
    topics = relationship("SyllabusTopic", back_populates="unit", cascade="all, delete-orphan", order_by="SyllabusTopic.id")
    questions = relationship("ExtractedQuestion", back_populates="unit")


class SyllabusTopic(Base):
    __tablename__ = "syllabus_topics"

    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(Integer, ForeignKey("syllabus_units.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_name = Column(String(255), nullable=False, index=True)  # e.g., "Binary Search Trees"
    subtopics = Column(Text, nullable=True)  # Comma separated or detailed JSON/text
    learning_objectives = Column(Text, nullable=True)
    importance_level = Column(String(50), default="high", nullable=False)  # high, medium, low

    # Relationships
    unit = relationship("SyllabusUnit", back_populates="topics")
    questions = relationship("ExtractedQuestion", back_populates="topic")
    study_plan_items = relationship("StudyPlanItem", back_populates="topic")
