# routes/database_routes.py

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from backend.database.models import Speech, SpeechAnalysis
from backend.database.database import get_session
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Configure Jinja2 templates with absolute path
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "templates")
templates = Jinja2Templates(directory=templates_dir)

# --- Database Page ---
@router.get("/database", response_class=HTMLResponse)
async def read_database(request: Request, session: AsyncSession = Depends(get_session)):
    """
    Fetch all speeches from the database and render them on the database page.
    """
    try:
        result = await session.execute(select(Speech))
        speeches = result.scalars().all()
        serialized_speeches = [speech.model_dump() for speech in speeches]
        return templates.TemplateResponse(
            "database.html",
            {"request": request, "speeches": serialized_speeches}
        )
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")

# --- Create a Speech Record ---
@router.post("/speeches/", response_model=Speech)
async def create_speech(speech: Speech, session: AsyncSession = Depends(get_session)):
    """
    Create a new speech record in the database.
    """
    try:
        session.add(speech)
        await session.commit()
        await session.refresh(speech)
        return speech
    except Exception as e:
        logger.error(f"Error creating speech: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create speech")

# --- Retrieve a Speech Record ---
@router.get("/speeches/{speech_id}", response_model=Speech)
async def get_speech(speech_id: str, session: AsyncSession = Depends(get_session)):
    """
    Retrieve a specific speech by its ID.
    """
    try:
        from uuid import UUID
        speech_uuid = UUID(speech_id)
        speech = await session.get(Speech, speech_uuid)
        if not speech:
            raise HTTPException(status_code=404, detail="Speech not found")
        return speech
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid speech ID format")
    except Exception as e:
        logger.error(f"Error retrieving speech: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve speech")