"""Personalized study plan and study item models."""

import enum
from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base


class ConfidenceLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PlanStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    target_exam_date = Column(Date, nullable=False)
    daily_hours = Column(Float, default=2.0, nullable=False)
    confidence_level = Column(Enum(ConfidenceLevel), default=ConfidenceLevel.MEDIUM, nullable=False)
    status = Column(Enum(PlanStatus), default=PlanStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="study_plans")
    subject = relationship("Subject", back_populates="study_plans")
    items = relationship("StudyPlanItem", back_populates="study_plan", cascade="all, delete-orphan", order_by="StudyPlanItem.scheduled_date")


class StudyPlanItem(Base):
    __tablename__ = "study_plan_items"

    id = Column(Integer, primary_key=True, index=True)
    study_plan_id = Column(Integer, ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("syllabus_topics.id", ondelete="CASCADE"), nullable=False, index=True)
    allocated_hours = Column(Float, default=1.5, nullable=False)
    practice_activity = Column(Text, nullable=True)  # e.g., "Solve 2023 Dec 7-mark question on AVL trees"
    scheduled_date = Column(Date, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    study_plan = relationship("StudyPlan", back_populates="items")
    topic = relationship("SyllabusTopic", back_populates="study_plan_items")
