# backend/config.py

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from pathlib import Path

# Get the project root directory (parent of backend directory)
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
ENV_FILE = PROJECT_ROOT / '.env'

# Load .env file explicitly if needed, although BaseSettings can do it
print("Loading environment variables...")
print(f"Looking for .env file at: {ENV_FILE}")
load_dotenv(ENV_FILE)

# Debug: Print environment variables (without sensitive values)
print("Environment variables loaded:")
print(f"DATABASE_URL exists: {'DATABASE_URL' in os.environ}")
print(f"SECRET_KEY exists: {'SECRET_KEY' in os.environ}")
print(f"OPENAI_API_KEY exists: {'OPENAI_API_KEY' in os.environ}")

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
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'

# Create a single instance to be imported elsewhere
settings = Settings()