# backend/api/v1/endpoints/analysis.py

from fastapi import APIRouter, Request, Form, File, UploadFile, Body, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, ValidationError

from backend.database.models import User, Speech, SpeechAnalysis, SourceType
from backend.database.database import get_session

# Optional auth dependency
try:
    from backend.dependencies.auth import get_current_user_optional
except Exception:
    def get_current_user_optional():
        return None
from backend.openai_service_backup import analyze_text_with_gpt_simple as analyze_text_with_gpt
try:
    from backend.middleware.rate_limiting import limiter, RateLimits, create_rate_limit_decorator
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    RATE_LIMITING_AVAILABLE = False
    # Mock limiter and decorator for when rate limiting is not available
    def create_rate_limit_decorator(limit: str):
        def decorator(func):
            return func
        return decorator
    
    class MockLimiter:
        def limit(self, limit_string):
            return create_rate_limit_decorator(limit_string)
    limiter = MockLimiter()
    
    # Mock RateLimits class
    RateLimits = type('RateLimits', (), {
        'API_READ': '30/minute',
        'ANALYSIS_TEXT': '10/minute',
        'ANALYSIS_UPLOAD': '5/minute'
    })()
from backend.schemas.analysis_schema import AnalysisResult, AnalysisResponse, AnalyzeTextRequest
from backend.schemas.speech_schema import SpeechRead
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

async def get_analysis_data(request: Request) -> dict:
    """Extract analysis data from either JSON or form data"""
    try:
        content_type = request.headers.get("content-type", "")
        if content_type.startswith("multipart/form-data"):
            form = await request.form()
            return {
                "text": form.get("text"),
                "user_id": form.get("user_id"), 
                "prompt": form.get("prompt_type", "default")
            }
        else:
            # Assume JSON
            data = await request.json()
            return {
                "text": data.get("text"),
                "user_id": data.get("user_id"),
                "prompt": data.get("prompt", "default")
            }
    except Exception as e:
        logger.error(f"Error parsing request: {e}")
        raise HTTPException(status_code=422, detail="Invalid request format")

@router.post("/text", response_model=AnalysisResponse, summary="Analyze Text")
@create_rate_limit_decorator(RateLimits.ANALYSIS_TEXT)
async def analyze_text(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user_optional),
) -> AnalysisResponse:
    """
    Analyze text content and return AI-powered feedback
    
    Accepts both JSON and multipart/form-data:
    - JSON: {"text": "...", "user_id": "...", "prompt": "default"}
    - Form: text=...&user_id=...&prompt_type=default
        
    Returns:
        AnalysisResponse: Analysis results with scores and feedback
    """
    try:
        # Get data from either JSON or form
        data = await get_analysis_data(request)
        text_content = data.get("text")
        prompt_value = data.get("prompt", "default")  
        user_id_value = data.get("user_id")
            
        # Extract and validate text
        text_content = (text_content or "").strip()
        if not text_content:
            raise HTTPException(status_code=400, detail="`text` is required")
        
        # Prefer authenticated user; fallback to optional user_id; allow None
        final_user_id = getattr(current_user, "id", None) if current_user else None
        if final_user_id is None:
            final_user_id = user_id_value  # may be None
        
        # Verify user exists if user_id is provided
        if final_user_id:
            result = await session.execute(select(User).where(User.id == final_user_id))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

        # Calculate basic metrics
        word_count = len(text_content.split())
        
        # Create and save Speech record
        speech = Speech(
            user_id=final_user_id,  # Can be None for anonymous
            title=f"Text Analysis {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            content=text_content,
            source_type=SourceType.TEXT,
            created_at=datetime.utcnow()
        )
        session.add(speech)
        await session.commit()
        await session.refresh(speech)

        # Get analysis from OpenAI
        analysis_result = await analyze_text_with_gpt(text_content, prompt_value)

        # Create and save Analysis record
        analysis = SpeechAnalysis(
            speech_id=speech.id,
            word_count=word_count,
            clarity_score=analysis_result.clarity_score,
            structure_score=analysis_result.structure_score,
            filler_word_count=analysis_result.filler_words_rating,
            prompt=prompt_value,
            feedback=analysis_result.feedback or "",
            created_at=datetime.utcnow()
        )
        session.add(analysis)
        await session.commit()
        await session.refresh(analysis)

        return AnalysisResponse(
            speech_id=speech.id,
            analysis_id=analysis.id,
            word_count=word_count,
            clarity_score=analysis_result.clarity_score,
            structure_score=analysis_result.structure_score,
            filler_words_rating=analysis_result.filler_words_rating,
            feedback=analysis_result.feedback,
            created_at=analysis.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_text: {str(e)}")
        # Only rollback if transaction is active
        if session.in_transaction():
            await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_model=AnalysisResponse, summary="Upload and Analyze File")
@create_rate_limit_decorator(RateLimits.ANALYSIS_UPLOAD)
async def upload_and_analyze(
    request: Request,
    file: UploadFile = File(..., description="Text file to upload and analyze"),
    user_id: Optional[UUID] = Form(None, description="ID of the user performing the analysis"),
    prompt_type: str = Form("default", description="Type of analysis prompt to use"),
    session: AsyncSession = Depends(get_session)
) -> AnalysisResponse:
    """
    Upload a text file and analyze its content
    
    Args:
        file: Text file to upload
        user_id: UUID of the user performing the analysis
        prompt_type: Type of analysis prompt
        
    Returns:
        AnalysisResponse: Analysis results with scores and feedback
    """
    try:
        # Verify user exists
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Read file content
        if not file.content_type or not file.content_type.startswith('text/'):
            raise HTTPException(status_code=400, detail="File must be a text file")
            
        content = await file.read()
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File must contain valid UTF-8 text")

        if len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="File cannot be empty")

        # Use the same analysis logic as text endpoint
        return await analyze_text(request, text, user_id, prompt_type, session)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_and_analyze: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{speech_id}", response_model=AnalysisResponse, summary="Get Analysis Results")
@create_rate_limit_decorator(RateLimits.API_READ)
async def get_analysis_results(
    request: Request,
    speech_id: UUID,
    session: AsyncSession = Depends(get_session)
) -> AnalysisResponse:
    """
    Get analysis results for a specific speech
    
    Args:
        speech_id: UUID of the speech to get analysis for
        
    Returns:
        AnalysisResponse: Analysis results with scores and feedback
    """
    try:
        # Get the speech
        speech_result = await session.execute(select(Speech).where(Speech.id == speech_id))
        speech = speech_result.scalar_one_or_none()
        if not speech:
            raise HTTPException(status_code=404, detail="Speech not found")

        # Get analysis
        analysis_result = await session.execute(
            select(SpeechAnalysis).where(SpeechAnalysis.speech_id == speech_id)
        )
        analysis = analysis_result.scalar_one_or_none()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        return AnalysisResponse(
            speech_id=speech.id,
            analysis_id=analysis.id,
            word_count=analysis.word_count,
            clarity_score=analysis.clarity_score,
            structure_score=analysis.structure_score,
            filler_words_rating=analysis.filler_word_count,
            feedback=analysis.feedback,
            created_at=analysis.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_analysis_results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}", response_model=List[AnalysisResponse], summary="Get User's Analyses")
@create_rate_limit_decorator(RateLimits.API_READ)
async def get_user_analyses(
    request: Request,
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
) -> List[AnalysisResponse]:
    """
    Get all analysis results for a specific user
    
    Args:
        user_id: UUID of the user
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        
    Returns:
        List[AnalysisResponse]: List of user's analysis results
    """
    try:
        # Verify user exists
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get user's speeches with analyses
        query = (
            select(Speech, SpeechAnalysis)
            .join(SpeechAnalysis, Speech.id == SpeechAnalysis.speech_id)
            .where(Speech.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Speech.created_at.desc())
        )
        
        results = await session.execute(query)
        speech_analysis_pairs = results.fetchall()

        analyses = []
        for speech, analysis in speech_analysis_pairs:
            analyses.append(AnalysisResponse(
                speech_id=speech.id,
                analysis_id=analysis.id,
                word_count=analysis.word_count,
                clarity_score=analysis.clarity_score,
                structure_score=analysis.structure_score,
                filler_words_rating=analysis.filler_word_count,
                feedback=analysis.feedback,
                created_at=analysis.created_at
            ))

        return analyses

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_user_analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))