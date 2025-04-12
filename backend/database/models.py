# database/models.py

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class SourceType(str, Enum):
    """
    Enumeration for source types.
    """
    AUDIO = "audio"
    TEXT = "text"

class User(SQLModel, table=True):
    """
    Represents a user in the system.
    """
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str

    # Relationships
    speeches: List["Speech"] = Relationship(back_populates="user")

class Speech(SQLModel, table=True):
    """
    Represents a speech or text input by a user.
    """
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: Optional[UUID] = Field(foreign_key="user.id")
    source_type: SourceType
    content: str
    feedback: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="speeches")
    analysis: Optional["SpeechAnalysis"] = Relationship(back_populates="speech")

class SpeechAnalysis(SQLModel, table=True):
    """
    Represents the analysis results of a speech.
    """
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    speech_id: UUID = Field(foreign_key="speech.id")
    word_count: int = Field(ge=0)
    estimated_duration: float = Field(ge=0)
    clarity_score: int = Field(ge=1, le=10)
    structure_score: int = Field(ge=1, le=10)
    filler_word_count: int = Field(ge=0)
    prompt: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    speech: Optional[Speech] = Relationship(back_populates="analysis")