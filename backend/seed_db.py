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

# Password hashing with robust fallback
pwd_context = None
bcrypt_available = False

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # Test bcrypt functionality
    test_hash = pwd_context.hash("test")
    pwd_context.verify("test", test_hash)
    bcrypt_available = True
    logger.info("✅ bcrypt password context initialized and tested successfully")
except ImportError as e:
    logger.error(f"❌ passlib/bcrypt not available: {e}")
    pwd_context = None
except Exception as e:
    logger.error(f"❌ bcrypt initialization/test failed: {e}")
    logger.warning("🔄 Falling back to development-only password hashing")
    pwd_context = None

def hash_password(password: str) -> str:
    """Hash password with bcrypt or fallback to development-only method."""
    if pwd_context and bcrypt_available:
        try:
            hashed = pwd_context.hash(password)
            logger.debug("✅ Password hashed with bcrypt")
            return hashed
        except Exception as e:
            logger.error(f"❌ bcrypt hashing failed: {e}")
            # Fall through to fallback
    
    # Fallback method - NOT secure, only for development/testing
    import hashlib
    fallback_hash = f"fallback_{hashlib.sha256(password.encode()).hexdigest()}"
    logger.warning("⚠️ Using development-only password hash (SHA256) - NOT for production!")
    return fallback_hash

async def seed_database():
    """Seed database with initial data. Non-fatal - continues startup even if seeding fails."""
    try:
        logger.info("🌱 Database seeding is now disabled for fresh user experience")
        logger.info("✅ Users can now create their own accounts and data from scratch")
        return True

    except Exception as e:
        logger.error(f"❌ Database seeding failed: {str(e)}")
        logger.warning("🔄 Continuing application startup without seeded data")
        # Don't raise - allow application to continue startup
        return False
    
    logger.info("✅ Database seeding completed successfully")
    return True

if __name__ == "__main__":
    asyncio.run(seed_database())