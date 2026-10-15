"""Personalized study plan creation and progress tracking API routes."""

from datetime import datetime, timedelta, timezone, date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.academic import Subject, SyllabusUnit, SyllabusTopic
from app.models.study_plan import StudyPlan, StudyPlanItem, PlanStatus
from app.schemas.study_plan import (
    StudyPlanCreate,
    StudyPlanResponse,
    StudyPlanItemUpdate,
    StudyPlanItemResponse,
)
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/study-plans", tags=["Personalized Study Planner"])


@router.post("/", response_model=StudyPlanResponse, status_code=status.HTTP_201_CREATED)
def create_study_plan(
    plan_in: StudyPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate a structured, topic-wise personalized study plan leading up to the target exam date.
    Distributes subject syllabus topics across available study days and includes PYQ practice activities.
    """
    subject = db.query(Subject).filter(Subject.id == plan_in.subject_id).first()
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found.")

    today = date.today()
    if plan_in.target_exam_date <= today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target exam date must be in the future."
        )

    # Create StudyPlan
    study_plan = StudyPlan(
        user_id=current_user.id,
        subject_id=plan_in.subject_id,
        title=plan_in.title,
        target_exam_date=plan_in.target_exam_date,
        daily_hours=plan_in.daily_hours,
        confidence_level=plan_in.confidence_level,
        status=PlanStatus.ACTIVE,
    )
    db.add(study_plan)
    db.flush()

    # Collect all topics under the subject
    all_topics = []
    for u in subject.units:
        for t in u.topics:
            all_topics.append(t)

    if not all_topics:
        db.commit()
        db.refresh(study_plan)
        return study_plan

    days_available = (plan_in.target_exam_date - today).days
    # Distribute topics across days
    step = max(1, days_available // len(all_topics)) if len(all_topics) > 0 else 1

    current_schedule_date = today + timedelta(days=1)
    for idx, topic in enumerate(all_topics):
        activity = f"Study {topic.topic_name} concepts, derive formulas, and solve 1 related RGPV 7-mark PYQ."
        item = StudyPlanItem(
            study_plan_id=study_plan.id,
            topic_id=topic.id,
            allocated_hours=round(min(plan_in.daily_hours, 2.0), 1),
            practice_activity=activity,
            scheduled_date=current_schedule_date,
            is_completed=False,
        )
        db.add(item)
        current_schedule_date += timedelta(days=step)
        if current_schedule_date >= plan_in.target_exam_date:
            current_schedule_date = plan_in.target_exam_date - timedelta(days=1)

    db.commit()
    db.refresh(study_plan)
    return study_plan


@router.get("/", response_model=List[StudyPlanResponse])
def get_user_study_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all study plans created by the current student."""
    return (
        db.query(StudyPlan)
        .filter(StudyPlan.user_id == current_user.id)
        .order_by(StudyPlan.created_at.desc())
        .all()
    )


@router.get("/{plan_id}", response_model=StudyPlanResponse)
def get_study_plan_detail(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve details and task items for a specific study plan."""
    plan = (
        db.query(StudyPlan)
        .filter(StudyPlan.id == plan_id, StudyPlan.user_id == current_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study plan not found.")
    return plan


@router.patch("/{plan_id}/items/{item_id}", response_model=StudyPlanItemResponse)
def update_study_plan_item(
    plan_id: int,
    item_id: int,
    update_in: StudyPlanItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a study topic item as completed or pending."""
    item = (
        db.query(StudyPlanItem)
        .join(StudyPlan, StudyPlanItem.study_plan_id == StudyPlan.id)
        .filter(
            StudyPlanItem.id == item_id,
            StudyPlan.id == plan_id,
            StudyPlan.user_id == current_user.id,
        )
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study plan item not found.")

    item.is_completed = update_in.is_completed
    item.completed_at = datetime.now(timezone.utc) if update_in.is_completed else None
    db.commit()
    db.refresh(item)
    return item
