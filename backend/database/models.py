from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
import uuid
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
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for the user."
    )
    email: str = Field(
        unique=True,
        index=True,
        description="Email address of the user (must be unique)."
    )
    hashed_password: str = Field(
        description="Hashed password of the user."
    )

    # Relationships
    speeches: list["Speech"] = Relationship(back_populates="user")


class Speech(SQLModel, table=True):
    """
    Represents a speech or text input by a user.
    """
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for the speech."
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id",
        description="ID of the user who created this speech."
    )
    source_type: SourceType = Field(
        description="Type of the source ('audio' or 'text')."
    )
    content: str = Field(
        description="The actual content of the speech or text."
    )
    feedback: Optional[str] = Field(
        default=None,
        description="Feedback provided for the speech (optional)."
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the speech was created."
    )

    # Relationships
    user: Optional[User] = Relationship(back_populates="speeches")
    analysis: Optional["SpeechAnalysis"] = Relationship(back_populates="speech")


class SpeechAnalysis(SQLModel, table=True):
    """
    Represents the analysis results of a speech.
    """
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for the analysis."
    )
    speech_id: uuid.UUID = Field(
        foreign_key="speech.id",
        description="ID of the speech being analyzed."
    )
    word_count: int = Field(
        ge=0,
        description="Total number of words in the speech."
    )
    estimated_duration: float = Field(
        ge=0,
        description="Estimated duration of the speech in minutes."
    )
    clarity_score: int = Field(
        ge=1,
        le=10,
        description="Clarity score of the speech on a scale of 1-10."
    )
    structure_score: int = Field(
        ge=1,
        le=10,
        description="Structure score of the speech on a scale of 1-10."
    )
    filler_word_count: int = Field(
        ge=0,
        description="Number of filler words detected in the speech."
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the analysis was created."
    )

    # Relationships
    speech: Optional[Speech] = Relationship(back_populates="analysis")