"""Initialize database tables and seed initial academic context and users."""

from app.core.database import engine, SessionLocal, Base
from app.models import *  # Import all models to ensure metadata registration
from app.db.seed_data import seed_database


def init_db():
    """Create all tables and seed default data."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

    db = SessionLocal()
    try:
        print("Seeding initial academic and user records...")
        seed_database(db)
        print("Database initialized successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
