"""
Analysis model for MasterSpeak-AI.
Provides idempotent analysis persistence with unique constraint on (user_id, speech_id).
"""

from sqlmodel import SQLModel, Field, UniqueConstraint
from sqlalchemy import JSON
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime


class Analysis(SQLModel, table=True):
    """
    Analysis persistence model with idempotent constraint.
    
    Features:
    - Unique constraint on (user_id, speech_id) for idempotency
    - Optional transcript, metrics, and summary fields
    - Required feedback field for AI-generated analysis
    - Automatic timestamps for audit trail
    """
    
    # Primary fields
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    speech_id: UUID = Field(foreign_key="speech.id", index=True)
    
    # Analysis content (optional fields for flexibility)
    transcript: Optional[str] = Field(default=None, description="Transcribed content (never logged)")
    metrics: Optional[str] = Field(default=None, description="Structured metrics JSON (stored as JSON string)")
    summary: Optional[str] = Field(default=None, description="AI-generated summary")
    feedback: str = Field(description="Required AI analysis feedback")
    
    # Audit timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Idempotency constraint
    __table_args__ = (
        UniqueConstraint("user_id", "speech_id", name="uq_analysis_user_speech"),
    )


class AnalysisCreate(SQLModel):
    """
    Pydantic model for analysis creation requests.
    """
    user_id: UUID
    speech_id: UUID
    transcript: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    feedback: str


class AnalysisResponse(SQLModel):
    """
    Pydantic model for analysis API responses.
    """
    analysis_id: UUID
    speech_id: UUID
    user_id: UUID
    transcript: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    feedback: str
    created_at: datetime
    updated_at: datetime


class AnalysisListResponse(SQLModel):
    """
    Pydantic model for paginated analysis list responses.
    """
    items: list[AnalysisResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool


class AnalysisComplete(SQLModel):
    """
    Pydantic model for the /api/v1/analysis/complete endpoint.
    """
    user_id: UUID
    speech_id: UUID
    transcript: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    feedback: str