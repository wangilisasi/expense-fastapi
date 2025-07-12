import os
import re
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Load .env file only in development (when .env exists)
if os.path.exists('.env'):
    load_dotenv()

# The database URL is read from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # More descriptive error message
    raise ValueError(
        "DATABASE_URL environment variable not set. "
        "Please set it in your Railway environment variables or .env file for local development."
    )

# For Railway/production, we might need to handle SSL
if DATABASE_URL.startswith("postgres://"):
    # Railway uses postgres:// but SQLAlchemy 2.0 needs postgresql://
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()