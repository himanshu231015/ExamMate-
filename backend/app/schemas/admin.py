"""Admin Pydantic request and response schemas."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.models.user import UserRole


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserStatusUpdate(BaseModel):
    is_active: bool


class ReviewerAssignmentRequest(BaseModel):
    submission_id: int
    reviewer_id: int


class ModerationResolveRequest(BaseModel):
    action: str = Field(..., description="approve, reject, return_for_correction, flag, unflag")
    reason: str = Field(..., min_length=3, description="Mandatory reason for decision or administrative override")


class PaperPublishRequest(BaseModel):
    is_published: bool


class SubjectCreate(BaseModel):
    name: str = Field(..., min_length=2)
    code: str = Field(..., min_length=2)
    branch_id: int
    scheme_id: int
    semester_number: int = Field(..., ge=1, le=8)
    credits: int = Field(4, ge=1, le=10)
    description: Optional[str] = None


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    branch_id: Optional[int] = None
    scheme_id: Optional[int] = None
    semester_number: Optional[int] = Field(None, ge=1, le=8)
    credits: Optional[int] = Field(None, ge=1, le=10)
    description: Optional[str] = None


class AnnouncementCreate(BaseModel):
    title: str = Field(..., min_length=3)
    content: str = Field(..., min_length=5)
    audience: str = Field("all", description="all, students, contributors, reviewers")
    expires_at: Optional[datetime] = None


class AnnouncementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    audience: str
    is_active: bool
    author_id: Optional[int] = None
    published_at: datetime
    expires_at: Optional[datetime] = None
    created_at: datetime


class AdminOverviewMetrics(BaseModel):
    total_users: int
    active_students: int
    total_contributors: int
    total_reviewers: int
    pending_submissions: int
    approved_papers: int
    verified_questions: int
    flagged_submissions: int
    rejected_submissions: int
    total_subjects: int
    total_units: int
    recent_activity: List[Dict[str, Any]] = []


class AdminUserListItem(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    submissions_count: int = 0
    reviews_count: int = 0


class ContributorStatsItem(BaseModel):
    user_id: int
    full_name: str
    email: str
    total_submissions: int
    approved: int
    rejected: int
    pending: int
    quality_score: float


class ReviewerStatsItem(BaseModel):
    user_id: int
    full_name: str
    email: str
    is_active: bool
    assigned_pending: int
    completed_reviews: int


class SyllabusCoverageItem(BaseModel):
    subject_id: int
    subject_code: str
    subject_name: str
    semester: int
    units_count: int
    topics_count: int
    papers_count: int
    is_complete: bool
