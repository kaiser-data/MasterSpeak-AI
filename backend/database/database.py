# backend/database/database.py

from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.orm import sessionmaker
from backend.config import settings # Import the settings instance
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Ensure data directory exists
data_dir = Path(__file__).parent.parent.parent / "data"
data_dir.mkdir(exist_ok=True)

# Create the database URL with absolute path
database_url = settings.DATABASE_URL
if database_url.startswith("sqlite:///"):
    db_path = data_dir / "masterspeak.db"
    database_url = f"sqlite:///{db_path.absolute()}"

# Configure engine with proper UUID handling
engine = create_engine(
    database_url,
    echo=True,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

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
    """Initializes the database by creating tables if they don't exist."""
    # Import models here or ensure they are imported before calling init_db
    from backend.database import models # Assuming models are defined here
    logger.info("Initializing database...")
    try:
        # Create tables if they don't exist
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

# Note: For production with PostgreSQL and async, you'd use:
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# engine = create_async_engine(settings.DATABASE_URL)
# SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
# async def get_session(): ... async with SessionLocal() as session: yield session ...