"""Academic context, subjects, and syllabus management API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles, get_current_user
from app.models.user import User, UserRole
from app.models.academic import (
    University,
    Degree,
    Branch,
    AcademicScheme,
    Subject,
    SyllabusUnit,
    SyllabusTopic,
)
from app.schemas.academic import (
    UniversityResponse,
    DegreeResponse,
    BranchResponse,
    AcademicSchemeResponse,
    SubjectResponse,
    SubjectDetailResponse,
    SubjectCreate,
    SyllabusUnitResponse,
    SyllabusUnitCreate,
    SyllabusTopicResponse,
    SyllabusTopicCreate,
)

router = APIRouter(prefix="/academic", tags=["Academic Context & Syllabus"])


@router.get("/universities", response_model=List[UniversityResponse])
def get_universities(db: Session = Depends(get_db)):
    """Retrieve all supported universities."""
    return db.query(University).all()


@router.get("/universities/{university_id}/degrees", response_model=List[DegreeResponse])
def get_degrees(university_id: int, db: Session = Depends(get_db)):
    """Retrieve degrees offered by a specific university."""
    return db.query(Degree).filter(Degree.university_id == university_id).all()


@router.get("/degrees/{degree_id}/branches", response_model=List[BranchResponse])
def get_branches(degree_id: int, db: Session = Depends(get_db)):
    """Retrieve academic branches for a specific degree."""
    return db.query(Branch).filter(Branch.degree_id == degree_id).all()


@router.get("/universities/{university_id}/schemes", response_model=List[AcademicSchemeResponse])
def get_schemes(university_id: int, db: Session = Depends(get_db)):
    """Retrieve academic curriculum schemes for a university (e.g., CBGS, CBCS)."""
    return db.query(AcademicScheme).filter(AcademicScheme.university_id == university_id).all()


@router.get("/subjects", response_model=List[SubjectResponse])
def get_subjects(
    branch_id: Optional[int] = Query(None, description="Branch ID"),
    scheme_id: Optional[int] = Query(None, description="Scheme ID"),
    semester: Optional[int] = Query(None, ge=1, le=8, description="Semester Number"),
    db: Session = Depends(get_db),
):
    """
    List subjects filtered by branch, scheme, and semester.
    Guarantees that subjects with the same name across different schemes/branches are separated.
    """
    query = db.query(Subject)
    if branch_id:
        query = query.filter(Subject.branch_id == branch_id)
    if scheme_id:
        query = query.filter(Subject.scheme_id == scheme_id)
    if semester:
        query = query.filter(Subject.semester_number == semester)

    return query.all()


@router.get("/subjects/{subject_id}", response_model=SubjectDetailResponse)
def get_subject_detail(subject_id: int, db: Session = Depends(get_db)):
    """Retrieve complete subject details including all units, topics, and syllabus documents."""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID {subject_id} not found."
        )
    return subject


@router.get("/subjects/{subject_id}/syllabus", response_model=List[SyllabusUnitResponse])
def get_subject_syllabus(subject_id: int, db: Session = Depends(get_db)):
    """Unit-wise syllabus navigation for a subject."""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID {subject_id} not found."
        )
    return subject.units


@router.get("/topics/{topic_id}", response_model=SyllabusTopicResponse)
def get_topic_detail(topic_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed learning objectives and subtopics for a specific syllabus topic."""
    topic = db.query(SyllabusTopic).filter(SyllabusTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic with ID {topic_id} not found."
        )
    return topic


@router.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject_in: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Create a new subject record (Admin only)."""
    subject = Subject(**subject_in.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


@router.post("/units", response_model=SyllabusUnitResponse, status_code=status.HTTP_201_CREATED)
def create_unit(
    unit_in: SyllabusUnitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Add a syllabus unit to a subject (Admin only)."""
    unit = SyllabusUnit(**unit_in.model_dump())
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


@router.post("/topics", response_model=SyllabusTopicResponse, status_code=status.HTTP_201_CREATED)
def create_topic(
    topic_in: SyllabusTopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Add a topic to a syllabus unit (Admin only)."""
    topic = SyllabusTopic(**topic_in.model_dump())
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic
