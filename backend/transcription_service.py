# backend/transcription_service.py
import os
import logging
import tempfile
import hashlib
from typing import Optional, Dict, Any
from openai import OpenAI, APIError, AuthenticationError, RateLimitError, BadRequestError
from fastapi import HTTPException, UploadFile
import asyncio
from datetime import datetime

from backend.config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Cache for storing transcription results
transcription_cache: Dict[str, str] = {}

def get_transcription_cache_key(file_content: bytes) -> str:
    """Generate a cache key for the transcription request based on file content."""
    return hashlib.md5(file_content).hexdigest()

async def transcribe_audio_file(file: UploadFile, max_retries: int = 3) -> str:
    """
    Transcribe audio file using OpenAI Whisper API.

    Args:
        file (UploadFile): The audio file to transcribe.
        max_retries (int): Maximum number of retry attempts.

    Returns:
        str: The transcribed text.

    Raises:
        HTTPException: If transcription fails or file is invalid.
    """
    if not file.content_type or not file.content_type.startswith('audio/'):
        raise HTTPException(
            status_code=400, 
            detail="File must be an audio file (MP3, WAV, M4A, etc.)"
        )

    try:
        # Read file content for caching
        file_content = await file.read()
        
        # Check cache first
        cache_key = get_transcription_cache_key(file_content)
        if cache_key in transcription_cache:
            logger.info("Returning cached transcription result")
            return transcription_cache[cache_key]

        # Reset file pointer for OpenAI API
        await file.seek(0)
        
        retry_count = 0
        last_error = None

        while retry_count < max_retries:
            try:
                # Create a temporary file for the upload
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
                    temp_file.write(file_content)
                    temp_file_path = temp_file.name

                try:
                    logger.info(f"Sending audio file to Whisper API: {file.filename}")
                    
                    # Open the temporary file and send to Whisper
                    with open(temp_file_path, "rb") as audio_file:
                        transcript = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file,
                            language="en",  # Can be made configurable
                            response_format="text"
                        )
                    
                    # Cache the result
                    transcription_cache[cache_key] = transcript
                    
                    logger.info("Audio transcription successful")
                    return transcript
                    
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(temp_file_path)
                    except OSError:
                        pass

            except RateLimitError as e:
                last_error = e
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = min(2 ** (retry_count + 1), 30)  # Exponential backoff
                    logger.warning(f"Rate limit hit, retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                continue

            except AuthenticationError as e:
                logger.error(f"OpenAI Authentication Error - check API key: {e}")
                raise HTTPException(
                    status_code=500, 
                    detail="Transcription service authentication failed"
                )
            
            except (APIError, BadRequestError) as e:
                logger.error(f"OpenAI API Error during transcription: {e}")
                raise HTTPException(
                    status_code=502 if isinstance(e, APIError) else 400,
                    detail=f"Transcription service error: {type(e).__name__}"
                )

            except Exception as e:
                logger.error(f"Unexpected error during transcription: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500, 
                    detail="An unexpected error occurred during transcription"
                )

        # If we've exhausted all retries
        if last_error:
            logger.error(f"Transcription failed after {max_retries} retries. Last error: {last_error}")
            raise HTTPException(
                status_code=429,
                detail="Transcription service is currently overloaded. Please try again later."
            )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"File processing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail="Failed to process audio file"
        )

def is_audio_file(content_type: str) -> bool:
    """Check if the file is an audio file based on content type."""
    audio_types = [
        'audio/mpeg',       # MP3
        'audio/wav',        # WAV
        'audio/mp4',        # M4A
        'audio/x-m4a',      # M4A alternative
        'audio/webm',       # WebM audio
        'audio/ogg',        # OGG
    ]
    return content_type in audio_types

def get_supported_audio_formats() -> list[str]:
    """Return list of supported audio formats for documentation."""
    return ["MP3", "WAV", "M4A", "WebM", "OGG"]