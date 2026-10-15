"""Question paper and PYQ search schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.academic import VerificationStatus
from app.models.question_paper import ExamType, ExamSession


class ExtractedQuestionBase(BaseModel):
    question_number: int
    sub_question: Optional[str] = None
    question_text: str
    marks: Optional[int] = None
    page_number: int = 1
    confidence_score: float = 1.0
    is_human_verified: bool = True


class ExtractedQuestionCreate(ExtractedQuestionBase):
    paper_id: int
    unit_id: Optional[int] = None
    topic_id: Optional[int] = None


class ExtractedQuestionResponse(ExtractedQuestionBase):
    id: int
    paper_id: int
    unit_id: Optional[int] = None
    topic_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionPaperBase(BaseModel):
    subject_id: int
    scheme_id: int
    exam_year: int
    exam_session: ExamSession
    exam_type: ExamType = ExamType.MAIN
    total_marks: int = 70
    source_url: Optional[str] = None


class QuestionPaperCreate(QuestionPaperBase):
    file_path: Optional[str] = None
    checksum: Optional[str] = None


class QuestionPaperResponse(QuestionPaperBase):
    id: int
    file_path: Optional[str] = None
    checksum: Optional[str] = None
    verification_status: VerificationStatus
    approved_at: Optional[datetime] = None
    created_at: datetime
    questions: List[ExtractedQuestionResponse] = []

    class Config:
        from_attributes = True


class PYQSearchQuery(BaseModel):
    query: Optional[str] = None
    subject_id: Optional[int] = None
    branch_id: Optional[int] = None
    semester_number: Optional[int] = None
    scheme_id: Optional[int] = None
    unit_id: Optional[int] = None
    topic_id: Optional[int] = None
    exam_year: Optional[int] = None
    exam_session: Optional[ExamSession] = None
    marks: Optional[int] = None
    page: int = 1
    page_size: int = 20


class PYQMatchReason(BaseModel):
    strategy: str  # "bm25_keyword", "semantic_vector", "exact_metadata"
    score: float
    matched_term: Optional[str] = None


class PYQSearchResultItem(BaseModel):
    question: ExtractedQuestionResponse
    paper_year: int
    paper_session: ExamSession
    paper_type: ExamType
    subject_code: str
    subject_name: str
    paper_source_url: Optional[str] = None
    unit_title: Optional[str] = None
    topic_name: Optional[str] = None
    match_reasons: List[PYQMatchReason] = []
    combined_score: float = 0.0


class PYQSearchResponse(BaseModel):
    items: List[PYQSearchResultItem]
    total: int
    page: int
    page_size: int
    total_pages: int
