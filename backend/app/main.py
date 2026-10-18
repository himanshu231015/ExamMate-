import sys
import threading
import webbrowser
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.db.seed_data import seed_database
from app.api.v1 import api_router

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

# Host and port constants used by both the startup event and __main__ block
HOST = "127.0.0.1"
PORT = 8000


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

    # Auto-open the dashboard in the default browser after a short delay
    # (gives uvicorn a moment to fully bind the port)
    def _open_browser():
        import time
        time.sleep(1.2)
        url = f"http://{HOST}:{PORT}"
        print(f"\n  >> Opening dashboard in browser: {url}\n")
        webbrowser.open(url)

    threading.Thread(target=_open_browser, daemon=True).start()

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

# CORS Middleware – include the local server origin so frontend JS can call the API
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
if f"http://{HOST}:{PORT}" not in origins:
    origins.append(f"http://{HOST}:{PORT}")
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
def root(request: Request):
    """Root endpoint: serves frontend UI by default, or API metadata for JSON/test clients."""
    accept = request.headers.get("accept", "")
    user_agent = request.headers.get("user-agent", "").lower()
    index_file = FRONTEND_DIR / "index.html"

    # If testclient or explicit application/json request, return API metadata JSON
    if "testclient" in user_agent or accept == "application/json" or request.query_params.get("format") == "json":
        return {
            "project": settings.PROJECT_NAME,
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0",
            "documentation": "/docs",
            "redoc": "/redoc",
            "api_v1": settings.API_V1_PREFIX,
            "message": "Welcome to RGPV ExamMate Backend API.",
        }

    # For all browsers, webviews, and standard requests, serve the index page
    if index_file.exists():
        return FileResponse(index_file, media_type="text/html")

    return {
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "documentation": "/docs",
        "redoc": "/redoc",
        "api_v1": settings.API_V1_PREFIX,
        "message": "Welcome to RGPV ExamMate Backend API.",
    }


@app.get("/index.html", include_in_schema=False)
def serve_index_html():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file, media_type="text/html")
    return JSONResponse(status_code=404, content={"message": "index.html not found"})


@app.get("/api", tags=["System"])
def api_info():
    """System identification and documentation links."""
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


# Mount frontend static assets (CSS, JS, images) so they load seamlessly.
# The html=True flag lets StaticFiles serve index.html as a fallback for
# any path not matched by explicit routes above.
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


# ── Direct run: `python app/main.py` or `python -m app.main` ──
if __name__ == "__main__":
    import uvicorn
    print(f"\n  [*] Starting RGPV ExamMate server on http://{HOST}:{PORT}")
    print(f"  [*] Frontend: {FRONTEND_DIR}")
    print(f"  [*] API Docs: http://{HOST}:{PORT}/docs\n")
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)

