#!/usr/bin/env python3
"""
Comprehensive configuration test suite for MasterSpeak AI.
Tests all configuration aspects and potential runtime errors.
"""

import asyncio
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

class ConfigurationTestSuite:
    def __init__(self):
        self.results = []
        self.errors = []
        self.warnings = []
        
    def add_result(self, test_name, status, message=""):
        self.results.append({
            "test": test_name,
            "status": "✅ PASS" if status else "❌ FAIL",
            "message": message
        })
        if not status:
            self.errors.append(f"{test_name}: {message}")
    
    def add_warning(self, message):
        self.warnings.append(f"⚠️  {message}")
    
    async def test_environment_variables(self):
        """Test all required environment variables are present and valid."""
        print("\n🔍 Testing Environment Variables...")
        
        try:
            from backend.config import settings
            
            # Required variables
            required_vars = [
                ("ENV", str),
                ("DATABASE_URL", str),
                ("OPENAI_API_KEY", str),
                ("SECRET_KEY", str),
                ("RESET_SECRET", str),
                ("VERIFICATION_SECRET", str),
                ("ALLOWED_ORIGINS", str),
                ("JWT_LIFETIME_SECONDS", int),
                ("DEBUG", bool)
            ]
            
            for var_name, var_type in required_vars:
                try:
                    value = getattr(settings, var_name)
                    if value is None:
                        self.add_result(f"ENV:{var_name}", False, "Value is None")
                    elif not isinstance(value, var_type):
                        self.add_result(f"ENV:{var_name}", False, f"Wrong type: expected {var_type.__name__}")
                    else:
                        self.add_result(f"ENV:{var_name}", True, f"Type: {var_type.__name__}")
                        
                        # Check for example values
                        if var_name in ["SECRET_KEY", "RESET_SECRET", "VERIFICATION_SECRET"]:
                            if "your_" in str(value) or "example" in str(value).lower():
                                self.add_warning(f"{var_name} appears to contain example value")
                                
                except AttributeError:
                    self.add_result(f"ENV:{var_name}", False, "Variable not defined")
            
            return True
            
        except Exception as e:
            self.add_result("Environment Variables", False, str(e))
            return False
    
    async def test_database_configuration(self):
        """Test database configuration and connectivity."""
        print("\n🗄️  Testing Database Configuration...")
        
        try:
            from backend.database.database import engine, init_db, get_session
            from backend.database.models import User, Speech, SpeechAnalysis
            from sqlmodel import select
            
            # Test initialization
            await init_db()
            self.add_result("Database Initialization", True)
            
            # Test session creation
            async with get_session() as session:
                # Test basic query
                result = await session.execute(select(User).limit(1))
                self.add_result("Database Session", True)
                
                # Check tables exist
                from sqlalchemy import inspect
                
                def check_tables(conn):
                    inspector = inspect(conn)
                    return inspector.get_table_names()
                
                async with engine.begin() as conn:
                    tables = await conn.run_sync(check_tables)
                    expected_tables = ['user', 'speech', 'speechanalysis']
                    
                    for table in expected_tables:
                        if table in tables:
                            self.add_result(f"Table:{table}", True)
                        else:
                            self.add_result(f"Table:{table}", False, "Table not found")
            
            return True
            
        except Exception as e:
            self.add_result("Database Configuration", False, str(e))
            return False
    
    async def test_authentication_configuration(self):
        """Test authentication and security configuration."""
        print("\n🔐 Testing Authentication Configuration...")
        
        try:
            from backend.routes.auth_routes import (
                UserManager, get_jwt_strategy, auth_backend
            )
            from backend.config import settings
            
            # Test UserManager secrets
            if UserManager.reset_password_token_secret == settings.RESET_SECRET:
                self.add_result("UserManager:reset_secret", True)
            else:
                self.add_result("UserManager:reset_secret", False, "Secret mismatch")
            
            if UserManager.verification_token_secret == settings.VERIFICATION_SECRET:
                self.add_result("UserManager:verification_secret", True)
            else:
                self.add_result("UserManager:verification_secret", False, "Secret mismatch")
            
            # Test JWT strategy
            strategy = get_jwt_strategy()
            if strategy.secret == settings.SECRET_KEY:
                self.add_result("JWT:secret_key", True)
            else:
                self.add_result("JWT:secret_key", False, "Secret mismatch")
            
            if strategy.lifetime_seconds == settings.JWT_LIFETIME_SECONDS:
                self.add_result("JWT:lifetime", True, f"{settings.JWT_LIFETIME_SECONDS}s")
            else:
                self.add_result("JWT:lifetime", False, "Lifetime mismatch")
            
            # Test auth backend
            self.add_result("Auth Backend", True, auth_backend.name)
            
            return True
            
        except Exception as e:
            self.add_result("Authentication Configuration", False, str(e))
            return False
    
    async def test_cors_configuration(self):
        """Test CORS configuration."""
        print("\n🌐 Testing CORS Configuration...")
        
        try:
            from backend.config import settings
            
            origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",")]
            
            if len(origins) == 0:
                self.add_result("CORS:origins", False, "No origins configured")
            else:
                self.add_result("CORS:origins", True, f"{len(origins)} origins")
                
                # Check for wildcard
                if "*" in origins:
                    self.add_warning("CORS configured with wildcard (*) - security risk in production")
                
                # Check for localhost in production
                if settings.ENV == "production":
                    localhost_origins = [o for o in origins if "localhost" in o]
                    if localhost_origins:
                        self.add_warning(f"Localhost origins in production: {localhost_origins}")
            
            return True
            
        except Exception as e:
            self.add_result("CORS Configuration", False, str(e))
            return False
    
    async def test_api_startup(self):
        """Test API can start without errors."""
        print("\n🚀 Testing API Startup...")
        
        try:
            from backend.main import app
            from backend.routes import all_routers
            
            # Check app instance
            self.add_result("FastAPI App", True, f"Routes: {len(app.routes)}")
            
            # Check routers loaded
            self.add_result("Routers Loaded", True, f"Count: {len(all_routers)}")
            
            # Check static files mount
            static_mounts = [r for r in app.routes if hasattr(r, 'path') and '/static' in str(r.path)]
            if static_mounts:
                self.add_result("Static Files", True)
            else:
                self.add_warning("Static files not mounted")
            
            return True
            
        except Exception as e:
            self.add_result("API Startup", False, str(e))
            return False
    
    async def test_openai_configuration(self):
        """Test OpenAI service configuration."""
        print("\n🤖 Testing OpenAI Configuration...")
        
        try:
            from backend.openai_service import client, rate_limiter
            from backend.config import settings
            
            # Check API key is set
            if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_api_key_here":
                self.add_result("OpenAI:api_key", True, "Configured")
            else:
                self.add_result("OpenAI:api_key", False, "Using example key")
            
            # Check rate limiter
            self.add_result("OpenAI:rate_limiter", True, f"Tokens/min: {rate_limiter.tokens_per_minute}")
            
            return True
            
        except Exception as e:
            self.add_result("OpenAI Configuration", False, str(e))
            return False
    
    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n" + "=" * 60)
        print("📊 CONFIGURATION TEST REPORT")
        print("=" * 60)
        print(f"Generated: {datetime.now().isoformat()}")
        print()
        
        # Summary stats
        passed = sum(1 for r in self.results if "PASS" in r["status"])
        failed = sum(1 for r in self.results if "FAIL" in r["status"])
        total = len(self.results)
        
        print(f"Results: {passed}/{total} passed ({int(passed/total*100)}%)")
        print()
        
        # Detailed results
        print("Test Results:")
        print("-" * 40)
        for result in self.results:
            message = f" - {result['message']}" if result['message'] else ""
            print(f"{result['status']} {result['test']}{message}")
        
        # Warnings
        if self.warnings:
            print("\n⚠️  Warnings:")
            print("-" * 40)
            for warning in self.warnings:
                print(warning)
        
        # Errors
        if self.errors:
            print("\n❌ Errors:")
            print("-" * 40)
            for error in self.errors:
                print(f"  - {error}")
        
        # Recommendations
        print("\n💡 Recommendations:")
        print("-" * 40)
        
        if failed > 0:
            print("1. Fix all failing tests before deployment")
        
        if any("example" in w.lower() for w in self.warnings):
            print("2. Generate production secrets with: python3 generate_secrets.py")
        
        if any("localhost" in w.lower() for w in self.warnings):
            print("3. Update CORS origins for production deployment")
        
        if not self.errors and not self.warnings:
            print("✅ Configuration is production-ready!")
        
        # Save report to file
        report_file = Path("config_test_report.json")
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "success_rate": f"{int(passed/total*100)}%"
            },
            "results": self.results,
            "warnings": self.warnings,
            "errors": self.errors
        }
        
        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📁 Report saved to: {report_file}")
        
        return failed == 0

async def main():
    """Run comprehensive configuration tests."""
    print("=" * 60)
    print("🔧 MasterSpeak AI - Comprehensive Configuration Test")
    print("=" * 60)
    
    suite = ConfigurationTestSuite()
    
    # Run all tests
    await suite.test_environment_variables()
    await suite.test_database_configuration()
    await suite.test_authentication_configuration()
    await suite.test_cors_configuration()
    await suite.test_api_startup()
    await suite.test_openai_configuration()
    
    # Generate report
    success = suite.generate_report()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL CONFIGURATION TESTS PASSED!")
        print("\nYour application is ready to run:")
        print("  python3 -m uvicorn backend.main:app --reload")
    else:
        print("⚠️  CONFIGURATION ISSUES DETECTED")
        print("\nPlease fix the issues above before running the application.")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))