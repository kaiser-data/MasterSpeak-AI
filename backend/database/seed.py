from sqlmodel import Session
from backend.database.database import engine, get_session  # Import database utilities
from backend.database.models import User, Speech, SpeechAnalysis, SourceType  # Import models
import logging
from datetime import datetime, timedelta
import random
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_random_users(count: int) -> list[User]:
    """
    Generate a list of random users.
    """
    users = []
    for i in range(count):
        email = f"user{i + 1}@example.com"
        hashed_password = f"hashedpassword{random.randint(100, 999)}"
        user = User(email=email, hashed_password=hashed_password)
        users.append(user)
    return users


def generate_random_speeches(users: list[User], count_per_user: int) -> list[Speech]:
    """
    Generate a list of random speeches for each user.
    """
    speeches = []
    sample_texts = [
        "This is a sample speech for testing purposes.",
        "Another speech sample recorded as audio.",
        "Public speaking is an essential skill for success.",
        "Practice makes perfect when it comes to speaking.",
        "Filler words like um and uh should be minimized."
    ]

    for user in users:
        for i in range(count_per_user):
            source_type = random.choice([SourceType.TEXT, SourceType.AUDIO])
            content = random.choice(sample_texts)
            feedback = random.choice(["Good clarity but too many filler words.", "Excellent structure but needs improvement in pacing."])
            timestamp = datetime.utcnow() - timedelta(days=random.randint(0, 30))  # Random timestamp within the last 30 days
            speech = Speech(
                user_id=user.id,
                source_type=source_type,
                content=content,
                feedback=feedback,
                timestamp=timestamp
            )
            speeches.append(speech)
    return speeches


def generate_random_analyses(speeches: list[Speech]) -> list[SpeechAnalysis]:
    """
    Generate a list of random speech analyses for each speech.
    """
    analyses = []
    for speech in speeches:
        word_count = random.randint(50, 200)
        estimated_duration = round(word_count / 150, 2)  # Assuming 150 words per minute
        clarity_score = random.randint(1, 10)
        structure_score = random.randint(1, 10)
        filler_word_count = random.randint(0, 10)
        created_at = speech.timestamp + timedelta(minutes=random.randint(1, 60))  # Analysis happens after speech creation
        analysis = SpeechAnalysis(
            speech_id=speech.id,
            word_count=word_count,
            estimated_duration=estimated_duration,
            clarity_score=clarity_score,
            structure_score=structure_score,
            filler_word_count=filler_word_count,
            created_at=created_at
        )
        analyses.append(analysis)
    return analyses


def seed_data():
    """
    Seed the database with initial data for testing and development.
    """
    logger.info("Seeding database with initial data...")

    # Generate random users
    user_count = 50  # Number of users to create
    users = generate_random_users(user_count)

    # Generate random speeches (e.g., 5 speeches per user)
    speeches_per_user = 5
    speeches = generate_random_speeches(users, speeches_per_user)

    # Generate random speech analyses
    analyses = generate_random_analyses(speeches)

    try:
        # Insert data into the database
        with get_session() as session:
            logger.info(f"Adding {len(users)} users...")
            session.add_all(users)

            # Commit to generate IDs for users
            session.commit()

            logger.info(f"Adding {len(speeches)} speeches...")
            session.add_all(speeches)

            # Commit to generate IDs for speeches
            session.commit()

            logger.info(f"Adding {len(analyses)} speech analyses...")
            session.add_all(analyses)

            # Final commit
            session.commit()

        logger.info("Database seeded successfully.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        raise


if __name__ == "__main__":
    # Initialize the database (create tables if they don't exist)
    from backend.database.database import init_db
    init_db()

    # Seed the database with initial data
    seed_data()