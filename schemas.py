from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid

# --- Speech Schemas ---

class SpeechBase(BaseModel):
    source_type: str = Field(..., regex="^(audio|text)$", description="Source type must be 'audio' or 'text'")
    content: str = Field(..., description="Original speech content (text or transcription)")
    feedback: Optional[str] = None

class SpeechCreate(SpeechBase):
    """Schema for creating a speech entry."""
    user_id: uuid.UUID

class SpeechResponse(SpeechBase):
    """Schema for returning speech data."""
    id: uuid.UUID
    user_id: uuid.UUID
    timestamp: datetime

    class Config:
        from_attributes = True

# --- Speech Analysis Schemas ---

class SpeechAnalysisBase(BaseModel):
    speech_id: uuid.UUID
    word_count: int
    estimated_duration: float
    clarity_score: int = Field(..., ge=0, le=10, description="Clarity score (0-10)")
    structure_score: int = Field(..., ge=0, le=10, description="Structure score (0-10)")
    filler_word_count: int

class SpeechAnalysisCreate(SpeechAnalysisBase):
    """Schema for creating speech analysis records."""
    pass

class SpeechAnalysisResponse(SpeechAnalysisBase):
    """Schema for returning analysis results."""
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
