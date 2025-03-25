from fastapi import APIRouter, Depends
from sqlmodel import Session
from backend.database.models import Speech, SpeechAnalysis  # Import models from models.py
from backend.database.database import get_session  # Import session utility

router = APIRouter()

@router.post("/speeches/", response_model=Speech)
def create_speech(speech: Speech, session: Session = Depends(get_session)):
    """
    Create a new speech record in the database.
    """
    session.add(speech)
    session.commit()
    session.refresh(speech)
    return speech

@router.get("/speeches/{speech_id}", response_model=Speech)
def get_speech(speech_id: int, session: Session = Depends(get_session)):
    """
    Retrieve a specific speech by its ID.
    """
    speech = session.get(Speech, speech_id)
    if not speech:
        raise HTTPException(status_code=404, detail="Speech not found")
    return speech