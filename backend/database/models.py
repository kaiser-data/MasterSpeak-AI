# database/models.py

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import UUID
import uuid
from datetime import datetime
from enum import Enum

# Import new models for database schema
from backend.models.share_token import ShareToken
from backend.models.analysis import Analysis

class SourceType(str, Enum):
    """
    Enumeration for source types.
    """
    AUDIO = "audio"
    TEXT = "text"
    PUBLIC_SPEECH = "public_speech"
    PRESENTATION = "presentation"
    CONFERENCE = "conference"
    PRODUCT_LAUNCH = "product_launch"
    REPORT = "report"

class User(SQLModel, table=True):
    """
    Represents a user in the system.
    """
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    # is_verified: Optional[bool] = Field(default=False)  # TODO: Add after proper migration

    # Relationships
    speeches: List["Speech"] = Relationship(back_populates="user")

class Speech(SQLModel, table=True):
    """
    Represents a speech or text input by a user.
    """
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: Optional[UUID] = Field(foreign_key="user.id")
    title: str
    source_type: SourceType
    content: str
    transcription: Optional[str] = None  # Store Whisper transcription for audio files
    feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="speeches")
    analysis: Optional["SpeechAnalysis"] = Relationship(back_populates="speech")

class SpeechAnalysis(SQLModel, table=True):
    """
    Represents the analysis results of a speech.
    """
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    speech_id: UUID = Field(foreign_key="speech.id")
    word_count: int
    clarity_score: int = Field(ge=1, le=10)
    structure_score: int = Field(ge=1, le=10)
    filler_word_count: Optional[int] = None
    prompt: str
    feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    speech: Optional[Speech] = Relationship(back_populates="analysis")