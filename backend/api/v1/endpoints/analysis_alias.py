# backend/api/v1/endpoints/analysis_alias.py
# Route aliases to maintain compatibility with frontend paths

from fastapi import APIRouter, Request, Form, File, UploadFile, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.database import get_session

# Import the actual handlers from the analysis module
from backend.api.v1.endpoints.analysis import (
    analyze_text as _analyze_text,
    upload_and_analyze as _upload_and_analyze,
    get_analysis_results as _get_analysis_results,
    get_user_analyses as _get_user_analyses
)

router = APIRouter(prefix="/analysis", tags=["analysis-alias"])

@router.post("/text")
async def analyze_text_alias(
    request: Request,
    text: str = Form(...),
    user_id: Optional[UUID] = Form(None),
    prompt_type: str = Form("default"),
    session: AsyncSession = Depends(get_session)
):
    """Alias for /api/v1/analyze/text to maintain frontend compatibility"""
    return await _analyze_text(request, text, user_id, prompt_type, session)

@router.post("/upload")
async def upload_and_analyze_alias(
    request: Request,
    file: UploadFile = File(...),
    user_id: Optional[UUID] = Form(None),
    prompt_type: str = Form("default"),
    session: AsyncSession = Depends(get_session)
):
    """Alias for /api/v1/analyze/upload"""
    return await _upload_and_analyze(request, file, user_id, prompt_type, session)

@router.get("/results/{speech_id}")
async def get_analysis_results_alias(
    request: Request, 
    speech_id: UUID, 
    session: AsyncSession = Depends(get_session)
):
    """Alias for /api/v1/analyze/results/{speech_id}"""
    return await _get_analysis_results(request, speech_id, session)

@router.get("/user/{user_id}")
async def get_user_analyses_alias(
    request: Request,
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
):
    """Alias for /api/v1/analyze/user/{user_id}"""
    return await _get_user_analyses(request, user_id, skip, limit, session)

# Also add a simple-text endpoint that matches the frontend
@router.post("/simple-text")
async def simple_text_analysis(
    text: str = Form(...),
    prompt_type: str = Form("default")
):
    """Simple text analysis endpoint that works without complex dependencies"""
    import uuid
    from datetime import datetime
    
    # Simple analysis logic
    word_count = len(text.split())
    clarity_score = min(10, max(3, 5 + (word_count // 10)))
    structure_score = min(10, max(3, 6 + (len(text.split('.')) // 2)))
    
    feedback = f"Analysis complete! Your speech has {word_count} words. "
    if clarity_score >= 7:
        feedback += "Good clarity. "
    if structure_score >= 7:
        feedback += "Well structured."
    
    speech_id = str(uuid.uuid4())
    
    return JSONResponse(content={
        "speech_id": speech_id,
        "analysis_id": speech_id,
        "word_count": word_count,
        "clarity_score": clarity_score,
        "structure_score": structure_score,
        "filler_words_rating": 7,
        "feedback": feedback,
        "created_at": datetime.utcnow().isoformat()
    })