#!/usr/bin/env python3
"""
Railway startup script that ensures database initialization before starting server
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def init_app():
    """Initialize the application for Railway deployment"""
    try:
        print("🚀 Starting MasterSpeak AI on Railway...")
        
        # Import after path setup
        from backend.database.database import init_db
        from backend.seed_db import seed_database
        
        print("📊 Initializing database...")
        await init_db()
        print("✅ Database initialized")
        
        print("🌱 Seeding database...")
        await seed_database()
        print("✅ Database seeded")
        
        print("🎉 Application initialized successfully")
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        # Don't fail completely - let uvicorn try to start anyway
        import traceback
        traceback.print_exc()

def main():
    """Main entry point"""
    # Run initialization
    try:
        asyncio.run(init_app())
    except Exception as e:
        print(f"⚠️ Init warning: {e}")
    
    # Start uvicorn server
    port = int(os.environ.get('PORT', 8000))
    print(f"🌐 Starting server on port {port}")
    
    os.system(f"uvicorn main:app --host 0.0.0.0 --port {port}")

if __name__ == "__main__":
    main()