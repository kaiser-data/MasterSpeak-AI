from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./speech_analysis.db")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Create Engine with SQLite-specific settings
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
    echo=DEBUG,  # Log SQL queries (useful for debugging, disable in production)
)

def init_db():
    """
    Initialize the database by creating all tables defined in SQLModel.
    """
    logger.info("Initializing database...")
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

@contextmanager
def get_session():
    """
    Context manager to provide a database session.
    Ensures the session is properly closed after use.
    Can also be used as a generator for FastAPI Depends.
    """
    session = Session(engine)
    try:
        logger.debug("Opening database session...")
        yield session  # Yield the session
        session.commit()  # Commit changes if no exceptions occur
        logger.debug("Database session committed successfully.")
    except Exception as e:
        session.rollback()  # Rollback in case of errors
        logger.error(f"Error in database session: {e}")
        raise
    finally:
        session.close()  # Ensure the session is always closed
        logger.debug("Database session closed.")

# Generator-based wrapper for FastAPI Depends
def get_db_session():
    """
    Generator-based function to provide a database session for FastAPI Depends.
    """
    with get_session() as session:
        yield session