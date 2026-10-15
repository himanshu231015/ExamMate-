"""Feedback and error reporting schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.feedback import FeedbackRating, ErrorCategory, ReportStatus


class FeedbackCreate(BaseModel):
    message_id: int
    rating: FeedbackRating
    error_category: Optional[ErrorCategory] = None
    comment: Optional[str] = Field(None, max_length=1000)


class FeedbackResponse(BaseModel):
    id: int
    message_id: int
    user_id: int
    rating: FeedbackRating
    error_category: Optional[ErrorCategory] = None
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ErrorReportCreate(BaseModel):
    report_category: ErrorCategory
    target_type: str  # "question_paper", "pyq", "syllabus_topic", "citation"
    target_id: Optional[int] = None
    description: str = Field(..., min_length=10, max_length=2000)


class ErrorReportResponse(BaseModel):
    id: int
    user_id: int
    report_category: ErrorCategory
    target_type: str
    target_id: Optional[int] = None
    description: str
    status: ReportStatus
    resolution_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
