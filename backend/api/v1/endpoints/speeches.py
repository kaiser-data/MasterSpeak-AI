# backend/api/v1/endpoints/speeches.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from backend.database.models import Speech, SpeechAnalysis, User
from backend.database.database import get_session
from backend.schemas.speech_schema import SpeechRead
from backend.middleware import limiter, RateLimits
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[SpeechRead], summary="Get All Speeches")
@limiter.limit(RateLimits.API_READ)
async def get_speeches(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[UUID] = None,
    session: AsyncSession = Depends(get_session)
) -> List[SpeechRead]:
    """
    Get all speeches with optional filtering by user
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        user_id: Optional UUID to filter by user
        
    Returns:
        List[SpeechRead]: List of speeches
    """
    try:
        query = select(Speech).offset(skip).limit(limit).order_by(Speech.created_at.desc())
        
        if user_id:
            # Verify user exists
            user_result = await session.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            query = query.where(Speech.user_id == user_id)
        
        result = await session.execute(query)
        speeches = result.scalars().all()
        return speeches
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_speeches: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{speech_id}", response_model=SpeechRead, summary="Get Speech by ID")
@limiter.limit(RateLimits.API_READ)
async def get_speech(
    request: Request,
    speech_id: UUID,
    session: AsyncSession = Depends(get_session)
) -> SpeechRead:
    """
    Get a specific speech by ID
    
    Args:
        speech_id: UUID of the speech
        
    Returns:
        SpeechRead: Speech information
    """
    try:
        result = await session.execute(select(Speech).where(Speech.id == speech_id))
        speech = result.scalar_one_or_none()
        
        if not speech:
            raise HTTPException(status_code=404, detail="Speech not found")
            
        return speech
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_speech: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{speech_id}", summary="Delete Speech")
@limiter.limit(RateLimits.API_WRITE)
async def delete_speech(
    request: Request,
    speech_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a speech and its associated analysis
    
    Args:
        speech_id: UUID of the speech to delete
        
    Returns:
        Success message
    """
    try:
        # Check if speech exists
        speech_result = await session.execute(select(Speech).where(Speech.id == speech_id))
        speech = speech_result.scalar_one_or_none()
        
        if not speech:
            raise HTTPException(status_code=404, detail="Speech not found")

        # Delete associated analysis first
        analysis_result = await session.execute(
            select(SpeechAnalysis).where(SpeechAnalysis.speech_id == speech_id)
        )
        analysis = analysis_result.scalar_one_or_none()
        
        if analysis:
            await session.delete(analysis)
        
        # Delete speech
        await session.delete(speech)
        await session.commit()

        return {"message": "Speech deleted successfully", "speech_id": speech_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_speech: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{speech_id}/analysis", summary="Get Speech Analysis")
@limiter.limit(RateLimits.API_READ)
async def get_speech_analysis(
    request: Request,
    speech_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """
    Get analysis for a specific speech
    
    Args:
        speech_id: UUID of the speech
        
    Returns:
        Analysis information
    """
    try:
        # Verify speech exists
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
            raise HTTPException(status_code=404, detail="Analysis not found for this speech")

        return {
            "speech_id": speech_id,
            "analysis_id": analysis.id,
            "word_count": analysis.word_count,
            "clarity_score": analysis.clarity_score,
            "structure_score": analysis.structure_score,
            "filler_word_count": analysis.filler_word_count,
            "feedback": analysis.feedback,
            "prompt": analysis.prompt,
            "created_at": analysis.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_speech_analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))