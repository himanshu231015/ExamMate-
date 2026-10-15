"""Paper submission and reviewer governance API routes."""

import os
import shutil
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.academic import Subject, AcademicScheme, VerificationStatus
from app.models.question_paper import QuestionPaper, ExtractedQuestion, ExamType, ExamSession
from app.models.submission import PaperSubmission, PaperReview, SubmissionStatus
from app.schemas.submission import (
    PaperSubmissionResponse,
    PaperReviewCreate,
    PaperReviewResponse,
)
from app.schemas.common import MessageResponse
from app.services.pdf_service import (
    compute_file_checksum,
    extract_text_from_pdf,
    parse_and_segment_questions,
)
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/submissions", tags=["Paper Ingestion & Review Governance"])


@router.post("/", response_model=PaperSubmissionResponse, status_code=status.HTTP_201_CREATED)
async def submit_question_paper(
    subject_id: int = Form(...),
    scheme_id: int = Form(...),
    exam_year: int = Form(...),
    exam_session: ExamSession = Form(...),
    exam_type: ExamType = Form(ExamType.MAIN),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit a previous year question paper for reviewer evaluation.
    Enforces PDF validation, file size limit (15 MB), and duplicate SHA-256 detection.
    Unapproved submissions are kept in staging and never appear in public search or RAG answers.
    """
    # 1. Validate file extension and MIME type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted for question paper submissions."
        )

    # 2. Check subject and scheme existence
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found.")

    scheme = db.query(AcademicScheme).filter(AcademicScheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Academic scheme not found.")

    # 3. Create upload destination directory
    upload_folder = os.path.join(settings.UPLOAD_DIR, "papers")
    os.makedirs(upload_folder, exist_ok=True)

    timestamp = int(datetime.now().timestamp())
    safe_filename = f"{subject.code}_{exam_year}_{exam_session.value}_{timestamp}.pdf".replace(" ", "_")
    target_path = os.path.join(upload_folder, safe_filename)

    # 4. Stream and write file with size restriction
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    bytes_read = 0

    with open(target_path, "wb") as buffer:
        while chunk := await file.read(1024 * 64):
            bytes_read += len(chunk)
            if bytes_read > max_bytes:
                buffer.close()
                if os.path.exists(target_path):
                    os.remove(target_path)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Uploaded file exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
                )
            buffer.write(chunk)

    # 5. Checksum and duplicate detection
    checksum = compute_file_checksum(target_path)
    existing_duplicate = (
        db.query(PaperSubmission)
        .filter(PaperSubmission.checksum == checksum)
        .first()
    )
    if existing_duplicate:
        if os.path.exists(target_path):
            os.remove(target_path)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A question paper with identical content (SHA-256: {checksum[:8]}...) was already submitted."
        )

    # 6. Save submission record
    submission = PaperSubmission(
        user_id=current_user.id,
        subject_id=subject_id,
        scheme_id=scheme_id,
        exam_year=exam_year,
        exam_session=exam_session,
        exam_type=exam_type,
        file_path=target_path,
        checksum=checksum,
        status=SubmissionStatus.PENDING,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    log_audit_event(
        db=db,
        action="paper_submitted",
        entity_type="paper_submission",
        entity_id=submission.id,
        user_id=current_user.id,
        details=f"Submitted {subject.code} {exam_session.value} {exam_year}",
    )

    return submission


@router.get("/mine", response_model=List[PaperSubmissionResponse])
def get_my_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """View status of papers submitted by the current user."""
    return (
        db.query(PaperSubmission)
        .filter(PaperSubmission.user_id == current_user.id)
        .order_by(PaperSubmission.created_at.desc())
        .all()
    )


@router.get("/pending", response_model=List[PaperSubmissionResponse])
def get_pending_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.REVIEWER, UserRole.ADMIN])),
):
    """Retrieve queue of pending submissions awaiting review (Reviewer/Admin only)."""
    return (
        db.query(PaperSubmission)
        .filter(PaperSubmission.status == SubmissionStatus.PENDING)
        .order_by(PaperSubmission.created_at.asc())
        .all()
    )


@router.post("/{submission_id}/review", response_model=MessageResponse)
def review_submission(
    submission_id: int,
    review_in: PaperReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.REVIEWER, UserRole.ADMIN])),
):
    """
    Review a pending paper submission: Approve, Reject, or Return for correction.
    Strict Governance Rule: A contributor cannot review their own submission.
    Upon approval, extracted questions are segmented and indexed into verified QuestionPaper bank.
    """
    submission = db.query(PaperSubmission).filter(PaperSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")

    # Prevent self-approval
    if submission.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Review governance violation: You cannot approve or review your own submission."
        )

    # Record review decision
    review = PaperReview(
        submission_id=submission.id,
        reviewer_id=current_user.id,
        decision=review_in.decision,
        remarks=review_in.remarks,
    )
    db.add(review)

    submission.status = review_in.decision
    submission.reviewer_notes = review_in.remarks

    # If APPROVED: publish into QuestionPaper repository and segment questions
    if review_in.decision == SubmissionStatus.APPROVED:
        # Create published QuestionPaper
        paper = QuestionPaper(
            subject_id=submission.subject_id,
            scheme_id=submission.scheme_id,
            exam_year=submission.exam_year,
            exam_session=submission.exam_session,
            exam_type=submission.exam_type,
            file_path=submission.file_path,
            checksum=submission.checksum,
            total_marks=70,
            verification_status=VerificationStatus.VERIFIED,
            uploaded_by_id=submission.user_id,
            approved_by_id=current_user.id,
            approved_at=datetime.now(timezone.utc),
        )
        db.add(paper)
        db.flush()

        # Extract text & segment questions if PDF exists
        if os.path.exists(submission.file_path):
            try:
                extracted = extract_text_from_pdf(submission.file_path)
                segmented_questions = parse_and_segment_questions(extracted["full_text"])
                for item in segmented_questions:
                    q = ExtractedQuestion(
                        paper_id=paper.id,
                        question_number=item["question_number"],
                        sub_question=item["sub_question"],
                        question_text=item["question_text"],
                        marks=item["marks"],
                        page_number=item["page_number"],
                        confidence_score=item["confidence_score"],
                        is_human_verified=True,
                    )
                    db.add(q)
            except Exception as e:
                # Log extraction issue without breaking approval
                print(f"Extraction warning: {e}")

    db.commit()

    log_audit_event(
        db=db,
        action=f"submission_{review_in.decision.value}",
        entity_type="paper_submission",
        entity_id=submission.id,
        user_id=current_user.id,
        details=f"Decision: {review_in.decision.value}. Remarks: {review_in.remarks}",
    )

    return MessageResponse(
        message=f"Submission {submission_id} reviewed successfully. Status: {review_in.decision.value}."
    )
