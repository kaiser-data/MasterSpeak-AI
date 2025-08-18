#!/usr/bin/env python3
"""
Migration script to add Analysis table for analysis persistence functionality
"""
import asyncio
import sqlite3
import os
from pathlib import Path
from backend.config import settings

async def migrate_add_analysis_table():
    """Add Analysis table for storing analysis results"""
    
    database_url = settings.DATABASE_URL
    
    # Handle different database types
    if database_url.startswith("sqlite:"):
        await migrate_sqlite()
    elif database_url.startswith("postgresql:"):
        await migrate_postgresql()
    else:
        print(f"Unsupported database type: {database_url}")
        return

async def migrate_sqlite():
    """SQLite-specific migration"""
    # Get database path
    database_url = settings.DATABASE_URL
    
    if database_url.startswith("sqlite:///./"):
        # Relative path
        project_root = Path(__file__).parent.parent.parent
        db_path = project_root / "data" / "masterspeak.db"
    elif database_url.startswith("sqlite:///"):
        # Absolute path
        db_path = Path(database_url.replace("sqlite:///", ""))
    else:
        # Handle other SQLite URL formats
        db_path = Path(__file__).parent.parent / "data" / "masterspeak.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        print("Run database initialization first")
        return
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if analysis table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analysis'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Creating Analysis table...")
            
            # Create Analysis table
            create_table_sql = """
            CREATE TABLE analysis (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                speech_id TEXT NOT NULL,
                transcript TEXT,
                metrics TEXT,
                summary TEXT,
                feedback TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (speech_id) REFERENCES speech (id),
                UNIQUE(user_id, speech_id)
            )
            """
            
            cursor.execute(create_table_sql)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX idx_analysis_user_id ON analysis(user_id)")
            cursor.execute("CREATE INDEX idx_analysis_speech_id ON analysis(speech_id)")
            cursor.execute("CREATE INDEX idx_analysis_created_at ON analysis(created_at)")
            cursor.execute("CREATE UNIQUE INDEX idx_analysis_user_speech ON analysis(user_id, speech_id)")
            
            conn.commit()
            print("✅ Analysis table created successfully")
        else:
            print("✅ Analysis table already exists")
        
    except Exception as e:
        print(f"❌ SQLite migration failed: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

async def migrate_postgresql():
    """PostgreSQL-specific migration"""
    try:
        from sqlalchemy import create_engine, text
        
        # Convert async URL to sync for migration
        database_url = settings.DATABASE_URL
        if "postgresql+asyncpg://" in database_url:
            sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        else:
            sync_url = database_url
        
        engine = create_engine(sync_url)
        
        with engine.connect() as conn:
            # Check if analysis table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'analysis'
                );
            """))
            
            table_exists = result.scalar()
            
            if not table_exists:
                print("Creating Analysis table...")
                
                # Create Analysis table
                conn.execute(text("""
                    CREATE TABLE analysis (
                        id UUID PRIMARY KEY,
                        user_id UUID NOT NULL,
                        speech_id UUID NOT NULL,
                        transcript TEXT,
                        metrics JSONB,
                        summary TEXT,
                        feedback TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES "user" (id),
                        FOREIGN KEY (speech_id) REFERENCES speech (id),
                        UNIQUE(user_id, speech_id)
                    )
                """))
                
                # Create indexes
                conn.execute(text("CREATE INDEX idx_analysis_user_id ON analysis(user_id)"))
                conn.execute(text("CREATE INDEX idx_analysis_speech_id ON analysis(speech_id)"))
                conn.execute(text("CREATE INDEX idx_analysis_created_at ON analysis(created_at)"))
                conn.execute(text("CREATE UNIQUE INDEX idx_analysis_user_speech ON analysis(user_id, speech_id)"))
                
                conn.commit()
                print("✅ Analysis table created successfully")
            else:
                print("✅ Analysis table already exists")
                
    except Exception as e:
        print(f"❌ PostgreSQL migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()

async def migrate_using_sqlmodel():
    """Alternative migration using SQLModel metadata (recommended)"""
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlmodel import SQLModel
        from backend.models.analysis import Analysis  # Import the Analysis model
        from backend.database.models import User, Speech  # Import existing models
        
        database_url = settings.DATABASE_URL
        
        # Handle SQLite URL conversion
        if database_url.startswith("sqlite:"):
            if database_url.startswith("sqlite:///./"):
                project_root = Path(__file__).parent.parent.parent
                data_dir = project_root / "data"
                data_dir.mkdir(exist_ok=True)
                db_path = data_dir / "masterspeak.db"
                database_url = f"sqlite+aiosqlite:///{db_path.absolute()}"
            elif database_url.startswith("sqlite:///"):
                database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
        elif database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        
        engine = create_async_engine(database_url)
        
        async with engine.begin() as conn:
            # Create only missing tables (won't affect existing tables)
            await conn.run_sync(SQLModel.metadata.create_all)
            print("✅ Database schema updated successfully")
            
    except Exception as e:
        print(f"❌ SQLModel migration failed: {e}")

if __name__ == "__main__":
    print("Starting Analysis table migration...")
    
    # Try SQLModel approach first (recommended)
    try:
        asyncio.run(migrate_using_sqlmodel())
    except Exception as e:
        print(f"SQLModel migration failed, falling back to direct SQL: {e}")
        asyncio.run(migrate_add_analysis_table())
    
    print("Migration completed!")