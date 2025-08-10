# backend/database/database.py

from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import StaticPool
from backend.config import settings
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

# Ensure data directory exists
data_dir = Path(__file__).parent.parent.parent / "data"
data_dir.mkdir(exist_ok=True)

# Create the database URL with absolute path
database_url = settings.DATABASE_URL
if database_url.startswith("sqlite:///"):
    db_path = data_dir / "masterspeak.db"
    database_url = f"sqlite+aiosqlite:///{db_path.absolute()}"

# Configure engine with connection pooling and optimized settings
# Note: For SQLite with async, we use StaticPool
engine = create_async_engine(
    database_url,
    echo=False,  # Disable SQL logging in production
    poolclass=StaticPool,  # Use StaticPool for SQLite async
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Initialize the database
async def init_db():
    """Initialize the database by creating tables if they don't exist."""
    from backend.database import models
    logger.info("Initializing database...")
    try:
        async with engine.begin() as conn:
            # Only drop tables in development mode
            if settings.ENV == "development" and settings.DEBUG:
                logger.warning("Development mode: Dropping existing tables")
                await conn.run_sync(SQLModel.metadata.drop_all)
            
            # Create tables if they don't exist
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

# Note: For production with PostgreSQL and async, you'd use:
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# engine = create_async_engine(settings.DATABASE_URL)
# SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
# async def get_session(): ... async with SessionLocal() as session: yield session ...