# routes/database_routes.py

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from ..database.models import Speech, SpeechAnalysis  # Import models from models.py
from ..database.database import get_session  # Import session utility

router = APIRouter()

# Configure Jinja2 templates
templates = Jinja2Templates(directory="../frontend/templates")

# --- Database Page ---
@router.get("/database", response_class=HTMLResponse)
async def read_database(request: Request, session: Session = Depends(get_session)):
    """
    Fetch all speeches from the database and render them on the database page.
    """
    speeches = session.exec(select(Speech)).all()
    serialized_speeches = [speech.dict() for speech in speeches]
    return templates.TemplateResponse(
        "database.html",
        {"request": request, "speeches": serialized_speeches}
    )

# --- Create a Speech Record ---
@router.post("/speeches/", response_model=Speech)
def create_speech(speech: Speech, session: Session = Depends(get_session)):
    """
    Create a new speech record in the database.
    """
    session.add(speech)
    session.commit()
    session.refresh(speech)
    return speech

# --- Retrieve a Speech Record ---
@router.get("/speeches/{speech_id}", response_model=Speech)
def get_speech(speech_id: int, session: Session = Depends(get_session)):
    """
    Retrieve a specific speech by its ID.
    """
    speech = session.get(Speech, speech_id)
    if not speech:
        raise HTTPException(status_code=404, detail="Speech not found")
    return speech