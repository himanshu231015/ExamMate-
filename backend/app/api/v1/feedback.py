"""Student feedback and issue reporting API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.chat import ChatMessage
from app.models.feedback import UserFeedback, ErrorReport, ReportStatus
from app.schemas.feedback import (
    FeedbackCreate,
    FeedbackResponse,
    ErrorReportCreate,
    ErrorReportResponse,
)
from app.schemas.common import MessageResponse
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/feedback", tags=["Feedback & Controlled Improvement"])


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    feedback_in: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit helpful/unhelpful rating and error categories for an AI response.
    Feeds into the controlled improvement workflow.
    """
    msg = db.query(ChatMessage).filter(ChatMessage.id == feedback_in.message_id).first()
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat message not found.")

    # Check if feedback already exists for this message by user
    existing = (
        db.query(UserFeedback)
        .filter(UserFeedback.message_id == feedback_in.message_id, UserFeedback.user_id == current_user.id)
        .first()
    )
    if existing:
        existing.rating = feedback_in.rating
        existing.error_category = feedback_in.error_category
        existing.comment = feedback_in.comment
        db.commit()
        db.refresh(existing)
        return existing

    feedback = UserFeedback(
        message_id=feedback_in.message_id,
        user_id=current_user.id,
        rating=feedback_in.rating,
        error_category=feedback_in.error_category,
        comment=feedback_in.comment,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.post("/reports", response_model=ErrorReportResponse, status_code=status.HTTP_201_CREATED)
def submit_error_report(
    report_in: ErrorReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Report incorrect answers, irrelevant PYQs, wrong syllabus mappings,
    unsupported citations, or broken PDF links.
    """
    report = ErrorReport(
        user_id=current_user.id,
        report_category=report_in.report_category,
        target_type=report_in.target_type,
        target_id=report_in.target_id,
        description=report_in.description,
        status=ReportStatus.OPEN,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    log_audit_event(
        db=db,
        action="error_reported",
        entity_type=report_in.target_type,
        entity_id=report_in.target_id,
        user_id=current_user.id,
        details=f"Category: {report_in.report_category.value}. Desc: {report_in.description[:50]}",
    )
    return report


@router.get("/reports", response_model=List[ErrorReportResponse])
def get_reports(
    status_filter: Optional[ReportStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.REVIEWER])),
):
    """Retrieve reported issues for moderation and quality improvement (Admin/Reviewer)."""
    query = db.query(ErrorReport)
    if status_filter:
        query = query.filter(ErrorReport.status == status_filter)
    return query.order_by(ErrorReport.created_at.desc()).all()


@router.patch("/reports/{report_id}", response_model=ErrorReportResponse)
def update_report_status(
    report_id: int,
    status_update: ReportStatus,
    resolution_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Update resolution status and notes for an error report (Admin only)."""
    report = db.query(ErrorReport).filter(ErrorReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

    report.status = status_update
    if resolution_notes:
        report.resolution_notes = resolution_notes
    db.commit()
    db.refresh(report)
    return report
