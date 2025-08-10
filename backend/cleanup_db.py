# backend/cleanup_db.py
# Script to clean up database entries with invalid data

import asyncio
import logging
import sys
import os
from sqlalchemy import text

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database.database import get_session
    from config import settings
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This script must be run from the project root or with proper Python path")
    sys.exit(1)

logger = logging.getLogger(__name__)

async def cleanup_invalid_data():
    """Clean up any invalid data in the database"""
    try:
        async with get_session() as session:
            # Delete speeches with invalid user_id format (like '123')
            result = await session.execute(text("""
                DELETE FROM speeches 
                WHERE user_id IS NOT NULL 
                AND LENGTH(user_id) < 32
            """))
            
            speeches_deleted = result.rowcount
            logger.info(f"Deleted {speeches_deleted} speeches with invalid user_id")
            
            # Delete analyses for speeches that no longer exist
            result = await session.execute(text("""
                DELETE FROM speech_analyses 
                WHERE speech_id NOT IN (SELECT id FROM speeches)
            """))
            
            analyses_deleted = result.rowcount  
            logger.info(f"Deleted {analyses_deleted} orphaned speech analyses")
            
            await session.commit()
            
            print(f"✅ Database cleanup completed:")
            print(f"   - Deleted {speeches_deleted} speeches with invalid user_id")
            print(f"   - Deleted {analyses_deleted} orphaned analyses")
            
    except Exception as e:
        logger.error(f"Error cleaning up database: {e}")
        print(f"❌ Database cleanup failed: {e}")

if __name__ == "__main__":
    asyncio.run(cleanup_invalid_data())