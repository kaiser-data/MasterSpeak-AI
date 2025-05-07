# backend/routes/analyze_routes.py

from fastapi import APIRouter, Request, Form, File, UploadFile, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid
import logging
from typing import Optional
from uuid import UUID
import os
from pathlib import Path

# Local imports
from backend.openai_service import analyze_text_with_gpt
from backend.database.models import User, Speech, SpeechAnalysis, SourceType
from backend.database.database import get_session
from backend.utils import check_database_exists, serialize_user, serialize_speech
from backend.schemas.analysis_schema import AnalysisResult, SpeechAnalysisCreate, AnalysisResponse
from backend.schemas.speech_schema import SpeechRead

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)
logger = logging.getLogger(__name__)

# Configure templates
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "templates")
templates = Jinja2Templates(directory=templates_dir)


# --- Helper Function ---
async def save_speech_and_analysis(
    session: AsyncSession,
    user_id: UUID,
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
        # Add more metrics as needed

        # 2. Create and save Speech record
        speech = Speech(
            user_id=user_id,
            title=f"Analysis {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            content=content,
            source_type=source_type,
            created_at=datetime.utcnow()
        )
        session.add(speech)
        await session.commit()
        await session.refresh(speech)

        # 3. Get analysis from OpenAI
        analysis_result = await analyze_text_with_gpt(content, prompt_type)

        # 4. Create and save Analysis record
        analysis = SpeechAnalysis(
            speech_id=speech.id,
            word_count=word_count,
            clarity_score=analysis_result.clarity_score,
            structure_score=analysis_result.structure_score,
            filler_word_count=analysis_result.filler_words_rating,
            prompt=prompt_type,
            feedback=analysis_result.feedback,
            created_at=datetime.utcnow()
        )
        session.add(analysis)
        await session.commit()
        await session.refresh(analysis)

        return analysis

    except Exception as e:
        logger.error(f"Error in save_speech_and_analysis: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text", response_class=HTMLResponse)
async def analyze_text_endpoint(
    request: Request,
    text: str = Form(...),
    user_id: str = Form(...),
    prompt_type: str = Form("default"),
    session: AsyncSession = Depends(get_session)
):
    """
    Analyze text input and return results.
    """
    try:
        # Convert user_id to UUID
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        # Verify user exists
        result = await session.execute(select(User).where(User.id == user_uuid))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Save and analyze
        analysis = await save_speech_and_analysis(
            session=session,
            user_id=user_uuid,
            content=text,
            source_type=SourceType.TEXT,
            prompt_type=prompt_type
        )

        # Redirect to the analysis results page
        return RedirectResponse(
            url=f"/analysis/results/{analysis.speech_id}",
            status_code=303
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_text_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_class=HTMLResponse)
async def upload_and_analyze(
    request: Request,
    file: UploadFile = File(None),
    text_content: str = Form(None),
    user_id: str = Form(...),
    prompt_type: str = Form("default"),
    session: AsyncSession = Depends(get_session)
):
    """
    Upload and analyze a file or text content.
    """
    try:
        # Convert user_id to UUID
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        # Verify user exists
        result = await session.execute(select(User).where(User.id == user_uuid))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get content from either file or text input
        content = None
        if file:
            content = await file.read()
            content = content.decode("utf-8")
        elif text_content:
            content = text_content
        else:
            raise HTTPException(status_code=400, detail="Either file or text content must be provided")

        # Save and analyze
        analysis = await save_speech_and_analysis(
            session=session,
            user_id=user_uuid,
            content=content,
            source_type=SourceType.TEXT,
            prompt_type=prompt_type
        )

        # Redirect to the analysis results page
        return RedirectResponse(
            url=f"/analysis/results/{analysis.speech_id}",
            status_code=303
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_and_analyze: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/text", response_class=HTMLResponse)
async def get_analyze_text_page(
    request: Request, 
    session: AsyncSession = Depends(get_session),
    user_id: Optional[str] = None
):
    """
    Serve the analyze text page with user selection.
    """
    try:
        if not check_database_exists():
            raise HTTPException(
                status_code=500,
                detail="Database file not found. Please ensure the application is properly initialized."
            )
        
        # Get all users
        result = await session.execute(select(User))
        users = result.scalars().all()
        if not users:
            logger.warning("No users found in database")
            return templates.TemplateResponse(
                "analyze_text.html",
                {"request": request, "users": [], "error": "No users found in database"}
            )
        
        # Convert users to list of dicts for template
        users_data = [
            {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "selected": str(user.id) == user_id if user_id else False
            }
            for user in users
        ]
        
        return templates.TemplateResponse(
            "analyze_text.html",
            {"request": request, "users": users_data, "selected_user_id": user_id}
        )
    except OperationalError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred. Please ensure the database is properly configured."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.get("/upload", response_class=HTMLResponse)
async def get_upload_page(
    request: Request, 
    session: AsyncSession = Depends(get_session),
    user_id: Optional[str] = None
):
    """
    Serve the upload page with user selection.
    """
    try:
        if not check_database_exists():
            raise HTTPException(
                status_code=500,
                detail="Database file not found. Please ensure the application is properly initialized."
            )
        
        # Get all users
        result = await session.execute(select(User))
        users = result.scalars().all()
        if not users:
            logger.warning("No users found in database")
            return templates.TemplateResponse(
                "upload_analysis.html",
                {"request": request, "users": [], "error": "No users found in database"}
            )
        
        # Convert users to list of dicts for template
        users_data = [
            {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "selected": str(user.id) == user_id if user_id else False
            }
            for user in users
        ]
        
        return templates.TemplateResponse(
            "upload_analysis.html",
            {"request": request, "users": users_data, "selected_user_id": user_id}
        )
    except OperationalError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred. Please ensure the database is properly configured."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.get("/results/{speech_id}", response_class=HTMLResponse)
async def get_analysis_results(
    request: Request,
    speech_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Display the analysis results for a specific speech.
    """
    try:
        # Convert speech_id to UUID
        try:
            speech_uuid = UUID(speech_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid speech ID format")

        # Get the speech and its analysis
        # Get speech
        speech_result = await session.execute(select(Speech).where(Speech.id == speech_uuid))
        speech = speech_result.scalar_one_or_none()
        if not speech:
            raise HTTPException(status_code=404, detail="Speech not found")

        # Get analysis
        analysis_result = await session.execute(select(SpeechAnalysis).where(SpeechAnalysis.speech_id == speech_uuid))
        analysis = analysis_result.scalar_one_or_none()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        return templates.TemplateResponse(
            "analysis_results.html",
            {
                "request": request,
                "speech": speech,
                "analysis": analysis
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_analysis_results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add endpoints to GET analysis results, maybe GET /speeches/{speech_id}/analysis
# Ensure these GET endpoints also use authentication and check ownership