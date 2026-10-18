"""API v1 Router aggregation."""

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.academic import router as academic_router
from app.api.v1.pyqs import router as pyqs_router
from app.api.v1.submissions import router as submissions_router
from app.api.v1.chat import router as chat_router
from app.api.v1.feedback import router as feedback_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.study_plans import router as study_plans_router
from app.api.v1.admin import router as admin_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(academic_router)
api_router.include_router(pyqs_router)
api_router.include_router(submissions_router)
api_router.include_router(chat_router)
api_router.include_router(feedback_router)
api_router.include_router(analytics_router)
api_router.include_router(study_plans_router)
api_router.include_router(admin_router)
