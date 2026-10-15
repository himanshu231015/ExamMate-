"""Paper submission and review schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.submission import SubmissionStatus
from app.models.question_paper import ExamType, ExamSession


class PaperSubmissionCreate(BaseModel):
    subject_id: int
    scheme_id: int
    exam_year: int
    exam_session: ExamSession
    exam_type: ExamType = ExamType.MAIN


class PaperReviewCreate(BaseModel):
    decision: SubmissionStatus  # APPROVED, REJECTED, RETURNED_FOR_CORRECTION
    remarks: str


class PaperReviewResponse(BaseModel):
    id: int
    submission_id: int
    reviewer_id: int
    decision: SubmissionStatus
    remarks: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaperSubmissionResponse(BaseModel):
    id: int
    user_id: int
    subject_id: int
    scheme_id: int
    exam_year: int
    exam_session: ExamSession
    exam_type: ExamType
    file_path: str
    checksum: str
    status: SubmissionStatus
    reviewer_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    reviews: List[PaperReviewResponse] = []

    class Config:
        from_attributes = True
