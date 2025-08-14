# backend/config.py

import re
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from pathlib import Path
from typing import Optional, List, Union

# Get the project root directory (parent of backend directory)
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
ENV_FILE = PROJECT_ROOT / '.env'

# Load .env file
load_dotenv(ENV_FILE)

# Only print debug info in development
if os.getenv('ENV', 'development') == 'development':
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(f"Looking for .env file at: {ENV_FILE}")
    logger.debug(f"Environment check - DATABASE_URL: {'✓' if 'DATABASE_URL' in os.environ else '✗'}")
    logger.debug(f"Environment check - SECRET_KEY: {'✓' if 'SECRET_KEY' in os.environ else '✗'}")
    logger.debug(f"Environment check - OPENAI_API_KEY: {'✓' if 'OPENAI_API_KEY' in os.environ else '✗'}")

class Settings(BaseSettings):
    """Manages application settings loaded from environment variables."""
    # Application environment
    ENV: str = "production"  # Default to production for Railway deployment
    
    # Database configuration with Railway PostgreSQL support
    DATABASE_URL: str = (
        os.getenv("DATABASE_URL") or  # Railway PostgreSQL (persistent)
        ("sqlite:////tmp/masterspeak.db" if (os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PORT")) else "sqlite:///./data/masterspeak.db")
    )
    
    # API Keys
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-3.5-turbo"  # Default model, can be overridden
    
    # Security settings
    SECRET_KEY: str  # For JWT token generation/validation
    RESET_SECRET: str  # For password reset tokens
    VERIFICATION_SECRET: str  # For email verification tokens
    
    # CORS and security settings
    TRUSTED_HOSTS: Union[List[str], str] = "localhost,127.0.0.1,[::1],masterspeak-ai-production.up.railway.app"
    ALLOWED_ORIGINS: Union[List[str], str] = "http://localhost:3000,https://masterspeak-ai.vercel.app,https://master-speak-gr57j6rdr-martins-projects-5db7b2b8.vercel.app"
    ALLOWED_ORIGIN_REGEX: Optional[str] = r"^https://.*\.vercel\.app$"
    
    # JWT settings
    JWT_LIFETIME_SECONDS: int = 3600  # 1 hour default
    
    # Application settings
    DEBUG: bool = False
    DEBUG_CORS: bool = True  # Enable CORS debug header injection (temporary for debugging)
    
    # Rate limiting settings
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "60/minute"
    RATE_LIMIT_BURST: str = ""  # Optional burst handling
    REDIS_URL: str = ""  # Optional Redis backend for rate limiting
    
    # Rate limit per-endpoint overrides
    RATE_LIMIT_AUTH: str = "20/minute"  # Increased for testing
    RATE_LIMIT_ANALYSIS: str = "10/minute"
    RATE_LIMIT_UPLOAD: str = "5/minute"
    RATE_LIMIT_HEALTH: str = "100/minute"
    
    # Email Configuration
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@masterspeak-ai.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_USE_TLS: bool = True
    MAIL_USE_SSL: bool = False
    

    @property
    def trusted_hosts(self) -> List[str]:
        v = self.TRUSTED_HOSTS
        return [s.strip() for s in (v.split(",") if isinstance(v, str) else v)]

    @property
    def allowed_origins(self) -> List[str]:
        v = self.ALLOWED_ORIGINS
        return [s.strip() for s in (v.split(",") if isinstance(v, str) else v)]

    # Optional: Configure BaseSettings to read from .env
    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'

# Create a single instance to be imported elsewhere
settings = Settings()