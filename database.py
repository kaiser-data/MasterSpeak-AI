from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./speech_analysis.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def get_session():
    with Session(engine) as session:
        yield session
