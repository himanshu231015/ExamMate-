"""AI tutor chat and citation schemas."""

from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class CitationResponse(BaseModel):
    id: Optional[int] = None
    source_type: str
    source_id: Optional[int] = None
    document_title: str
    university_name: str = "RGPV"
    subject_code: Optional[str] = None
    unit_number: Optional[int] = None
    exam_year: Optional[int] = None
    exam_session: Optional[str] = None
    page_number: Optional[int] = None
    question_number: Optional[str] = None
    source_url: Optional[str] = None

    class Config:
        from_attributes = True


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    intent_classification: Optional[str] = None
    is_within_scope: bool
    created_at: datetime
    citations: List[CitationResponse] = []

    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    id: int
    user_id: int
    subject_id: int
    title: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    session_id: Optional[int] = None
    subject_id: int
    message: str = Field(..., min_length=2, max_length=2000)
    answer_format: Optional[str] = Field(
        default="explanation",
        description="Format: '2_mark', '7_mark', '14_mark', 'explanation', 'step_by_step', 'revision_notes', 'comparison'"
    )


class ChatResponse(BaseModel):
    session_id: int
    message_id: int
    reply: str
    is_within_scope: bool
    intent: str
    citations: List[CitationResponse] = []
    related_pyqs: List[Dict[str, Any]] = []
    latency_ms: float = 0.0
