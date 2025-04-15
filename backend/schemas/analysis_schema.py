# backend/schemas/analysis_schema.py

from pydantic import BaseModel, Field, Json
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime

class AnalysisResponse(BaseModel):
    """Schema to validate the direct JSON response from OpenAI."""
    clarity_score: int = Field(..., ge=1, le=10, description="Clarity rating (1-10)")
    structure_score: int = Field(..., ge=1, le=10, description="Structure rating (1-10)")
    filler_words_rating: int = Field(..., ge=1, le=10, description="Rating based on filler words (lower is better)") # Example: OpenAI might give a rating
    feedback: Optional[str] = Field(None, description="Brief qualitative feedback")
    # Add other fields if your prompt asks for them

class AnalysisResult(BaseModel):
    """Schema for the analysis data returned by our API."""
    id: UUID
    speech_id: UUID
    word_count: int
    estimated_duration: Optional[float] = None # Making duration optional as it's hard to estimate accurately
    clarity_score: int
    structure_score: int
    filler_word_count: Optional[int] = None # Make optional if not reliably calculated
    prompt: str
    created_at: datetime
    # Include feedback if available from OpenAI response
    feedback: Optional[str] = None

    class Config:
        orm_mode = True # For compatibility with SQLModel/SQLAlchemy objects

class SpeechAnalysisCreate(BaseModel):
    """Schema for creating a new analysis record internaly."""
    speech_id: UUID
    word_count: int
    estimated_duration: Optional[float] = None
    clarity_score: int
    structure_score: int
    filler_word_count: Optional[int] = None
    prompt: str
    feedback: Optional[str] = None