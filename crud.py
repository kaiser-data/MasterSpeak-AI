from sqlmodel import Session, select
from models import Speech, SpeechAnalysis

# --- Speech CRUD Operations ---

def create_speech(session: Session, speech: Speech) -> Speech:
    """Save a new speech entry to the database."""
    session.add(speech)
    session.commit()
    session.refresh(speech)
    return speech

def get_speech_by_id(session: Session, speech_id: str) -> Speech | None:
    """Retrieve a speech entry by its ID."""
    return session.exec(select(Speech).where(Speech.id == speech_id)).first()

# --- Speech Analysis CRUD Operations ---

def save_analysis(session: Session, analysis: SpeechAnalysis) -> SpeechAnalysis:
    """Save speech analysis results to the database."""
    session.add(analysis)
    session.commit()
    session.refresh(analysis)
    return analysis

def get_analysis_by_speech_id(session: Session, speech_id: str) -> SpeechAnalysis | None:
    """Retrieve analysis results for a given speech ID."""
    return session.exec(select(SpeechAnalysis).where(SpeechAnalysis.speech_id == speech_id)).first()

def get_all_analyses(session: Session):
    """Retrieve all speech analysis records."""
    return session.exec(select(SpeechAnalysis)).all()
