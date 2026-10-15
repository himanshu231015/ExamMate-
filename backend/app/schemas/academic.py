"""Academic and syllabus schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.academic import VerificationStatus


class UniversityBase(BaseModel):
    name: str
    short_name: str
    state: str
    city: str
    website: Optional[str] = None


class UniversityResponse(UniversityBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DegreeResponse(BaseModel):
    id: int
    university_id: int
    name: str
    code: str
    duration_years: int

    class Config:
        from_attributes = True


class BranchResponse(BaseModel):
    id: int
    degree_id: int
    name: str
    code: str

    class Config:
        from_attributes = True


class AcademicSchemeResponse(BaseModel):
    id: int
    university_id: int
    name: str
    code: str
    start_year: int
    description: Optional[str] = None

    class Config:
        from_attributes = True


class SyllabusTopicBase(BaseModel):
    topic_name: str
    subtopics: Optional[str] = None
    learning_objectives: Optional[str] = None
    importance_level: Optional[str] = "high"


class SyllabusTopicCreate(SyllabusTopicBase):
    unit_id: int


class SyllabusTopicResponse(SyllabusTopicBase):
    id: int
    unit_id: int

    class Config:
        from_attributes = True


class SyllabusUnitBase(BaseModel):
    unit_number: int
    title: str
    description: Optional[str] = None


class SyllabusUnitCreate(SyllabusUnitBase):
    subject_id: int


class SyllabusUnitResponse(SyllabusUnitBase):
    id: int
    subject_id: int
    topics: List[SyllabusTopicResponse] = []

    class Config:
        from_attributes = True


class SyllabusDocumentResponse(BaseModel):
    id: int
    subject_id: int
    academic_year: str
    file_path: Optional[str] = None
    source_url: Optional[str] = None
    verification_status: VerificationStatus
    created_at: datetime

    class Config:
        from_attributes = True


class SubjectBase(BaseModel):
    name: str
    code: str
    semester_number: int
    credits: int = 4
    description: Optional[str] = None


class SubjectCreate(SubjectBase):
    branch_id: int
    scheme_id: int


class SubjectResponse(SubjectBase):
    id: int
    branch_id: int
    scheme_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SubjectDetailResponse(SubjectResponse):
    units: List[SyllabusUnitResponse] = []
    syllabus_documents: List[SyllabusDocumentResponse] = []

    class Config:
        from_attributes = True


class AcademicContextSelection(BaseModel):
    university_id: int
    degree_id: int
    branch_id: int
    scheme_id: int
    semester_number: int
