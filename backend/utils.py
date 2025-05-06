"""
Utility functions shared across the backend.
"""

from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def check_database_exists() -> bool:
    """
    Check if the SQLite database file exists.
    
    Returns:
        bool: True if database file exists, False otherwise.
    """
    data_dir = Path(__file__).parent.parent / "data"
    db_path = data_dir / "masterspeak.db"
    exists = db_path.exists()
    
    if not exists:
        logger.warning(f"Database file not found at: {db_path}")
    
    return exists


def serialize_user(user) -> dict:
    """
    Serialize a User model for template rendering.
    
    Args:
        user: User model instance
        
    Returns:
        dict: Serialized user data
    """
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active
    }


def serialize_speech(speech) -> dict:
    """
    Serialize a Speech model for template rendering.
    
    Args:
        speech: Speech model instance
        
    Returns:
        dict: Serialized speech data
    """
    return {
        "id": str(speech.id),
        "user_id": str(speech.user_id),
        "title": speech.title,
        "content": speech.content,
        "source_type": speech.source_type,
        "feedback": speech.feedback,
        "created_at": speech.created_at.isoformat() if speech.created_at else None
    }