# routes/analyze_routes.py

from fastapi import APIRouter, Request, Form, File, UploadFile, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session
from pydantic import BaseModel
from datetime import datetime
import uuid
from openai_service import analyze_text_with_gpt
from database.models import Speech, SpeechAnalysis
from database.database import get_session

router = APIRouter()

DEFAULT_USER_ID = "52c3a53197a94910b78b3b858b63bf71"

@router.get("/analyze-text", response_class=HTMLResponse)
async def analyze_text_form(request: Request):
    return templates.TemplateResponse("analyze_text.html", {"request": request})

@router.post("/analyze-text", response_class=JSONResponse)
async def analyze_text_endpoint(
    request: Request,
    text: str = Form(...),
    prompt_type: str = Form("default"),
    session: Session = Depends(get_session)
):
    try:
        user_id = DEFAULT_USER_ID
        analysis_result = save_speech_and_analysis(session, user_id, text, "text", prompt_type)
        return JSONResponse(content={"message": "Text successfully analyzed.", "analysis": analysis_result})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/upload-analysis", response_class=JSONResponse)
async def upload_and_analyze(file: UploadFile = File(...), session: Session = Depends(get_session)):
    try:
        content = (await file.read()).decode("utf-8")
        user_id = DEFAULT_USER_ID
        analysis_result = save_speech_and_analysis(session, user_id, content, "file")
        return JSONResponse(content={"message": "File successfully analyzed.", "analysis": analysis_result})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

def save_speech_and_analysis(session, user_id, content, source_type="text", prompt_type="default"):
    """
    Save speech and its analysis to the database.
    """
    try:
        analysis_result = analyze_text_with_gpt(content, prompt_type)
        speech = Speech(
            id=uuid.uuid4(),
            user_id=user_id,
            source_type=source_type,
            content=content,
            timestamp=datetime.utcnow()
        )
        session.add(speech)
        session.commit()
        session.refresh(speech)

        speech_analysis = SpeechAnalysis(
            id=uuid.uuid4(),
            speech_id=speech.id,
            word_count=len(content.split()),
            estimated_duration=len(content.split()) / 150,
            clarity_score=analysis_result.get("Clarity", 0),
            structure_score=analysis_result.get("Structure", 0),
            filler_word_count=analysis_result.get("Filler Words", 0),
            prompt=prompt_type,
            created_at=datetime.utcnow()
        )
        session.add(speech_analysis)
        session.commit()
        session.refresh(speech_analysis)

        return analysis_result
    except Exception as e:
        session.rollback()
        raise e