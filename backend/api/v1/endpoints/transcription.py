# backend/api/v1/endpoints/transcription.py
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from backend.database.database import get_session
from backend.database.models import Speech, User
from backend.transcription_service import transcribe_audio_file, is_audio_file, get_supported_audio_formats
from backend.api.v1.endpoints.auth import get_current_user
from backend.schemas.speech_schema import SpeechRead

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/transcribe", response_model=dict)
async def transcribe_audio(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Transcribe an audio file using OpenAI Whisper API.
    
    Returns the transcription text without saving to database.
    """
    try:
        # Validate file type
        if not file.content_type or not is_audio_file(file.content_type):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported formats: {', '.join(get_supported_audio_formats())}"
            )
        
        # Validate file size (10MB limit)
        if file.size and file.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File size too large. Maximum size is 10MB."
            )
        
        logger.info(f"Starting transcription for file: {file.filename}")
        
        # Transcribe the audio
        transcription = await transcribe_audio_file(file)
        
        logger.info(f"Transcription completed for file: {file.filename}")
        
        return {
            "transcription": transcription,
            "filename": file.filename,
            "content_type": file.content_type,
            "supported_formats": get_supported_audio_formats()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to transcribe audio file"
        )

@router.post("/transcribe-and-save", response_model=SpeechRead)
async def transcribe_and_save_speech(
    file: UploadFile = File(...),
    title: str = None,
    current_user: Optional[User] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Transcribe an audio file and save it as a Speech record.
    
    The transcription will be stored in both the transcription and content fields.
    """
    try:
        # Validate file type
        if not file.content_type or not is_audio_file(file.content_type):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported formats: {', '.join(get_supported_audio_formats())}"
            )
        
        # Validate file size (10MB limit)
        if file.size and file.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File size too large. Maximum size is 10MB."
            )
        
        logger.info(f"Starting transcription and save for file: {file.filename}")
        
        # Transcribe the audio
        transcription = await transcribe_audio_file(file)
        
        # Create speech record
        speech_title = title or f"Transcribed from {file.filename}"
        
        speech = Speech(
            user_id=current_user.id if current_user else None,
            title=speech_title,
            source_type="audio",
            content=transcription,  # Store transcription as content for analysis
            transcription=transcription  # Also store in dedicated transcription field
        )
        
        session.add(speech)
        await session.commit()
        await session.refresh(speech)
        
        logger.info(f"Speech record created with transcription: {speech.id}")
        
        return SpeechRead.model_validate(speech)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription and save error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to transcribe and save audio file"
        )

@router.get("/speech/{speech_id}/transcription")
async def get_speech_transcription(
    speech_id: UUID,
    current_user: Optional[User] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get the transcription for a specific speech record.
    """
    try:
        # Get the speech record
        speech = session.get(Speech, speech_id)
        
        if not speech:
            raise HTTPException(
                status_code=404,
                detail="Speech not found"
            )
        
        # Check authorization
        if current_user and speech.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this speech"
            )
        
        return {
            "speech_id": speech.id,
            "title": speech.title,
            "transcription": speech.transcription,
            "source_type": speech.source_type,
            "created_at": speech.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get transcription error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve speech transcription"
        )

@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get list of supported audio formats for transcription.
    """
    return {
        "supported_formats": get_supported_audio_formats(),
        "max_file_size": "10MB",
        "model": "whisper-1"
    }