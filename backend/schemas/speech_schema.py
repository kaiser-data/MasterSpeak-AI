from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class SpeechBase(BaseModel):
    """
    Base schema for speech-related data.
    """
    source_type: str = Field(..., description="Source type must be 'audio' or 'text'")
    content: str = Field(..., min_length=1, description="Original speech content (text or transcription)")
    feedback: Optional[str] = Field(None, description="Optional feedback on the speech")

class SpeechCreate(SpeechBase):
    """
    Schema for creating a new speech entry.
    """
    user_id: UUID = Field(..., description="ID of the user who created the speech")

class SpeechRead(SpeechBase):
    """
    Schema for returning speech data.
    """
    id: UUID = Field(..., description="Unique identifier for the speech")
    user_id: UUID = Field(..., description="ID of the user who created the speech")
    timestamp: datetime = Field(..., description="Timestamp when the speech was created")

    class Config:
        orm_mode = True

class SpeechAnalysisRead(BaseModel):
    """
    Schema for returning speech analysis results.
    """
    clarity_score: int = Field(..., ge=1, le=10, description="Clarity score of the speech (1-10)")
    structure_score: int = Field(..., ge=1, le=10, description="Structure score of the speech (1-10)")
    filler_word_count: int = Field(..., ge=0, description="Number of filler words detected in the speech")