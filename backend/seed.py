# seed.py

from sqlmodel import Session, select
from backend.database.database import engine
from backend.database.models import User, Speech, SpeechAnalysis, SourceType
from passlib.context import CryptContext
from datetime import datetime, timedelta
import uuid

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def seed_database():
    # Create a session
    with Session(engine) as session:
        # Check if we already have users
        users = session.exec(select(User)).all()
        if users:
            print("Database already seeded. Skipping...")
            return

        # Create test users
        users = [
            User(
                email="test1@example.com",
                hashed_password=hash_password("password123")
            ),
            User(
                email="test2@example.com",
                hashed_password=hash_password("password123")
            ),
            User(
                email="test3@example.com",
                hashed_password=hash_password("password123")
            )
        ]

        # Add users to session
        for user in users:
            session.add(user)
        session.commit()

        # Create some speeches for each user
        for user in users:
            # Create a speech
            speech = Speech(
                user_id=user.id,
                source_type=SourceType.TEXT,
                content="This is a test speech for user " + user.email,
                feedback="Good job!",
                timestamp=datetime.utcnow() - timedelta(days=1)
            )
            session.add(speech)
            session.commit()
            session.refresh(speech)

            # Create an analysis for the speech
            analysis = SpeechAnalysis(
                speech_id=speech.id,
                word_count=10,
                estimated_duration=30.0,
                clarity_score=8,
                structure_score=7,
                filler_word_count=2,
                prompt="Analyze this speech for clarity and structure",
                created_at=datetime.utcnow()
            )
            session.add(analysis)

        # Commit all changes
        session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database() 