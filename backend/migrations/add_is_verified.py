#!/usr/bin/env python3
"""
Migration script to add is_verified column to existing users
"""
import asyncio
import sqlite3
from pathlib import Path

async def migrate_add_is_verified():
    """Add is_verified column to user table if it doesn't exist"""
    
    # Get database path
    db_path = Path(__file__).parent.parent / "data" / "masterspeak.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if is_verified column exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_verified' not in columns:
            print("Adding is_verified column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN is_verified BOOLEAN DEFAULT 0")
            
            # Update existing users to have is_verified = False
            cursor.execute("UPDATE user SET is_verified = 0 WHERE is_verified IS NULL")
            
            conn.commit()
            print("✅ Migration completed successfully")
        else:
            print("✅ is_verified column already exists")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    asyncio.run(migrate_add_is_verified())