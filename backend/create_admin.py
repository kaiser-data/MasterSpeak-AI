#!/usr/bin/env python3
"""
Create an admin (superuser) account for MasterSpeak AI
Usage: python -m backend.create_admin
"""

import asyncio
from backend.database.models import User
from backend.database.database import AsyncSessionLocal
from sqlmodel import select
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Robust password hashing with fallback (matches seed_db.py)
def hash_password_simple(password: str) -> str:
    """Hash password with bcrypt or fallback to development-only method."""
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # Test that bcrypt actually works
        test_hash = pwd_context.hash("test")
        pwd_context.verify("test", test_hash)
        return pwd_context.hash(password)
    except ImportError:
        pass  # Fall through to fallback
    except Exception as e:
        logger.warning(f"bcrypt failed: {e}, using fallback")
    
    # Fallback method - NOT secure, only for development/testing
    import hashlib
    fallback_hash = f"fallback_{hashlib.sha256(password.encode()).hexdigest()}"
    return fallback_hash

async def create_admin_user():
    """Create an admin user if one doesn't exist."""
    try:
        admin_email = "admin@masterspeak.ai"
        admin_password = "admin123"  # Change this!
        admin_name = "Admin User"
        
        async with AsyncSessionLocal() as session:
            # Check if admin already exists
            result = await session.execute(
                select(User).where(User.email == admin_email)
            )
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                logger.info(f"✅ Admin user already exists: {admin_email}")
                if existing_admin.is_superuser:
                    logger.info("✅ User has superuser privileges")
                else:
                    # Update to superuser
                    existing_admin.is_superuser = True
                    await session.commit()
                    logger.info("✅ Updated user to superuser")
                return existing_admin
            
            # Create new admin user
            hashed_password = hash_password_simple(admin_password)
            admin_user = User(
                email=admin_email,
                hashed_password=hashed_password,
                full_name=admin_name,
                is_active=True,
                is_verified=True,
                is_superuser=True
            )
            
            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)
            
            logger.info(f"✅ Created admin user: {admin_email}")
            logger.info("🔑 Default password: admin123")
            logger.warning("⚠️  CHANGE THE PASSWORD AFTER FIRST LOGIN!")
            
            return admin_user
            
    except Exception as e:
        logger.error(f"❌ Failed to create admin user: {str(e)}")
        raise

async def list_all_users():
    """List all users in the database."""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).order_by(User.email))
            users = result.scalars().all()
            
            if not users:
                logger.info("📭 No users found in database")
                return []
            
            logger.info(f"👥 Found {len(users)} users:")
            for user in users:
                status = []
                if user.is_superuser:
                    status.append("SUPERUSER")
                if not user.is_active:
                    status.append("INACTIVE")
                if not getattr(user, 'is_verified', True):
                    status.append("UNVERIFIED")
                
                status_str = f" ({', '.join(status)})" if status else ""
                logger.info(f"  📧 {user.email} - {user.full_name}{status_str}")
            
            return users
            
    except Exception as e:
        logger.error(f"❌ Failed to list users: {str(e)}")
        raise

if __name__ == "__main__":
    async def main():
        logger.info("🔧 MasterSpeak AI Admin User Management")
        logger.info("=" * 50)
        
        # List existing users
        await list_all_users()
        
        # Create admin if needed
        logger.info("\n🔑 Checking/Creating admin user...")
        await create_admin_user()
        
        # List users again
        logger.info("\n👥 Final user list:")
        await list_all_users()
        
        logger.info("\n✅ Admin setup complete!")
        logger.info("📚 Available admin endpoints:")
        logger.info("  GET  /api/v1/users/ - List all users")
        logger.info("  GET  /api/v1/users/admin/count - Get user statistics")
        logger.info("  DELETE /api/v1/users/admin/delete-all - Delete all users")
        logger.info("  DELETE /api/v1/users/admin/delete-inactive - Delete inactive users")
    
    asyncio.run(main())