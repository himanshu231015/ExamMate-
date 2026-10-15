"""Study plan schemas."""

from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.study_plan import ConfidenceLevel, PlanStatus


class StudyPlanItemBase(BaseModel):
    topic_id: int
    allocated_hours: float = 1.5
    practice_activity: Optional[str] = None
    scheduled_date: date


class StudyPlanItemUpdate(BaseModel):
    is_completed: bool


class StudyPlanItemResponse(StudyPlanItemBase):
    id: int
    study_plan_id: int
    is_completed: bool
    completed_at: Optional[datetime] = None
    topic_name: Optional[str] = None

    class Config:
        from_attributes = True


class StudyPlanCreate(BaseModel):
    subject_id: int
    title: str = Field(..., min_length=2, max_length=150)
    target_exam_date: date
    daily_hours: float = Field(2.0, ge=0.5, le=12.0)
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM


class StudyPlanResponse(BaseModel):
    id: int
    user_id: int
    subject_id: int
    title: str
    target_exam_date: date
    daily_hours: float
    confidence_level: ConfidenceLevel
    status: PlanStatus
    created_at: datetime
    items: List[StudyPlanItemResponse] = []

    class Config:
        from_attributes = True
