from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from uuid import UUID
from enum import Enum

# --- Enums ---
class SourceType(str, Enum):
    """
    Enumeration for source types.
    """
    AUDIO = "audio"
    TEXT = "text"

# --- Speech Schemas ---

class SpeechBase(BaseModel):
    """
    Base schema for speech-related data.
    """
    source_type: SourceType = Field(..., description="Source type must be 'audio' or 'text'")
    content: str = Field(..., min_length=1, description="Original speech content (text or transcription)")
    feedback: Optional[str] = Field(None, description="Optional feedback on the speech")

    @validator("content")
    def validate_content(cls, value):
        """
        Ensure the content is not empty or whitespace-only.
        """
        if not value.strip():
            raise ValueError("Content cannot be empty or whitespace-only.")
        return value

class SpeechCreate(SpeechBase):
    """
    Schema for creating a new speech entry.
    """
    user_id: UUID = Field(..., description="ID of the user who created the speech")

class SpeechResponse(SpeechBase):
    """
    Schema for returning speech data.
    """
    id: UUID = Field(..., description="Unique identifier for the speech")
    user_id: UUID = Field(..., description="ID of the user who created the speech")
    timestamp: datetime = Field(..., description="Timestamp when the speech was created")

    class Config:
        from_attributes = True  # Enable ORM mode for compatibility with SQLModel/SQLAlchemy

# --- Speech Analysis Schemas ---

class SpeechAnalysisBase(BaseModel):
    """
    Base schema for speech analysis-related data.
    """
    speech_id: UUID = Field(..., description="ID of the speech being analyzed")
    word_count: int = Field(..., ge=0, description="Total number of words in the speech")
    estimated_duration: float = Field(..., ge=0, description="Estimated duration of the speech in minutes")
    clarity_score: int = Field(..., ge=1, le=10, description="Clarity score of the speech (1-10)")
    structure_score: int = Field(..., ge=1, le=10, description="Structure score of the speech (1-10)")
    filler_word_count: int = Field(..., ge=0, description="Number of filler words detected in the speech")
    prompt: str = Field(..., min_length=1, description="The prompt used for analyzing the speech")

class SpeechAnalysisCreate(SpeechAnalysisBase):
    """
    Schema for creating speech analysis records.
    """
    pass

class SpeechAnalysisResponse(SpeechAnalysisBase):
    """
    Schema for returning speech analysis results.
    """
    id: UUID = Field(..., description="Unique identifier for the analysis")
    created_at: datetime = Field(..., description="Timestamp when the analysis was created")

    class Config:
        from_attributes = True  # Enable ORM mode for compatibility with SQLModel/SQLAlchemy

# --- User Schemas ---

class UserBase(BaseModel):
    """
    Base schema for user-related data.
    """
    email: str = Field(..., description="Email address of the user (must be unique)")

    @validator("email")
    def validate_email(cls, value):
        """
        Ensure the email is valid.
        """
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Invalid email format.")
        return value

class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """
    hashed_password: str = Field(..., min_length=8, description="Hashed password of the user")

class UserResponse(UserBase):
    """
    Schema for returning user data.
    """
    id: UUID = Field(..., description="Unique identifier for the user")

    class Config:
        from_attributes = True  # Enable ORM mode for compatibility with SQLModel/SQLAlchemy