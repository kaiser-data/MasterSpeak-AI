from sqlmodel import SQLModel
from database import engine  # Import the database engine

def init_db():
    """
    Initialize the database by creating all tables defined in SQLModel.
    """
    print("Initializing database...")
    try:
        SQLModel.metadata.create_all(engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    init_db()