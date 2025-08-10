# backend/seed_db.py

from backend.database.models import User, Speech, SpeechAnalysis, SourceType
from backend.database.database import engine, AsyncSessionLocal
from sqlmodel import SQLModel, select
from datetime import datetime, timedelta
from passlib.context import CryptContext
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing with fallback
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    logger.info("bcrypt password context initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize bcrypt context: {e}")
    logger.warning("Using fallback password context - DEVELOPMENT ONLY")
    pwd_context = None

def hash_password(password: str) -> str:
    if pwd_context is None:
        # Fallback to a simple hash - NOT secure, only for development
        import hashlib
        logger.warning("Using insecure fallback password hash - DEVELOPMENT ONLY")
        return f"fallback_{hashlib.md5(password.encode()).hexdigest()}"
    
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing failed: {e}")
        # Fallback to a simple hash - NOT secure, only for development
        import hashlib
        logger.warning("Using insecure fallback password hash - DEVELOPMENT ONLY")
        return f"fallback_{hashlib.md5(password.encode()).hexdigest()}"

async def seed_database():
    try:
        logger.info("Starting database seeding...")

        # Check if database is already seeded
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).limit(1))
            if result.first():
                logger.info("Database already seeded, skipping...")
                return

        # Sample user data
        users = [
            {
                "email": "john.doe@example.com",
                "hashed_password": hash_password("password123"),
                "full_name": "John Doe",
                "is_active": True,
                "is_superuser": False
            },
            {
                "email": "jane.smith@example.com",
                "hashed_password": hash_password("password456"),
                "full_name": "Jane Smith",
                "is_active": True,
                "is_superuser": False
            },
            {
                "email": "admin@example.com",
                "hashed_password": hash_password("admin123"),
                "full_name": "Admin User",
                "is_active": True,
                "is_superuser": True
            }
        ]

        # Create users
        async with AsyncSessionLocal() as session:
            for user_data in users:
                user = User(**user_data)
                session.add(user)
            await session.commit()
            logger.info("Users created successfully")

            # Get user IDs for speeches
            result = await session.execute(select(User))
            user_ids = [user.id for user in result.scalars().all()]

            # Sample speech data
            speeches = [
                {
                    "user_id": user_ids[0],
                    "title": "Product Launch Presentation",
                    "content": "Ladies and gentlemen, today we are excited to introduce our revolutionary new product...",
                    "source_type": SourceType.PUBLIC_SPEECH,
                    "created_at": datetime.utcnow() - timedelta(days=30)
                },
                {
                    "user_id": user_ids[1],
                    "title": "Quarterly Business Review",
                    "content": "Thank you all for joining us today for our quarterly business review...",
                    "source_type": SourceType.PRESENTATION,
                    "created_at": datetime.utcnow() - timedelta(days=15)
                },
                {
                    "user_id": user_ids[2],
                    "title": "Annual Conference Keynote",
                    "content": "Welcome to our annual conference. It's an honor to address such a distinguished audience...",
                    "source_type": SourceType.CONFERENCE,
                    "created_at": datetime.utcnow() - timedelta(days=7)
                }
            ]

            # Create speeches
            for speech_data in speeches:
                speech = Speech(**speech_data)
                session.add(speech)
            await session.commit()
            logger.info("Speeches created successfully")

            # Get speech IDs for analyses
            result = await session.execute(select(Speech))
            speech_ids = [speech.id for speech in result.scalars().all()]

            # Sample analysis data
            analyses = [
                {
                    "speech_id": speech_ids[0],
                    "word_count": 150,
                    "clarity_score": 8.5,
                    "structure_score": 8.0,
                    "filler_word_count": 5,
                    "prompt": "default",
                    "feedback": "Strong opening and clear product messaging. Consider adding more specific data points.",
                    "created_at": datetime.utcnow() - timedelta(days=30)
                },
                {
                    "speech_id": speech_ids[1],
                    "word_count": 200,
                    "clarity_score": 7.2,
                    "structure_score": 7.5,
                    "filler_word_count": 8,
                    "prompt": "default",
                    "feedback": "Good structure but could use more visual aids. Consider breaking down complex data.",
                    "created_at": datetime.utcnow() - timedelta(days=15)
                },
                {
                    "speech_id": speech_ids[2],
                    "word_count": 300,
                    "clarity_score": 9.0,
                    "structure_score": 9.2,
                    "filler_word_count": 3,
                    "prompt": "default",
                    "feedback": "Excellent keynote with strong audience engagement. Well-paced and informative.",
                    "created_at": datetime.utcnow() - timedelta(days=7)
                }
            ]

            # Create analyses
            for analysis_data in analyses:
                analysis = SpeechAnalysis(**analysis_data)
                session.add(analysis)
            await session.commit()
            logger.info("Analyses created successfully")

    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(seed_database())