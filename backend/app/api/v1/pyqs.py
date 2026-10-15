"""Previous Year Questions (PYQ) Search and Question Paper API routes."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User, UserRole
from app.models.academic import VerificationStatus
from app.models.question_paper import QuestionPaper, ExtractedQuestion, ExamSession
from app.schemas.question_paper import (
    PYQSearchQuery,
    PYQSearchResponse,
    QuestionPaperResponse,
    ExtractedQuestionResponse,
    QuestionPaperCreate,
)
from app.services.pyq_service import PYQSearchEngine

router = APIRouter(prefix="/pyqs", tags=["Previous Year Questions (PYQs)"])


@router.get("/search", response_model=PYQSearchResponse)
def search_pyqs(
    query: Optional[str] = Query(None, description="Keywords to search in question text"),
    subject_id: Optional[int] = Query(None, description="Subject ID"),
    branch_id: Optional[int] = Query(None, description="Branch ID"),
    semester: Optional[int] = Query(None, ge=1, le=8, description="Semester Number"),
    scheme_id: Optional[int] = Query(None, description="Academic Scheme ID"),
    unit_id: Optional[int] = Query(None, description="Syllabus Unit ID"),
    topic_id: Optional[int] = Query(None, description="Syllabus Topic ID"),
    year: Optional[int] = Query(None, description="Exam Year (e.g. 2023)"),
    session: Optional[ExamSession] = Query(None, description="Exam Session (e.g. December, June)"),
    marks: Optional[int] = Query(None, description="Marks (e.g. 2, 7, 14)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Search historical university question papers using hybrid BM25 and academic filters.
    Only verified questions from approved papers are returned.
    """
    search_params = PYQSearchQuery(
        query=query,
        subject_id=subject_id,
        branch_id=branch_id,
        semester_number=semester,
        scheme_id=scheme_id,
        unit_id=unit_id,
        topic_id=topic_id,
        exam_year=year,
        exam_session=session,
        marks=marks,
        page=page,
        page_size=page_size,
    )
    engine = PYQSearchEngine(db=db)
    return engine.search(search_params)


@router.get("/{question_id}", response_model=ExtractedQuestionResponse)
def get_question_detail(question_id: int, db: Session = Depends(get_db)):
    """Retrieve an individual extracted question with verification status."""
    question = (
        db.query(ExtractedQuestion)
        .join(QuestionPaper, ExtractedQuestion.paper_id == QuestionPaper.id)
        .filter(
            ExtractedQuestion.id == question_id,
            QuestionPaper.verification_status == VerificationStatus.VERIFIED,
            ExtractedQuestion.is_human_verified == True,
        )
        .first()
    )
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found or not yet verified."
        )
    return question


@router.get("/papers/{paper_id}", response_model=QuestionPaperResponse)
def get_question_paper(paper_id: int, db: Session = Depends(get_db)):
    """Retrieve full question paper metadata, verified PDF link, and all extracted questions."""
    paper = (
        db.query(QuestionPaper)
        .filter(
            QuestionPaper.id == paper_id,
            QuestionPaper.verification_status == VerificationStatus.VERIFIED,
        )
        .first()
    )
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question Paper with ID {paper_id} not found or not yet approved."
        )
    return paper
