from database import engine  # Import the database engine
from sqlmodel import SQLModel
from database.models import User, Speech, SpeechAnalysis


def init_db():
    """
    Initialize the database by creating all tables defined in SQLModel.
    """
    print("Initializing database...")
    try:
        # Create all tables defined in the imported models
        SQLModel.metadata.create_all(engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    init_db()