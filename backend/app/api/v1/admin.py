"""Admin Governance, Moderation, Analytics, and User Management API routes."""

import io
import csv
import os
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User, UserRole
from app.models.academic import (
    Subject,
    AcademicScheme,
    Branch,
    SyllabusUnit,
    SyllabusTopic,
    VerificationStatus,
)
from app.models.question_paper import (
    QuestionPaper,
    ExtractedQuestion,
    ExamType,
    ExamSession,
)
from app.models.submission import (
    PaperSubmission,
    PaperReview,
    SubmissionStatus,
)
from app.models.announcement import Announcement
from app.models.audit import AuditLog
from app.schemas.admin import (
    UserRoleUpdate,
    UserStatusUpdate,
    ReviewerAssignmentRequest,
    ModerationResolveRequest,
    PaperPublishRequest,
    SubjectCreate,
    SubjectUpdate,
    AnnouncementCreate,
    AnnouncementResponse,
    AdminOverviewMetrics,
    AdminUserListItem,
    ContributorStatsItem,
    ReviewerStatsItem,
    SyllabusCoverageItem,
)
from app.schemas.common import MessageResponse
from app.services.audit_service import log_audit_event
from app.services.pdf_service import extract_text_from_pdf, parse_and_segment_questions

router = APIRouter(prefix="/admin", tags=["Admin Console & Governance"])


# =========================================================================
# 1. OVERVIEW & METRICS
# =========================================================================

@router.get("/overview", response_model=AdminOverviewMetrics)
def get_admin_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Real-time database-calculated platform metrics and recent activity."""
    total_users = db.query(User).count()
    active_students = (
        db.query(User)
        .filter(User.role == UserRole.STUDENT, User.is_active == True)
        .count()
    )
    total_contributors = db.query(User).filter(User.role == UserRole.CONTRIBUTOR).count()
    total_reviewers = db.query(User).filter(User.role == UserRole.REVIEWER).count()
    pending_submissions = (
        db.query(PaperSubmission)
        .filter(PaperSubmission.status == SubmissionStatus.PENDING)
        .count()
    )
    approved_papers = (
        db.query(QuestionPaper)
        .filter(QuestionPaper.verification_status == VerificationStatus.VERIFIED)
        .count()
    )
    verified_questions = (
        db.query(ExtractedQuestion)
        .filter(ExtractedQuestion.is_human_verified == True)
        .count()
    )
    flagged_submissions = (
        db.query(PaperSubmission)
        .filter(
            or_(
                PaperSubmission.status == SubmissionStatus.FLAGGED,
                PaperSubmission.is_flagged == True,
            )
        )
        .count()
    )
    rejected_submissions = (
        db.query(PaperSubmission)
        .filter(PaperSubmission.status == SubmissionStatus.REJECTED)
        .count()
    )
    total_subjects = db.query(Subject).count()
    total_units = db.query(SyllabusUnit).count()

    recent_logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(10)
        .all()
    )
    recent_activity = [
        {
            "id": log.id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "details": log.details,
            "created_at": log.created_at.isoformat(),
            "user_id": log.user_id,
        }
        for log in recent_logs
    ]

    return AdminOverviewMetrics(
        total_users=total_users,
        active_students=active_students,
        total_contributors=total_contributors,
        total_reviewers=total_reviewers,
        pending_submissions=pending_submissions,
        approved_papers=approved_papers,
        verified_questions=verified_questions,
        flagged_submissions=flagged_submissions,
        rejected_submissions=rejected_submissions,
        total_subjects=total_subjects,
        total_units=total_units,
        recent_activity=recent_activity,
    )


# =========================================================================
# 2. USER MANAGEMENT
# =========================================================================

@router.get("/users", response_model=List[AdminUserListItem])
def list_users(
    search: Optional[str] = Query(None, description="Search by name or email"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by account status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Searchable, filterable list of all registered users."""
    query = db.query(User)
    if search:
        search_fmt = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(User.full_name).like(search_fmt),
                func.lower(User.email).like(search_fmt),
            )
        )
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    users = query.order_by(User.id.asc()).all()

    # Calculate submission and review counts per user
    result = []
    for u in users:
        sub_count = db.query(PaperSubmission).filter(PaperSubmission.user_id == u.id).count()
        rev_count = db.query(PaperReview).filter(PaperReview.reviewer_id == u.id).count()
        result.append(
            AdminUserListItem(
                id=u.id,
                email=u.email,
                full_name=u.full_name,
                role=u.role.value,
                is_active=u.is_active,
                created_at=u.created_at,
                submissions_count=sub_count,
                reviews_count=rev_count,
            )
        )
    return result


@router.get("/users/{user_id}")
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Retrieve detailed user profile, submissions, and review history."""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    submissions = (
        db.query(PaperSubmission)
        .filter(PaperSubmission.user_id == user_id)
        .order_by(PaperSubmission.created_at.desc())
        .all()
    )
    reviews = (
        db.query(PaperReview)
        .filter(PaperReview.reviewer_id == user_id)
        .order_by(PaperReview.created_at.desc())
        .all()
    )

    return {
        "id": target_user.id,
        "email": target_user.email,
        "full_name": target_user.full_name,
        "role": target_user.role.value,
        "is_active": target_user.is_active,
        "created_at": target_user.created_at.isoformat(),
        "submissions": [
            {
                "id": s.id,
                "exam_year": s.exam_year,
                "status": s.status.value,
                "created_at": s.created_at.isoformat(),
            }
            for s in submissions
        ],
        "reviews": [
            {
                "id": r.id,
                "submission_id": r.submission_id,
                "decision": r.decision.value,
                "remarks": r.remarks,
                "created_at": r.created_at.isoformat(),
            }
            for r in reviews
        ],
    }


@router.patch("/users/{user_id}/role", response_model=MessageResponse)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """
    Update a user's role.
    Security Guard: Prevents demoting or removing the last active administrator.
    """
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    # Last active admin protection
    if target_user.role == UserRole.ADMIN and payload.role != UserRole.ADMIN:
        other_admins_count = (
            db.query(User)
            .filter(User.role == UserRole.ADMIN, User.is_active == True, User.id != user_id)
            .count()
        )
        if other_admins_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security protection: Cannot demote the last active administrator.",
            )

    old_role = target_user.role.value
    target_user.role = payload.role
    db.commit()

    log_audit_event(
        db=db,
        action="user_role_changed",
        entity_type="user",
        entity_id=target_user.id,
        user_id=current_user.id,
        details=f"Changed role of user {target_user.email} from {old_role} to {payload.role.value}",
    )

    return MessageResponse(
        message=f"Role for user {target_user.email} updated to {payload.role.value} successfully."
    )


@router.patch("/users/{user_id}/status", response_model=MessageResponse)
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """
    Activate or deactivate a user account.
    Security Guard: Admins cannot deactivate their own account or deactivate the last admin.
    """
    if current_user.id == user_id and not payload.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security protection: Administrators cannot deactivate their own account.",
        )

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if target_user.role == UserRole.ADMIN and not payload.is_active:
        other_admins_count = (
            db.query(User)
            .filter(User.role == UserRole.ADMIN, User.is_active == True, User.id != user_id)
            .count()
        )
        if other_admins_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security protection: Cannot deactivate the last active administrator.",
            )

    target_user.is_active = payload.is_active
    db.commit()

    status_str = "activated" if payload.is_active else "deactivated"
    log_audit_event(
        db=db,
        action=f"user_{status_str}",
        entity_type="user",
        entity_id=target_user.id,
        user_id=current_user.id,
        details=f"Account status of user {target_user.email} set to {status_str}",
    )

    return MessageResponse(
        message=f"User {target_user.email} account {status_str} successfully."
    )


# =========================================================================
# 3. CONTRIBUTOR & REVIEWER WORKLOAD MANAGEMENT
# =========================================================================

@router.get("/contributors", response_model=List[ContributorStatsItem])
def list_contributors(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """List all contributors with their submission metrics and quality scores."""
    contributors = db.query(User).filter(User.role == UserRole.CONTRIBUTOR).all()
    result = []
    for c in contributors:
        total = db.query(PaperSubmission).filter(PaperSubmission.user_id == c.id).count()
        approved = (
            db.query(PaperSubmission)
            .filter(PaperSubmission.user_id == c.id, PaperSubmission.status == SubmissionStatus.APPROVED)
            .count()
        )
        rejected = (
            db.query(PaperSubmission)
            .filter(PaperSubmission.user_id == c.id, PaperSubmission.status == SubmissionStatus.REJECTED)
            .count()
        )
        pending = (
            db.query(PaperSubmission)
            .filter(PaperSubmission.user_id == c.id, PaperSubmission.status == SubmissionStatus.PENDING)
            .count()
        )
        decided = approved + rejected
        quality = round((approved / decided * 100), 1) if decided > 0 else 100.0

        result.append(
            ContributorStatsItem(
                user_id=c.id,
                full_name=c.full_name,
                email=c.email,
                total_submissions=total,
                approved=approved,
                rejected=rejected,
                pending=pending,
                quality_score=quality,
            )
        )
    return result


@router.get("/reviewers", response_model=List[ReviewerStatsItem])
def list_reviewers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """List reviewers with assigned workloads and completion stats."""
    reviewers = db.query(User).filter(User.role.in_([UserRole.REVIEWER, UserRole.ADMIN])).all()
    result = []
    for r in reviewers:
        assigned_pending = (
            db.query(PaperSubmission)
            .filter(
                PaperSubmission.assigned_reviewer_id == r.id,
                PaperSubmission.status.in_([SubmissionStatus.PENDING, SubmissionStatus.IN_REVIEW]),
            )
            .count()
        )
        completed = (
            db.query(PaperReview)
            .filter(PaperReview.reviewer_id == r.id)
            .count()
        )
        result.append(
            ReviewerStatsItem(
                user_id=r.id,
                full_name=r.full_name,
                email=r.email,
                is_active=r.is_active,
                assigned_pending=assigned_pending,
                completed_reviews=completed,
            )
        )
    return result


@router.post("/reviews/assignments", response_model=MessageResponse)
def assign_reviewer(
    payload: ReviewerAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Assign or reassign a submission to an authorized reviewer."""
    submission = db.query(PaperSubmission).filter(PaperSubmission.id == payload.submission_id).first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")

    reviewer = db.query(User).filter(User.id == payload.reviewer_id).first()
    if not reviewer or reviewer.role not in [UserRole.REVIEWER, UserRole.ADMIN] or not reviewer.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target user is not an active reviewer or admin.",
        )

    # Governance rule: cannot assign to submitter
    if submission.user_id == reviewer.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Governance conflict: Submitter cannot be assigned as the reviewer.",
        )

    submission.assigned_reviewer_id = reviewer.id
    if submission.status == SubmissionStatus.PENDING:
        submission.status = SubmissionStatus.IN_REVIEW
    db.commit()

    log_audit_event(
        db=db,
        action="reviewer_assigned",
        entity_type="paper_submission",
        entity_id=submission.id,
        user_id=current_user.id,
        details=f"Assigned submission {submission.id} to reviewer {reviewer.email}",
    )

    return MessageResponse(
        message=f"Submission {submission.id} successfully assigned to reviewer {reviewer.full_name}."
    )


# =========================================================================
# 4. QUESTION BANK & PUBLISHING MANAGEMENT
# =========================================================================

@router.get("/question-papers")
def list_question_papers(
    subject_id: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    is_published: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Centralized question bank manager listing all papers, verification, and publication state."""
    query = db.query(QuestionPaper)
    if subject_id:
        query = query.filter(QuestionPaper.subject_id == subject_id)
    if year:
        query = query.filter(QuestionPaper.exam_year == year)
    if is_published is not None:
        query = query.filter(QuestionPaper.is_published == is_published)

    papers = query.order_by(QuestionPaper.exam_year.desc()).all()
    result = []
    for p in papers:
        q_count = db.query(ExtractedQuestion).filter(ExtractedQuestion.paper_id == p.id).count()
        subj = db.query(Subject).filter(Subject.id == p.subject_id).first()
        result.append({
            "id": p.id,
            "subject_id": p.subject_id,
            "subject_code": subj.code if subj else "N/A",
            "subject_name": subj.name if subj else "N/A",
            "exam_year": p.exam_year,
            "exam_session": p.exam_session.value,
            "exam_type": p.exam_type.value,
            "total_marks": p.total_marks,
            "verification_status": p.verification_status.value,
            "is_published": p.is_published,
            "checksum": p.checksum,
            "questions_count": q_count,
            "created_at": p.created_at.isoformat(),
        })
    return result


@router.post("/question-papers/{paper_id}/publish", response_model=MessageResponse)
def publish_question_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Publish a question paper so it appears in student search and AI retrieval."""
    paper = db.query(QuestionPaper).filter(QuestionPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question paper not found.")

    paper.is_published = True
    paper.verification_status = VerificationStatus.VERIFIED
    db.commit()

    log_audit_event(
        db=db,
        action="paper_published",
        entity_type="question_paper",
        entity_id=paper.id,
        user_id=current_user.id,
        details=f"Question paper ID {paper.id} published to student portal.",
    )

    return MessageResponse(message=f"Question paper {paper_id} has been published successfully.")


@router.post("/question-papers/{paper_id}/unpublish", response_model=MessageResponse)
def unpublish_question_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Unpublish a paper to immediately remove it from all student-facing searches and AI RAG."""
    paper = db.query(QuestionPaper).filter(QuestionPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question paper not found.")

    paper.is_published = False
    db.commit()

    log_audit_event(
        db=db,
        action="paper_unpublished",
        entity_type="question_paper",
        entity_id=paper.id,
        user_id=current_user.id,
        details=f"Question paper ID {paper.id} unpublished from student portal.",
    )

    return MessageResponse(message=f"Question paper {paper_id} has been unpublished successfully.")


# =========================================================================
# 5. ACADEMIC & SYLLABUS MANAGEMENT
# =========================================================================

@router.get("/subjects")
def list_admin_subjects(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """List all subjects with linked papers and unit counts."""
    subjects = db.query(Subject).order_by(Subject.semester_number.asc(), Subject.code.asc()).all()
    result = []
    for s in subjects:
        paper_count = db.query(QuestionPaper).filter(QuestionPaper.subject_id == s.id).count()
        unit_count = db.query(SyllabusUnit).filter(SyllabusUnit.subject_id == s.id).count()
        branch = db.query(Branch).filter(Branch.id == s.branch_id).first()
        result.append({
            "id": s.id,
            "name": s.name,
            "code": s.code,
            "semester_number": s.semester_number,
            "credits": s.credits,
            "branch_code": branch.code if branch else "N/A",
            "branch_name": branch.name if branch else "N/A",
            "linked_papers": paper_count,
            "syllabus_units": unit_count,
        })
    return result


@router.post("/subjects", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_subject(
    payload: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Create a new university subject with duplicate code validation."""
    existing = db.query(Subject).filter(Subject.code == payload.code.upper().strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A subject with code '{payload.code.upper().strip()}' already exists ({existing.name})."
        )

    new_subject = Subject(
        name=payload.name.strip(),
        code=payload.code.upper().strip(),
        branch_id=payload.branch_id,
        scheme_id=payload.scheme_id,
        semester_number=payload.semester_number,
        credits=payload.credits,
        description=payload.description,
    )
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)

    log_audit_event(
        db=db,
        action="subject_created",
        entity_type="subject",
        entity_id=new_subject.id,
        user_id=current_user.id,
        details=f"Created subject {new_subject.code} - {new_subject.name}",
    )

    return MessageResponse(message=f"Subject {new_subject.code} created successfully.")


@router.patch("/subjects/{subject_id}", response_model=MessageResponse)
def update_subject(
    subject_id: int,
    payload: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Update subject details."""
    subj = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found.")

    if payload.name:
        subj.name = payload.name.strip()
    if payload.code:
        subj.code = payload.code.upper().strip()
    if payload.semester_number is not None:
        subj.semester_number = payload.semester_number
    if payload.credits is not None:
        subj.credits = payload.credits
    if payload.description is not None:
        subj.description = payload.description

    db.commit()

    log_audit_event(
        db=db,
        action="subject_updated",
        entity_type="subject",
        entity_id=subj.id,
        user_id=current_user.id,
        details=f"Updated subject {subj.code}",
    )

    return MessageResponse(message=f"Subject {subj.code} updated successfully.")


@router.get("/syllabus/coverage", response_model=List[SyllabusCoverageItem])
def get_syllabus_coverage(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Analyze subject-wise syllabus coverage and missing units/topics."""
    subjects = db.query(Subject).order_by(Subject.semester_number.asc()).all()
    result = []
    for s in subjects:
        units = db.query(SyllabusUnit).filter(SyllabusUnit.subject_id == s.id).all()
        topics_count = (
            db.query(SyllabusTopic)
            .join(SyllabusUnit, SyllabusTopic.unit_id == SyllabusUnit.id)
            .filter(SyllabusUnit.subject_id == s.id)
            .count()
        )
        papers_count = db.query(QuestionPaper).filter(QuestionPaper.subject_id == s.id).count()
        is_complete = len(units) >= 5

        result.append(
            SyllabusCoverageItem(
                subject_id=s.id,
                subject_code=s.code,
                subject_name=s.name,
                semester=s.semester_number,
                units_count=len(units),
                topics_count=topics_count,
                papers_count=papers_count,
                is_complete=is_complete,
            )
        )
    return result


# =========================================================================
# 6. MODERATION & DISPUTES
# =========================================================================

@router.get("/moderation/queue")
def get_moderation_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Retrieve submissions requiring administrative moderation or dispute resolution."""
    submissions = (
        db.query(PaperSubmission)
        .filter(
            or_(
                PaperSubmission.status.in_([
                    SubmissionStatus.PENDING,
                    SubmissionStatus.IN_REVIEW,
                    SubmissionStatus.FLAGGED,
                    SubmissionStatus.RETURNED_FOR_CORRECTION,
                ]),
                PaperSubmission.is_flagged == True,
            )
        )
        .order_by(PaperSubmission.created_at.desc())
        .all()
    )
    result = []
    for s in submissions:
        subj = db.query(Subject).filter(Subject.id == s.subject_id).first()
        submitter = db.query(User).filter(User.id == s.user_id).first()
        reviewer = db.query(User).filter(User.id == s.assigned_reviewer_id).first() if s.assigned_reviewer_id else None
        result.append({
            "id": s.id,
            "subject_code": subj.code if subj else "N/A",
            "subject_name": subj.name if subj else "N/A",
            "exam_year": s.exam_year,
            "exam_session": s.exam_session.value,
            "status": s.status.value,
            "is_flagged": s.is_flagged,
            "flag_reason": s.flag_reason,
            "dispute_reason": s.dispute_reason,
            "reviewer_notes": s.reviewer_notes,
            "submitter_name": submitter.full_name if submitter else "Unknown",
            "submitter_email": submitter.email if submitter else "N/A",
            "assigned_reviewer": reviewer.full_name if reviewer else "Unassigned",
            "checksum": s.checksum,
            "file_path": s.file_path,
            "created_at": s.created_at.isoformat(),
        })
    return result


@router.post("/moderation/{submission_id}/resolve", response_model=MessageResponse)
def resolve_moderation(
    submission_id: int,
    payload: ModerationResolveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """
    Administrative override or dispute resolution for a submission.
    Requires mandatory reason and creates an immutable audit trail.
    """
    submission = db.query(PaperSubmission).filter(PaperSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")

    action_lower = payload.action.strip().lower()

    if action_lower == "approve":
        submission.status = SubmissionStatus.APPROVED
        submission.is_flagged = False
        submission.reviewer_notes = payload.reason

        # Ensure question paper is published
        existing_paper = db.query(QuestionPaper).filter(QuestionPaper.checksum == submission.checksum).first()
        if not existing_paper:
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
                is_published=True,
                uploaded_by_id=submission.user_id,
                approved_by_id=current_user.id,
                approved_at=datetime.now(timezone.utc),
            )
            db.add(paper)
            db.flush()

            if os.path.exists(submission.file_path):
                try:
                    extracted = extract_text_from_pdf(submission.file_path)
                    questions = parse_and_segment_questions(extracted["full_text"])
                    for item in questions:
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
                    print(f"Extraction notice: {e}")
        else:
            existing_paper.is_published = True
            existing_paper.verification_status = VerificationStatus.VERIFIED

    elif action_lower == "reject":
        submission.status = SubmissionStatus.REJECTED
        submission.is_flagged = False
        submission.reviewer_notes = payload.reason

    elif action_lower == "return_for_correction":
        submission.status = SubmissionStatus.RETURNED_FOR_CORRECTION
        submission.reviewer_notes = payload.reason

    elif action_lower == "flag":
        submission.status = SubmissionStatus.FLAGGED
        submission.is_flagged = True
        submission.flag_reason = payload.reason

    elif action_lower == "unflag":
        submission.is_flagged = False
        submission.status = SubmissionStatus.PENDING

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action '{payload.action}'. Supported: approve, reject, return_for_correction, flag, unflag.",
        )

    db.commit()

    log_audit_event(
        db=db,
        action=f"moderation_resolved_{action_lower}",
        entity_type="paper_submission",
        entity_id=submission.id,
        user_id=current_user.id,
        details=f"Admin override '{action_lower}'. Reason: {payload.reason}",
    )

    return MessageResponse(
        message=f"Submission {submission_id} moderated successfully with action '{action_lower}'."
    )


# =========================================================================
# 7. ANALYTICS & CSV EXPORT
# =========================================================================

@router.get("/analytics/overview")
def get_platform_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Platform growth, status breakdown, and curriculum distribution analytics."""
    # User roles breakdown
    roles_count = {
        role.value: db.query(User).filter(User.role == role).count()
        for role in UserRole
    }

    # Submission status breakdown
    statuses_count = {
        s.value: db.query(PaperSubmission).filter(PaperSubmission.status == s).count()
        for s in SubmissionStatus
    }

    # Branch-wise question papers
    branches = db.query(Branch).all()
    branch_data = []
    for b in branches:
        paper_count = (
            db.query(QuestionPaper)
            .join(Subject, QuestionPaper.subject_id == Subject.id)
            .filter(Subject.branch_id == b.id)
            .count()
        )
        branch_data.append({"branch_code": b.code, "branch_name": b.name, "papers_count": paper_count})

    return {
        "user_roles": roles_count,
        "submission_statuses": statuses_count,
        "branch_distribution": branch_data,
        "total_papers": db.query(QuestionPaper).count(),
        "total_questions": db.query(ExtractedQuestion).count(),
    }


@router.get("/analytics/export")
def export_platform_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Generate and export a CSV summary of platform users and submissions."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["RGPV ExamMate - Platform Administration Report"])
    writer.writerow(["Generated At", datetime.now(timezone.utc).isoformat()])
    writer.writerow(["Generated By", f"{current_user.full_name} ({current_user.email})"])
    writer.writerow([])

    # Users summary
    writer.writerow(["User ID", "Name", "Email", "Role", "Active", "Registered Date"])
    users = db.query(User).order_by(User.id.asc()).all()
    for u in users:
        writer.writerow([u.id, u.full_name, u.email, u.role.value, u.is_active, u.created_at.isoformat()])

    writer.writerow([])
    writer.writerow(["Submission ID", "Subject ID", "Year", "Session", "Status", "Flagged", "Created At"])
    submissions = db.query(PaperSubmission).order_by(PaperSubmission.id.asc()).all()
    for s in submissions:
        writer.writerow([s.id, s.subject_id, s.exam_year, s.exam_session.value, s.status.value, s.is_flagged, s.created_at.isoformat()])

    log_audit_event(
        db=db,
        action="admin_csv_exported",
        entity_type="system",
        entity_id=None,
        user_id=current_user.id,
        details="Exported platform summary CSV report.",
    )

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=rgpv_exammate_admin_report.csv"},
    )


# =========================================================================
# 8. ANNOUNCEMENTS & NOTIFICATIONS
# =========================================================================

@router.get("/announcements", response_model=List[AnnouncementResponse])
def list_announcements(
    audience: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """List administrative announcements."""
    query = db.query(Announcement)
    if audience:
        query = query.filter(or_(Announcement.audience == audience, Announcement.audience == "all"))
    return query.order_by(Announcement.created_at.desc()).all()


@router.post("/announcements", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
def create_announcement(
    payload: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Publish a new announcement for students, contributors, or reviewers."""
    announcement = Announcement(
        title=payload.title.strip(),
        content=payload.content.strip(),
        audience=payload.audience,
        author_id=current_user.id,
        expires_at=payload.expires_at,
    )
    db.add(announcement)
    db.commit()
    db.refresh(announcement)

    log_audit_event(
        db=db,
        action="announcement_created",
        entity_type="announcement",
        entity_id=announcement.id,
        user_id=current_user.id,
        details=f"Created announcement '{announcement.title}' for audience '{announcement.audience}'",
    )

    return announcement


@router.delete("/announcements/{announcement_id}", response_model=MessageResponse)
def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Archive or remove an announcement."""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found.")

    db.delete(announcement)
    db.commit()

    log_audit_event(
        db=db,
        action="announcement_deleted",
        entity_type="announcement",
        entity_id=announcement_id,
        user_id=current_user.id,
        details=f"Deleted announcement ID {announcement_id}",
    )

    return MessageResponse(message=f"Announcement {announcement_id} removed successfully.")


# =========================================================================
# 9. AUDIT LOGS & SECURITY MONITORING
# =========================================================================

@router.get("/audit-logs")
def list_audit_logs(
    actor_id: Optional[int] = Query(None),
    entity_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Immutable audit trail of all sensitive operations."""
    query = db.query(AuditLog)
    if actor_id:
        query = query.filter(AuditLog.user_id == actor_id)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if action:
        query = query.filter(AuditLog.action.like(f"%{action}%"))

    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    result = []
    for l in logs:
        actor = db.query(User).filter(User.id == l.user_id).first() if l.user_id else None
        result.append({
            "id": l.id,
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "details": l.details,
            "actor_id": l.user_id,
            "actor_name": actor.full_name if actor else "System",
            "actor_email": actor.email if actor else "System",
            "created_at": l.created_at.isoformat(),
        })
    return result


# =========================================================================
# 10. SYSTEM HEALTH & DIAGNOSTICS (No credential leak)
# =========================================================================

@router.get("/system/health")
def get_system_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Read-only operational diagnostics (strictly sanitizes secrets)."""
    # Test DB responsiveness
    import time
    start = time.perf_counter()
    from sqlalchemy import text
    db.execute(text("SELECT 1"))
    latency_ms = round((time.perf_counter() - start) * 1000, 2)

    upload_exists = os.path.exists(settings.UPLOAD_DIR)

    return {
        "status": "operational",
        "database": {
            "status": "connected",
            "latency_ms": latency_ms,
        },
        "storage": {
            "upload_directory_exists": upload_exists,
            "max_upload_size_mb": settings.MAX_UPLOAD_SIZE_MB,
            "allowed_mime_types": ["application/pdf"],
        },
        "application": {
            "name": settings.PROJECT_NAME,
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0",
            "cors_configured": True,
            "rbac_enforced": True,
        },
    }
