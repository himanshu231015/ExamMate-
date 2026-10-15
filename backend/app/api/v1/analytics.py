"""Historical topic analytics and administrative dashboard metrics."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User, UserRole
from app.models.academic import Subject, University, VerificationStatus
from app.models.question_paper import QuestionPaper, ExtractedQuestion
from app.models.submission import PaperSubmission, SubmissionStatus
from app.models.feedback import UserFeedback, ErrorReport
from app.models.chat import ChatMessage
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics & Topic Prioritization"])


@router.get("/topics/{subject_id}")
def get_historical_topic_analytics(subject_id: int, db: Session = Depends(get_db)):
    """
    Get historical appearance frequencies, marks distribution, and syllabus coverage
    for all topics under a subject.
    Transparently explains that frequency != future exam certainty.
    """
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found.")

    analytics_service = AnalyticsService(db=db)
    return analytics_service.get_topic_analytics(subject_id=subject_id)


@router.get("/backtest/{subject_id}")
def run_topic_backtest(
    subject_id: int,
    target_year: int = Query(2023, description="Target exam year to evaluate against"),
    k: int = Query(5, ge=1, le=20, description="Top K ranked topics"),
    db: Session = Depends(get_db),
):
    """
    Run chronological backtesting:
    Evaluates topic rankings derived strictly from prior papers against actual questions
    in the target exam year to compute Precision@K and Recall@K.
    """
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found.")

    analytics_service = AnalyticsService(db=db)
    return analytics_service.run_chronological_backtest(
        subject_id=subject_id,
        target_year=target_year,
        k=k,
    )


@router.get("/admin/summary")
def get_admin_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """System analytics for administrator overview."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_subjects = db.query(func.count(Subject.id)).scalar() or 0
    verified_papers = db.query(func.count(QuestionPaper.id)).filter(QuestionPaper.verification_status == VerificationStatus.VERIFIED).scalar() or 0
    verified_questions = db.query(func.count(ExtractedQuestion.id)).filter(ExtractedQuestion.is_human_verified == True).scalar() or 0
    pending_submissions = db.query(func.count(PaperSubmission.id)).filter(PaperSubmission.status == SubmissionStatus.PENDING).scalar() or 0
    total_feedbacks = db.query(func.count(UserFeedback.id)).scalar() or 0
    open_reports = db.query(func.count(ErrorReport.id)).filter(ErrorReport.status == "open").scalar() or 0
    total_chat_messages = db.query(func.count(ChatMessage.id)).scalar() or 0

    return {
        "total_users": total_users,
        "total_subjects": total_subjects,
        "verified_papers": verified_papers,
        "verified_questions": verified_questions,
        "pending_submissions": pending_submissions,
        "total_feedbacks": total_feedbacks,
        "open_reports": open_reports,
        "total_chat_messages": total_chat_messages,
    }
