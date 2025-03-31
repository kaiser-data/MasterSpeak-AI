from database.models import User, Speech, SpeechAnalysis
from database.database import get_session
import uuid
from datetime import datetime

def seed_database():
    with get_session() as session:
        # Create users
        user1 = User(email="alice@example.com", hashed_password="hashed_password_1")
        user2 = User(email="bob@example.com", hashed_password="hashed_password_2")
        session.add_all([user1, user2])

        # Add speeches for Alice
        speech1 = Speech(
            user=user1,
            source_type="text",
            content="This is Alice's first speech.",
            feedback="Good start!",
            timestamp=datetime.utcnow()
        )
        speech2 = Speech(
            user=user1,
            source_type="text",
            content="Another speech by Alice.",
            feedback="Excellent structure.",
            timestamp=datetime.utcnow()
        )

        # Add speeches for Bob
        speech3 = Speech(
            user=user2,
            source_type="audio",
            content="Bob's speech about technology.",
            feedback="Clear and concise.",
            timestamp=datetime.utcnow()
        )
        speech4 = Speech(
            user=user2,
            source_type="text",
            content="Bob's second speech.",
            feedback="Needs improvement.",
            timestamp=datetime.utcnow()
        )

        # Add analysis for speeches
        analysis1 = SpeechAnalysis(
            speech=speech1,
            word_count=50,
            estimated_duration=2.5,
            clarity_score=8,
            structure_score=7,
            filler_word_count=5,
            prompt="default",  # Add a prompt type
            created_at=datetime.utcnow()
        )
        analysis2 = SpeechAnalysis(
            speech=speech2,
            word_count=60,
            estimated_duration=3.0,
            clarity_score=9,
            structure_score=6,
            filler_word_count=3,
            prompt="detailed",  # Add a prompt type
            created_at=datetime.utcnow()
        )
        analysis3 = SpeechAnalysis(
            speech=speech3,
            word_count=70,
            estimated_duration=3.5,
            clarity_score=7,
            structure_score=8,
            filler_word_count=4,
            prompt="concise",  # Add a prompt type
            created_at=datetime.utcnow()
        )
        analysis4 = SpeechAnalysis(
            speech=speech4,
            word_count=45,
            estimated_duration=2.0,
            clarity_score=6,
            structure_score=7,
            filler_word_count=6,
            prompt="default",  # Add a prompt type
            created_at=datetime.utcnow()
        )

        # Add everything to the session
        session.add_all([speech1, speech2, speech3, speech4, analysis1, analysis2, analysis3, analysis4])

if __name__ == "__main__":
    seed_database()