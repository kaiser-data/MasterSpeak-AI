#!/usr/bin/env python3
"""
Migration script to add ShareToken table for analysis sharing functionality
"""
import asyncio
import sqlite3
import os
from pathlib import Path
from backend.config import settings

async def migrate_add_share_token():
    """Add ShareToken table for sharing analysis functionality"""
    
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
        
        # Check if sharetoken table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sharetoken'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Creating ShareToken table...")
            
            # Create ShareToken table
            create_table_sql = """
            CREATE TABLE sharetoken (
                id TEXT PRIMARY KEY,
                analysis_id TEXT NOT NULL,
                hashed_token TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (analysis_id) REFERENCES analysis (id)
            )
            """
            
            cursor.execute(create_table_sql)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX idx_sharetoken_analysis_id ON sharetoken(analysis_id)")
            cursor.execute("CREATE INDEX idx_sharetoken_expires_at ON sharetoken(expires_at)")
            cursor.execute("CREATE INDEX idx_sharetoken_hashed_token ON sharetoken(hashed_token)")
            
            conn.commit()
            print("✅ ShareToken table created successfully")
        else:
            print("✅ ShareToken table already exists")
        
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
            # Check if sharetoken table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'sharetoken'
                );
            """))
            
            table_exists = result.scalar()
            
            if not table_exists:
                print("Creating ShareToken table...")
                
                # Create ShareToken table
                conn.execute(text("""
                    CREATE TABLE sharetoken (
                        id UUID PRIMARY KEY,
                        analysis_id UUID NOT NULL,
                        hashed_token VARCHAR NOT NULL,
                        expires_at TIMESTAMP NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (analysis_id) REFERENCES analysis (id)
                    )
                """))
                
                # Create indexes
                conn.execute(text("CREATE INDEX idx_sharetoken_analysis_id ON sharetoken(analysis_id)"))
                conn.execute(text("CREATE INDEX idx_sharetoken_expires_at ON sharetoken(expires_at)"))
                conn.execute(text("CREATE INDEX idx_sharetoken_hashed_token ON sharetoken(hashed_token)"))
                
                conn.commit()
                print("✅ ShareToken table created successfully")
            else:
                print("✅ ShareToken table already exists")
                
    except Exception as e:
        print(f"❌ PostgreSQL migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()

async def migrate_using_sqlmodel():
    """Alternative migration using SQLModel metadata (recommended)"""
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlmodel import SQLModel
        from backend.database.models import ShareToken, Analysis  # Import all models
        
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
    print("Starting ShareToken table migration...")
    
    # Try SQLModel approach first (recommended)
    try:
        asyncio.run(migrate_using_sqlmodel())
    except Exception as e:
        print(f"SQLModel migration failed, falling back to direct SQL: {e}")
        asyncio.run(migrate_add_share_token())
    
    print("Migration completed!")