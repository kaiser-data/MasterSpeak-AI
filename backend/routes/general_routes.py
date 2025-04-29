# routes/general_routes.py

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from uuid import UUID
from typing import List
from backend.database.models import User, Speech
from backend.database.database import get_session
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Configure Jinja2 templates with absolute path
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "templates")
templates = Jinja2Templates(directory=templates_dir)

# Home page
@router.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# About page
@router.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

# Contact page
@router.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

# Analyze text page
@router.get("/analyze-text", response_class=HTMLResponse)
async def analyze_text(request: Request, session: Session = Depends(get_session)):
    try:
        # Get all users
        users = session.exec(select(User)).all()
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
                "full_name": user.full_name,
                "email": user.email
            }
            for user in users
        ]
        
        return templates.TemplateResponse(
            "analyze_text.html",
            {"request": request, "users": users_data}
        )
    except Exception as e:
        logger.error(f"Error loading analyze text page: {str(e)}")
        return templates.TemplateResponse(
            "analyze_text.html",
            {"request": request, "users": [], "error": str(e)}
        )

# Upload analysis page
@router.get("/upload-analysis", response_class=HTMLResponse)
async def upload_analysis(request: Request, session: Session = Depends(get_session)):
    try:
        # Get all users
        users = session.exec(select(User)).all()
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
                "full_name": user.full_name,
                "email": user.email
            }
            for user in users
        ]
        
        return templates.TemplateResponse(
            "upload_analysis.html",
            {"request": request, "users": users_data}
        )
    except Exception as e:
        logger.error(f"Error loading upload analysis page: {str(e)}")
        return templates.TemplateResponse(
            "upload_analysis.html",
            {"request": request, "users": [], "error": str(e)}
        )

# Database page
@router.get("/database", response_class=HTMLResponse)
async def database(request: Request, session: Session = Depends(get_session)):
    speeches = session.exec(select(Speech)).all()
    serialized_speeches = [speech.dict() for speech in speeches]
    return templates.TemplateResponse(
        "database.html",
        {"request": request, "speeches": serialized_speeches}
    )

# Users page
@router.get("/users", response_class=HTMLResponse)
async def read_users(request: Request, session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    serialized_users = [{"id": user.id, "email": user.email} for user in users]
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "users": serialized_users}
    )

# User speeches page
@router.get("/users/{user_id}/speeches", response_class=HTMLResponse)
async def read_user_speeches(
    request: Request,
    user_id: str,
    session: Session = Depends(get_session)
):
    try:
        user_uuid = UUID(user_id)
        user = session.get(User, user_uuid)
        if not user:
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "message": "User not found"}
            )

        serialized_user = {"id": user.id, "email": user.email}
        serialized_speeches = [
            {
                "id": speech.id,
                "content": speech.content,
                "source_type": speech.source_type,
                "timestamp": speech.timestamp,
                "analysis": {
                    "clarity_score": speech.analysis.clarity_score,
                    "structure_score": speech.analysis.structure_score,
                    "filler_word_count": speech.analysis.filler_word_count,
                } if speech.analysis else None,
            }
            for speech in user.speeches
        ]
        return templates.TemplateResponse(
            "user_speeches.html",
            {"request": request, "user": serialized_user, "speeches": serialized_speeches}
        )
    except ValueError:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Invalid user ID format"}
        )