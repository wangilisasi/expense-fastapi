import os
import re
from dotenv import load_dotenv
from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

load_dotenv()

# The database URL is read from the .env file
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found in environment variables")

# The user's snippet uses a regex to ensure the connection string is async-compatible.
# This is a robust way to handle it.
async_db_url = re.sub(r"^(postgresql)://", r"\1+asyncpg://", DATABASE_URL)

# Create an async engine using the new URL
engine = create_async_engine(async_db_url, echo=True, future=True)


async def init_db():
    """
    Initializes the database and creates tables if they don't exist.
    This is called on application startup.
    """
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all) # Use this to drop all tables for a fresh start
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get a database session for each request.
    """
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session 