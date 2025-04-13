# backend/config.py

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file explicitly if needed, although BaseSettings can do it
load_dotenv()

class Settings(BaseSettings):
    """Manages application settings loaded from environment variables."""
    # Default database URL if not set in .env
    DATABASE_URL: str = "sqlite:///./data/masterspeak.db"
    OPENAI_API_KEY: str
    SECRET_KEY: str  # For JWT token generation/validation
    # Add other secrets if using fastapi-users defaults
    # RESET_SECRET: str
    # VERIFICATION_SECRET: str

    # Optional: Configure BaseSettings to read from .env
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

# Create a single instance to be imported elsewhere
settings = Settings()