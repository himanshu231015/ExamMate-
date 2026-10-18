"""Pytest fixtures for database, test client, and authenticated test tokens."""

import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.db.seed_data import seed_database
from app.main import app

# Use a test SQLite database
TEST_DB_URL = "sqlite:///./data/test_exammate.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create test tables and seed initial records once per session."""
    os.makedirs("./data", exist_ok=True)
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    seed_database(db)
    db.close()
    yield
    # Teardown
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./data/test_exammate.db"):
        try:
            os.remove("./data/test_exammate.db")
        except Exception:
            pass


@pytest.fixture
def db():
    """Provide a database session for a test and roll back changes."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def student_headers():
    """Authorization headers for a student user (ID: 4 in seed)."""
    token = create_access_token(data={"sub": "4", "role": "student"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def reviewer_headers():
    """Authorization headers for a reviewer user (ID: 2 in seed)."""
    token = create_access_token(data={"sub": "2", "role": "reviewer"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def contributor_headers():
    """Authorization headers for a contributor user (ID: 3 in seed)."""
    token = create_access_token(data={"sub": "3", "role": "contributor"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers():
    """Authorization headers for an administrator user (ID: 1 in seed)."""
    token = create_access_token(data={"sub": "1", "role": "admin"})
    return {"Authorization": f"Bearer {token}"}
