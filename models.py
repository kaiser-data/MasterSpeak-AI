from sqlmodel import SQLModel, Field
from typing import Optional
import uuid
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str
    hashed_password: str

class Speech(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    source_type: str  # 'audio' or 'text'
    content: str
    feedback: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SpeechAnalysis(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    speech_id: uuid.UUID = Field(foreign_key="speech.id")
    word_count: int
    estimated_duration: float  # In minutes
    clarity_score: int  # Scale 1-10
    structure_score: int  # Scale 1-10
    filler_word_count: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
