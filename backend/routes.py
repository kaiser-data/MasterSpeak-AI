from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from backend.database import get_session
from backend.models import Speech, SpeechAnalysis
from backend.crud import create_speech, get_speech_by_id, save_analysis, get_analysis_by_speech_id
from schemas import SpeechCreate, SpeechAnalysisCreate

router = APIRouter()

# --- Speech Endpoints ---

@router.post("/speech/", response_model=Speech)
def upload_speech(speech_data: SpeechCreate, session: Session = Depends(get_session)):
    """
    Uploads a new speech (text or audio metadata).
    """
    speech = Speech(**speech_data.dict())
    return create_speech(session, speech)


@router.get("/speech/{speech_id}", response_model=Speech)
def get_speech(speech_id: str, session: Session = Depends(get_session)):
    """
    Retrieves speech details by ID.
    """
    speech = get_speech_by_id(session, speech_id)
    if not speech:
        raise HTTPException(status_code=404, detail="Speech not found")
    return speech

# --- Speech Analysis Endpoints ---

@router.post("/analysis/", response_model=SpeechAnalysis)
def analyze_speech(analysis_data: SpeechAnalysisCreate, session: Session = Depends(get_session)):
    """
    Stores speech analysis results.
    """
    analysis = SpeechAnalysis(**analysis_data.dict())
    return save_analysis(session, analysis)


@router.get("/analysis/{speech_id}", response_model=SpeechAnalysis)
def get_analysis(speech_id: str, session: Session = Depends(get_session)):
    """
    Retrieves analysis results for a specific speech ID.
    """
    analysis = get_analysis_by_speech_id(session, speech_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis
