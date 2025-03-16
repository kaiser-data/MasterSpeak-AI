from fastapi_users.db import SQLAlchemyBaseUserTable
from .database import Base

class User(SQLAlchemyBaseUserTable, Base):
    pass


class Speech(Base):
    __tablename__ = "speeches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    source_type = Column(String, nullable=False)
    content = Column(String, nullable=False)
    feedback = Column(String, nullable=True)
    timestamp = Column(String, nullable=False)


from sqlalchemy import Column, Integer, Float, String, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .database import Base

class SpeechAnalysis(Base):
    __tablename__ = "speech_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    speech_id = Column(UUID(as_uuid=True), ForeignKey("speeches.id"), nullable=False)
    word_count = Column(Integer, nullable=False)
    estimated_duration = Column(Float, nullable=False)  # in minutes
    clarity_score = Column(Integer, nullable=False)  # Scale 1-10
    structure_score = Column(Integer, nullable=False)  # Scale 1-10
    filler_word_count = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP")
