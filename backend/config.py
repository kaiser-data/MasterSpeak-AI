# backend/config.py

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from pathlib import Path
from typing import Optional

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
    ENV: str = "development"
    
    # Database configuration
    DATABASE_URL: str = "sqlite:///./data/masterspeak.db"
    
    # API Keys
    OPENAI_API_KEY: str
    
    # Security settings
    SECRET_KEY: str  # For JWT token generation/validation
    RESET_SECRET: str  # For password reset tokens
    VERIFICATION_SECRET: str  # For email verification tokens
    
    # CORS settings
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"  # Comma-separated list
    
    # JWT settings
    JWT_LIFETIME_SECONDS: int = 3600  # 1 hour default
    
    # Application settings
    DEBUG: bool = False
    
    # Rate limiting settings
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "60/minute"
    RATE_LIMIT_BURST: str = ""  # Optional burst handling
    REDIS_URL: str = ""  # Optional Redis backend for rate limiting
    
    # Rate limit per-endpoint overrides
    RATE_LIMIT_AUTH: str = "5/minute"
    RATE_LIMIT_ANALYSIS: str = "10/minute"
    RATE_LIMIT_UPLOAD: str = "5/minute"
    RATE_LIMIT_HEALTH: str = "100/minute"
    

    # Optional: Configure BaseSettings to read from .env
    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'

# Create a single instance to be imported elsewhere
settings = Settings()