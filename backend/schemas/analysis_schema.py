from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class AnalysisBase(BaseModel):
    """
    Base schema for speech analysis-related data.
    """
    speech_id: UUID = Field(..., description="ID of the speech being analyzed")
    word_count: int = Field(..., ge=0, description="Total number of words in the speech")
    estimated_duration: float = Field(..., ge=0, description="Estimated duration of the speech in minutes")
    clarity_score: int = Field(..., ge=1, le=10, description="Clarity score of the speech (1-10)")
    structure_score: int = Field(..., ge=1, le=10, description="Structure score of the speech (1-10)")
    filler_word_count: int = Field(..., ge=0, description="Number of filler words detected in the speech")
    prompt: str = Field(..., description="The prompt used for analyzing the speech")

class AnalysisCreate(AnalysisBase):
    """
    Schema for creating speech analysis records.
    """
    pass

class AnalysisRead(AnalysisBase):
    """
    Schema for returning speech analysis results.
    """
    id: UUID = Field(..., description="Unique identifier for the analysis")
    created_at: datetime = Field(..., description="Timestamp when the analysis was created")

    class Config:
        orm_mode = True