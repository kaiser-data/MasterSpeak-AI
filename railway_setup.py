#!/usr/bin/env python3
"""
Railway deployment setup script
Run this on Railway to set up the database and admin user
"""

import asyncio
import os
import logging
from backend.database.database import init_db
from backend.seed_db import seed_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_railway():
    """Set up Railway environment"""
    try:
        logger.info("🚀 Starting Railway setup...")
        
        # Log environment info
        logger.info(f"DATABASE_URL: {'✓' if os.getenv('DATABASE_URL') else '✗'}")
        logger.info(f"RAILWAY_ENVIRONMENT: {'✓' if os.getenv('RAILWAY_ENVIRONMENT') else '✗'}")
        logger.info(f"OPENAI_API_KEY: {'✓' if os.getenv('OPENAI_API_KEY') else '✗'}")
        logger.info(f"SECRET_KEY: {'✓' if os.getenv('SECRET_KEY') else '✗'}")
        
        # Initialize database
        logger.info("📊 Initializing database...")
        await init_db()
        logger.info("✅ Database initialized")
        
        # Run seed (now disabled for fresh accounts)
        logger.info("🌱 Running database seed...")
        await seed_database()
        logger.info("✅ Database seed completed")
        
        logger.info("🎉 Railway setup complete!")
        
    except Exception as e:
        logger.error(f"❌ Railway setup failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(setup_railway())