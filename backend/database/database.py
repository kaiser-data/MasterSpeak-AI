# backend/database/database.py

from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.orm import sessionmaker
from backend.config import settings # Import the settings instance
import logging

logger = logging.getLogger(__name__)

# Use the DATABASE_URL from settings
engine = create_engine(settings.DATABASE_URL, echo=True) # Set echo=False for production

# Create a session factory (consider async version for production)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get a database session
def get_session():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize the database (ensure models are imported before calling)
def init_db():
    """Initializes the database by creating tables."""
    # Import models here or ensure they are imported before calling init_db
    from backend.database import models # Assuming models are defined here
    logger.info("Initializing database...")
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created or already exist.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        raise

# Note: For production with PostgreSQL and async, you'd use:
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# engine = create_async_engine(settings.DATABASE_URL)
# SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
# async def get_session(): ... async with SessionLocal() as session: yield session ...