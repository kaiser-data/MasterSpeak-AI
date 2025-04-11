# backend/seed_db.py

from database.models import User, Speech, SpeechAnalysis
from database.database import get_session
import uuid
from datetime import datetime

def seed_database():
    """
    Seed the database with sample data for users, speeches, and speech analyses.
    """
    # Sample data for seeding
    users_data = [
        {"email": "alice@example.com", "hashed_password": "hashed_password_1"},
        {"email": "bob@example.com", "hashed_password": "hashed_password_2"},
    ]

    speeches_data = [
        {
            "user_index": 0,  # Index of the user in the `users_data` list
            "source_type": "text",
            "content": "This is Alice's first speech.",
            "feedback": "Good start!",
        },
        {
            "user_index": 0,
            "source_type": "text",
            "content": "Another speech by Alice.",
            "feedback": "Excellent structure.",
        },
        {
            "user_index": 1,
            "source_type": "audio",
            "content": "Bob's speech about technology.",
            "feedback": "Clear and concise.",
        },
        {
            "user_index": 1,
            "source_type": "text",
            "content": "Bob's second speech.",
            "feedback": "Needs improvement.",
        },
    ]

    analyses_data = [
        {"word_count": 50, "estimated_duration": 2.5, "clarity_score": 8, "structure_score": 7, "filler_word_count": 5, "prompt": "default"},
        {"word_count": 60, "estimated_duration": 3.0, "clarity_score": 9, "structure_score": 6, "filler_word_count": 3, "prompt": "detailed"},
        {"word_count": 70, "estimated_duration": 3.5, "clarity_score": 7, "structure_score": 8, "filler_word_count": 4, "prompt": "concise"},
        {"word_count": 45, "estimated_duration": 2.0, "clarity_score": 6, "structure_score": 7, "filler_word_count": 6, "prompt": "default"},
    ]

    with get_session() as session:
        # Create users
        users = [User(email=user["email"], hashed_password=user["hashed_password"]) for user in users_data]
        session.add_all(users)
        session.commit()

        # Create speeches
        speeches = []
        for speech_info in speeches_data:
            user = users[speech_info["user_index"]]
            speech = Speech(
                user=user,
                source_type=speech_info["source_type"],
                content=speech_info["content"],
                feedback=speech_info["feedback"],
                timestamp=datetime.utcnow(),
            )
            speeches.append(speech)

        session.add_all(speeches)
        session.commit()

        # Create speech analyses
        analyses = []
        for i, analysis_info in enumerate(analyses_data):
            speech = speeches[i]
            analysis = SpeechAnalysis(
                speech=speech,
                word_count=analysis_info["word_count"],
                estimated_duration=analysis_info["estimated_duration"],
                clarity_score=analysis_info["clarity_score"],
                structure_score=analysis_info["structure_score"],
                filler_word_count=analysis_info["filler_word_count"],
                prompt=analysis_info["prompt"],
                created_at=datetime.utcnow(),
            )
            analyses.append(analysis)

        session.add_all(analyses)
        session.commit()


if __name__ == "__main__":
    seed_database()