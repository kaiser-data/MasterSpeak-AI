from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
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
    content: str = Field(..., description="Original speech content (text or transcription)")
    feedback: Optional[str] = Field(None, description="Optional feedback on the speech")

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
    clarity_score: int = Field(..., ge=0, le=10, description="Clarity score of the speech (0-10)")
    structure_score: int = Field(..., ge=0, le=10, description="Structure score of the speech (0-10)")
    filler_word_count: int = Field(..., ge=0, description="Number of filler words detected in the speech")

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