"""FastAPI Main Application for RGPV ExamMate."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.db.seed_data import seed_database
from app.api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler: initializes database and seed data on startup."""
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield
    print("Application shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Production-minded AI-Powered University Exam Preparation Platform API "
        "designed for RGPV (Rajiv Gandhi Proudyogiki Vishwavidyalaya) B.Tech Students."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 API Routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["System"])
def root():
    """Root endpoint providing system identification and documentation links."""
    return {
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "documentation": "/docs",
        "redoc": "/redoc",
        "api_v1": settings.API_V1_PREFIX,
        "message": "Welcome to RGPV ExamMate Backend API.",
    }


@app.get("/health", tags=["System"])
def health_check():
    """System health check verifying API and database operational status."""
    db_status = "healthy"
    try:
        db = SessionLocal()
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER,
        "embedding_provider": settings.EMBEDDING_PROVIDER,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler ensuring sensitive stack traces aren't leaked in responses."""
    # In debug mode, we can include stringified error; in production, keep generic
    detail = str(exc) if settings.DEBUG else "An unexpected internal server error occurred."
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal Server Error", "detail": detail},
    )
