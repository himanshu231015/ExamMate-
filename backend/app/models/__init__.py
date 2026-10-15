"""Database models package."""

from app.core.database import Base
from app.models.user import User, UserRole
from app.models.academic import (
    University,
    Degree,
    Branch,
    AcademicScheme,
    Subject,
    SyllabusDocument,
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
    DocumentVersion,
    SubmissionStatus,
)
from app.models.chat import (
    ChatSession,
    ChatMessage,
    RetrievalRecord,
    Citation,
)
from app.models.feedback import (
    UserFeedback,
    ErrorReport,
    FeedbackRating,
    ErrorCategory,
    ReportStatus,
)
from app.models.study_plan import (
    StudyPlan,
    StudyPlanItem,
    ConfidenceLevel,
    PlanStatus,
)
from app.models.audit import AuditLog

__all__ = [
    "Base",
    "User",
    "UserRole",
    "University",
    "Degree",
    "Branch",
    "AcademicScheme",
    "Subject",
    "SyllabusDocument",
    "SyllabusUnit",
    "SyllabusTopic",
    "VerificationStatus",
    "QuestionPaper",
    "ExtractedQuestion",
    "ExamType",
    "ExamSession",
    "PaperSubmission",
    "PaperReview",
    "DocumentVersion",
    "SubmissionStatus",
    "ChatSession",
    "ChatMessage",
    "RetrievalRecord",
    "Citation",
    "UserFeedback",
    "ErrorReport",
    "FeedbackRating",
    "ErrorCategory",
    "ReportStatus",
    "StudyPlan",
    "StudyPlanItem",
    "ConfidenceLevel",
    "PlanStatus",
    "AuditLog",
]
