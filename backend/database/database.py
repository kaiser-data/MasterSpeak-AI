# database/database.py

from sqlmodel import create_engine, Session
from sqlalchemy.orm import sessionmaker

# Database URL (replace with your actual database URL)
DATABASE_URL = "sqlite:///./test.db"

# Create the engine
engine = create_engine(DATABASE_URL, echo=True)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get a database session
def get_session():
    with Session(engine) as session:
        yield session

# Initialize the database
def init_db():
    from models import SQLModel  # Import here to avoid circular imports
    SQLModel.metadata.create_all(engine)