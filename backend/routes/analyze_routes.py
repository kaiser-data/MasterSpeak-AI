# backend/routes/analyze_routes.py

from fastapi import APIRouter, Request, Form, File, UploadFile, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlmodel import Session
from datetime import datetime
import uuid
import logging
from typing import Optional

# Local imports
from backend.openai_service import analyze_text_with_gpt
from backend.database.models import User, Speech, SpeechAnalysis, SourceType
from backend.database.database import get_session
from backend.schemas.analysis_schema import AnalysisResult, SpeechAnalysisCreate, AnalysisResponse
from backend.schemas.speech_schema import SpeechRead # Assuming you have this schema

# Placeholder for your actual authentication dependency
# Replace with your fastapi-users or custom dependency
async def get_current_active_user() -> User:
    # This is a placeholder! Implement your actual user fetching logic.
    # Example: raise HTTPException(status_code=401, detail="Not authenticated") if no user
    # Fetch user from DB based on token, etc.
    # For testing, you might fetch a default user, but REMOVE THIS for production
    # with get_session() as session:
    #     user = session.get(User, uuid.UUID("your-test-user-uuid")) # Replace with actual UUID
    #     if not user: raise HTTPException(404)
    #     return user
    raise NotImplementedError("Replace with actual authentication dependency")

router = APIRouter(
    prefix="/analysis", # Add a prefix for clarity
    tags=["Analysis"]   # Tag for API docs
)
logger = logging.getLogger(__name__)

# --- Helper Function (Completed and Refined) ---
def save_speech_and_analysis(
    session: Session,
    user_id: uuid.UUID,
    content: str,
    source_type: SourceType,
    prompt_type: str = "default"
) -> SpeechAnalysis:
    """
    Saves Speech, performs analysis via OpenAI, saves Analysis, and returns the analysis record.
    """
    try:
        # 1. Calculate basic metrics locally
        word_count = len(content.split())
        # Simple duration estimate (adjust WPM as needed)
        words_per_minute = 150
        estimated_duration = round(word_count / words_per_minute, 2) if word_count > 0 else 0.0

        # 2. Create and save Speech record first
        speech = Speech(
            user_id=user_id,
            content=content,
            source_type=source_type,
            timestamp=datetime.utcnow()
            # Feedback field in Speech might be redundant if analysis has feedback
        )
        session.add(speech)
        session.commit()
        session.refresh(speech)
        logger.info(f"Saved Speech record with ID: {speech.id}")

        # 3. Call OpenAI for analysis (can raise HTTPException)
        analysis_response: AnalysisResponse = analyze_text_with_gpt(content, prompt_type)

        # 4. Create SpeechAnalysis record
        # Note: filler_word_count isn't directly provided by the example AnalysisResponse
        # You might need to adjust the prompt/response schema or calculate it differently.
        analysis_create_data = SpeechAnalysisCreate(
            speech_id=speech.id,
            word_count=word_count,
            estimated_duration=estimated_duration,
            clarity_score=analysis_response.clarity_score,
            structure_score=analysis_response.structure_score,
            filler_word_count=None, # Placeholder - needs calculation or prompt adjustment
            prompt=prompt_type,
            feedback=analysis_response.feedback
        )
        analysis = SpeechAnalysis.from_orm(analysis_create_data) # Use from_orm for SQLModel >= 0.0.14
        # Or manually: analysis = SpeechAnalysis(**analysis_create_data.dict())

        session.add(analysis)
        session.commit()
        session.refresh(analysis)
        logger.info(f"Saved SpeechAnalysis record with ID: {analysis.id} for Speech ID: {speech.id}")

        return analysis

    except HTTPException as e:
        # Re-raise HTTPExceptions from analyze_text_with_gpt
        logger.warning(f"HTTPException during analysis for user {user_id}: {e.detail}")
        raise e
    except Exception as e:
        # Catch other unexpected errors (e.g., database commit errors)
        logger.error(f"Failed to save speech and analysis for user {user_id}: {e}", exc_info=True)
        # Rollback potentially needed depending on session management
        # session.rollback() # Be careful with session state if using context manager 'with'
        raise HTTPException(status_code=500, detail="Failed to process and save speech analysis.")


# --- API Endpoints (Improved) ---

# Note: Consider making analysis asynchronous using BackgroundTasks for long analyses
@router.post("/text", response_model=AnalysisResult) # Use specific response model
async def analyze_text_endpoint(
    background_tasks: BackgroundTasks, # Optional: if you want async processing
    text: str = Form(...),
    prompt_type: str = Form("default"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user) # Use authentication
):
    """
    Accepts text input, analyzes it, saves speech and analysis, and returns the result.
    """
    logger.info(f"Received text analysis request from user: {current_user.email}")
    try:
        # Perform saving and analysis directly (or use background task)
        analysis_result = save_speech_and_analysis(
            session=session,
            user_id=current_user.id, # Use authenticated user's ID
            content=text,
            source_type=SourceType.TEXT,
            prompt_type=prompt_type
        )
        # Convert to Pydantic model for response
        return AnalysisResult.from_orm(analysis_result)

    except HTTPException as e:
         # If save_speech_and_analysis raises HTTPException, let FastAPI handle it
        raise e
    except Exception as e:
        # Catch any other unexpected errors during endpoint logic
        logger.error(f"Unhandled error in /text endpoint for user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred.")


@router.post("/upload", response_model=AnalysisResult)
async def upload_and_analyze(
    file: UploadFile = File(...),
    prompt_type: str = Form("default"), # Allow prompt type for uploads too
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Accepts file upload (text), analyzes it, saves speech and analysis, returns result.
    """
    logger.info(f"Received file upload analysis request from user: {current_user.email}")
    try:
        # Basic validation for text files
        if not file.content_type or not file.content_type.startswith('text/'):
             raise HTTPException(status_code=400, detail="Invalid file type. Please upload a text file.")

        content_bytes = await file.read()
        try:
            content = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File content is not valid UTF-8 text.")

        analysis_result = save_speech_and_analysis(
            session=session,
            user_id=current_user.id,
            content=content,
            source_type=SourceType.TEXT, # Assuming file upload is text, adjust if audio->text planned
            prompt_type=prompt_type
        )
        return AnalysisResult.from_orm(analysis_result)

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unhandled error in /upload endpoint for user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred during file processing.")

# Add endpoints to GET analysis results, maybe GET /speeches/{speech_id}/analysis
# Ensure these GET endpoints also use authentication and check ownership