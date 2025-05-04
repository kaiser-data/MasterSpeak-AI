#!/usr/bin/env python3
"""
Test script to verify authentication and security configurations are working.
Run after setting up your .env file with proper secrets.
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_config():
    """Test configuration loading."""
    print("Testing configuration loading...")
    try:
        from backend.config import settings
        
        # Check required settings
        assert settings.SECRET_KEY, "SECRET_KEY not set"
        assert settings.RESET_SECRET, "RESET_SECRET not set"
        assert settings.VERIFICATION_SECRET, "VERIFICATION_SECRET not set"
        assert settings.OPENAI_API_KEY, "OPENAI_API_KEY not set"
        
        # Check they're not the example values
        assert settings.SECRET_KEY != "your_strong_random_secret_key_here_min_32_chars", \
            "SECRET_KEY is still the example value! Generate real secrets."
        assert settings.RESET_SECRET != "another_strong_random_secret_for_password_reset", \
            "RESET_SECRET is still the example value! Generate real secrets."
        
        print("✅ Configuration loaded successfully")
        print(f"   - Environment: {settings.ENV}")
        print(f"   - Debug mode: {settings.DEBUG}")
        print(f"   - JWT lifetime: {settings.JWT_LIFETIME_SECONDS}s")
        print(f"   - CORS origins: {settings.ALLOWED_ORIGINS}")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

async def test_database():
    """Test database connection and initialization."""
    print("\nTesting database connection...")
    try:
        from backend.database.database import init_db, get_session
        from backend.database.models import User
        
        # Initialize database
        await init_db()
        print("✅ Database initialized successfully")
        
        # Test session
        async with get_session() as session:
            # Simple query to test connection
            from sqlmodel import select
            result = await session.execute(select(User).limit(1))
            print("✅ Database connection successful")
            return True
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

async def test_auth_routes():
    """Test authentication route configuration."""
    print("\nTesting authentication routes...")
    try:
        from backend.routes.auth_routes import UserManager, get_jwt_strategy
        from backend.config import settings
        
        # Check UserManager secrets
        assert UserManager.reset_password_token_secret == settings.RESET_SECRET
        assert UserManager.verification_token_secret == settings.VERIFICATION_SECRET
        print("✅ UserManager configured with secure secrets")
        
        # Check JWT strategy
        strategy = get_jwt_strategy()
        assert strategy.secret == settings.SECRET_KEY
        assert strategy.lifetime_seconds == settings.JWT_LIFETIME_SECONDS
        print("✅ JWT strategy configured correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Auth routes error: {e}")
        return False

async def test_cors_config():
    """Test CORS configuration."""
    print("\nTesting CORS configuration...")
    try:
        from backend.config import settings
        
        origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",")]
        assert len(origins) > 0, "No CORS origins configured"
        
        print(f"✅ CORS configured with {len(origins)} allowed origins:")
        for origin in origins:
            print(f"   - {origin}")
        
        return True
        
    except Exception as e:
        print(f"❌ CORS configuration error: {e}")
        return False

async def main():
    """Run all security tests."""
    print("=" * 60)
    print("🔒 MasterSpeak AI Security Configuration Test")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(await test_config())
    results.append(await test_database())
    results.append(await test_auth_routes())
    results.append(await test_cors_config())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    if all(results):
        print("✅ All security configurations passed!")
        print("\n🎉 Your application is ready for secure operation.")
        print("\nNext steps:")
        print("1. Run: python -m uvicorn backend.main:app --reload")
        print("2. Visit: http://localhost:8000")
        print("3. Test the authentication endpoints")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nCommon issues:")
        print("1. Missing .env file (copy from .env.example)")
        print("2. Using example secrets (run generate_secrets.py)")
        print("3. Missing dependencies (pip install -r requirements.txt)")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))