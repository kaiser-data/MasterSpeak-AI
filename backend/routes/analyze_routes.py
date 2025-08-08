# analyze_routes.py

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4
import os
import logging
from datetime import datetime

from backend.database.database import get_session
from backend.database.models import Speech, SpeechAnalysis, User
from backend.mock_analysis_service import analyze_text_with_gpt_mock as analyze_text_with_gpt
# Prompts are now handled by the openai_service function

# Configure logging
logger = logging.getLogger(__name__)

# Create a router for analyze-related routes
router = APIRouter()

# OpenAI service is now imported as function

# API endpoints only - no HTML/template endpoints
# All HTML endpoints have been removed for API-only mode

@router.post("/api/analyze/text")
async def analyze_text_api(
    text: str = Form(...),
    title: str = Form(None)
):
    """API endpoint for text analysis."""
    try:
        # Create speech record
        speech_id = uuid4()
        speech = Speech(
            id=speech_id,
            user_id=None,  # Anonymous for now
            title=title or f"Text Analysis {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            source_type="text",
            content=text,
            created_at=datetime.utcnow()
        )
        
        # Perform analysis
        analysis_result = await analyze_text_with_gpt(text, "default")
        
        # Create analysis record
        analysis = SpeechAnalysis(
            id=uuid4(),
            speech_id=speech_id,
            word_count=len(text.split()),
            clarity_score=analysis_result.clarity_score,
            structure_score=analysis_result.structure_score,
            filler_word_count=getattr(analysis_result, 'filler_words_rating', 0),
            prompt="default",
            feedback=analysis_result.feedback or "",
            created_at=datetime.utcnow()
        )
        
        speech.analysis = analysis
        
        # Save to database
        async with get_session() as db:
            db.add(speech)
            db.add(analysis)
            await db.commit()
        
        return JSONResponse(content={
            "success": True,
            "speech_id": str(speech_id),
            "analysis": {
                "clarity_score": analysis_result.clarity_score,
                "structure_score": analysis_result.structure_score,
                "filler_word_count": getattr(analysis_result, 'filler_words_rating', 0),
                "feedback": analysis_result.feedback or ""
            }
        })
        
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/analyze/upload")
async def analyze_upload_api(
    file: UploadFile = File(...),
    title: str = Form(None)
):
    """API endpoint for file upload analysis."""
    try:
        # Read file content
        content = await file.read()
        text = content.decode('utf-8')
        
        # Create speech record
        speech_id = uuid4()
        speech = Speech(
            id=speech_id,
            user_id=None,  # Anonymous for now
            title=title or file.filename or f"Upload Analysis {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            source_type="upload",
            content=text,
            created_at=datetime.utcnow()
        )
        
        # Perform analysis
        analysis_result = await analyze_text_with_gpt(text, "default")
        
        # Create analysis record
        analysis = SpeechAnalysis(
            id=uuid4(),
            speech_id=speech_id,
            word_count=len(text.split()),
            clarity_score=analysis_result.clarity_score,
            structure_score=analysis_result.structure_score,
            filler_word_count=getattr(analysis_result, 'filler_words_rating', 0),
            prompt="default",
            feedback=analysis_result.feedback or "",
            created_at=datetime.utcnow()
        )
        
        speech.analysis = analysis
        
        # Save to database
        async with get_session() as db:
            db.add(speech)
            db.add(analysis)
            await db.commit()
        
        return JSONResponse(content={
            "success": True,
            "speech_id": str(speech_id),
            "analysis": {
                "clarity_score": analysis_result.clarity_score,
                "structure_score": analysis_result.structure_score,
                "filler_word_count": getattr(analysis_result, 'filler_words_rating', 0),
                "feedback": analysis_result.feedback or ""
            }
        })
        
    except Exception as e:
        logger.error(f"Error analyzing upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/analyze/{speech_id}")
async def get_analysis_api(
    speech_id: str
):
    """API endpoint to get analysis results."""
    try:
        async with get_session() as db:
            # Query speech and analysis
            result = await db.execute(
                select(Speech).where(Speech.id == speech_id)
            )
            speech = result.scalar_one_or_none()
            
            if not speech:
                raise HTTPException(status_code=404, detail="Speech not found")
            
            # Get analysis
            result = await db.execute(
                select(SpeechAnalysis).where(SpeechAnalysis.speech_id == speech_id)
            )
            analysis = result.scalar_one_or_none()
            
            if not analysis:
                raise HTTPException(status_code=404, detail="Analysis not found")
            
            return JSONResponse(content={
                "success": True,
                "speech": {
                    "id": str(speech.id),
                    "title": speech.title,
                    "content": speech.content,
                    "source_type": speech.source_type,
                    "created_at": speech.created_at.isoformat()
                },
                "analysis": {
                    "word_count": analysis.word_count,
                    "clarity_score": analysis.clarity_score,
                    "structure_score": analysis.structure_score,
                    "filler_word_count": analysis.filler_word_count,
                    "feedback": analysis.feedback,
                    "created_at": analysis.created_at.isoformat()
                }
            })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))