from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

# The database URL is for a SQLite database stored in a file named "database.db"
DATABASE_URL = "sqlite+aiosqlite:///database.db"

# Create an async engine
engine = AsyncEngine(create_engine(DATABASE_URL, echo=True, future=True))

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