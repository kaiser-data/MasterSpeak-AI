# Example structure (assuming refactored slightly)
# backend/analysis_service.py (or wherever the function lives)

from sqlmodel import Session
from uuid import UUID
from datetime import datetime
import logging

from .database.models import User, Speech, SpeechAnalysis, SourceType
from .openai_service import analyze_text_with_gpt # Assume this raises HTTPException on failure
from .schemas.analysis_schema import AnalysisResponse, SpeechAnalysisCreate
from fastapi import HTTPException

logger = logging.getLogger(__name__)

def calculate_word_count(text: str) -> int:
    """Calculates word count."""
    return len(text.split()) if text else 0

def estimate_duration(word_count: int, wpm: int = 150) -> float:
    """Estimates speech duration in minutes."""
    return round(word_count / wpm, 2) if wpm > 0 and word_count > 0 else 0.0

def save_speech_and_analysis(
    session: Session,
    user_id: UUID,
    content: str,
    source_type: SourceType,
    prompt_type: str = "default"
) -> SpeechAnalysis:
    """
    Saves Speech, performs analysis via OpenAI, saves Analysis, and returns the analysis record.
    Handles potential errors during the process.
    """
    try:
        # 1. Calculate metrics
        word_count = calculate_word_count(content)
        estimated_duration = estimate_duration(word_count)

        # 2. Create and save Speech record
        # Note: Consider if Speech should be committed *before* calling OpenAI.
        # If OpenAI fails, the speech still exists but without analysis.
        # Alternatively, commit everything at the end for atomicity.
        # Current logic saves Speech first.
        speech = Speech(
            user_id=user_id,
            content=content,
            source_type=source_type,
            timestamp=datetime.utcnow()
        )
        session.add(speech)
        session.commit() # Commit Speech separately
        session.refresh(speech)
        logger.info(f"Saved Speech record with ID: {speech.id}")

        try:
            # 3. Call OpenAI for analysis (can raise HTTPException)
            analysis_response: AnalysisResponse = analyze_text_with_gpt(content, prompt_type)

            # 4. Create SpeechAnalysis record
            analysis_create_data = SpeechAnalysisCreate(
                speech_id=speech.id, # Use the committed speech ID
                word_count=word_count,
                estimated_duration=estimated_duration,
                clarity_score=analysis_response.clarity_score,
                structure_score=analysis_response.structure_score,
                filler_word_count=None, # Placeholder
                prompt=prompt_type,
                feedback=analysis_response.feedback
            )
            # Use model_validate for Pydantic v2+ or from_orm/construct for older/SQLModel
            analysis = SpeechAnalysis.model_validate(analysis_create_data)

            session.add(analysis)
            session.commit() # Commit Analysis
            session.refresh(analysis)
            logger.info(f"Saved SpeechAnalysis record with ID: {analysis.id}")

            return analysis

        except Exception as analysis_error:
            # Log analysis-specific error, Speech record still exists
            logger.error(f"Failed during analysis/saving analysis for Speech ID {speech.id}: {analysis_error}", exc_info=True)
            # Re-raise specific exceptions if needed, or handle gracefully
            if isinstance(analysis_error, HTTPException):
                 raise analysis_error # Re-raise HTTP exceptions from openai_service
            else:
                 # Convert other unexpected errors during analysis saving to HTTPException
                 raise HTTPException(status_code=500, detail="Failed to save analysis results after speech creation.")

    except Exception as speech_error:
        # Catch errors during initial Speech saving/commit
        logger.error(f"Failed to save initial speech record for user {user_id}: {speech_error}", exc_info=True)
        session.rollback() # Rollback any potential changes from failed commit
        raise HTTPException(status_code=500, detail="Failed to save speech record.")