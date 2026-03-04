"""
init_db.py — One-time database table creation script.

Run this manually for initial setup on a fresh database ONLY.
For all subsequent schema changes, use Alembic migrations instead:

    alembic revision --autogenerate -m "describe change"
    alembic upgrade head

Usage:
    python init_db.py
"""
from app.database import engine
import app.models as models

if __name__ == "__main__":
    print("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    print("Done. All tables created successfully.")
