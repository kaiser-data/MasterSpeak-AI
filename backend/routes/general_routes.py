# routes/general_routes.py

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from uuid import UUID
from typing import List
from backend.database.models import User, Speech
from backend.database.database import get_session
import os
import logging
from pathlib import Path
from sqlalchemy.exc import OperationalError

router = APIRouter()
logger = logging.getLogger(__name__)

# Configure Jinja2 templates with absolute path
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "templates")
templates = Jinja2Templates(directory=templates_dir)

def check_database_exists():
    """Check if the database file exists."""
    data_dir = Path(__file__).parent.parent.parent / "data"
    db_path = data_dir / "masterspeak.db"
    return db_path.exists()

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
        if not check_database_exists():
            raise HTTPException(
                status_code=500,
                detail="Database file not found. Please ensure the application is properly initialized."
            )
        
        # Get all users
        users = session.query(User).all()
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
                "full_name": user.full_name
            }
            for user in users
        ]
        
        return templates.TemplateResponse(
            "analyze_text.html",
            {"request": request, "users": users_data}
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

# Upload analysis page
@router.get("/upload-analysis", response_class=HTMLResponse)
async def upload_analysis(request: Request, session: Session = Depends(get_session)):
    try:
        if not check_database_exists():
            raise HTTPException(
                status_code=500,
                detail="Database file not found. Please ensure the application is properly initialized."
            )
        
        # Get all users
        users = session.query(User).all()
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
                "full_name": user.full_name
            }
            for user in users
        ]
        
        return templates.TemplateResponse(
            "upload_analysis.html",
            {"request": request, "users": users_data}
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

# Database page
@router.get("/database", response_class=HTMLResponse)
async def database(request: Request, session: Session = Depends(get_session)):
    try:
        if not check_database_exists():
            raise HTTPException(
                status_code=500,
                detail="Database file not found. Please ensure the application is properly initialized."
            )
        
        speeches = session.query(Speech).all()
        serialized_speeches = [
            {
                "id": str(speech.id),
                "title": speech.title,
                "content": speech.content,
                "source_type": speech.source_type,
                "created_at": speech.created_at.isoformat(),
                "user_id": str(speech.user_id)
            }
            for speech in speeches
        ]
        
        return templates.TemplateResponse(
            "database.html",
            {"request": request, "speeches": serialized_speeches}
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

# Users page
@router.get("/users", response_class=HTMLResponse)
async def read_users(request: Request, session: Session = Depends(get_session)):
    try:
        if not check_database_exists():
            raise HTTPException(
                status_code=500,
                detail="Database file not found. Please ensure the application is properly initialized."
            )
        
        users = session.query(User).all()
        serialized_users = [
            {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name
            }
            for user in users
        ]
        
        return templates.TemplateResponse(
            "users.html",
            {"request": request, "users": serialized_users}
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

# User speeches page
@router.get("/users/{user_id}/speeches", response_class=HTMLResponse)
async def read_user_speeches(
    request: Request,
    user_id: str,
    session: Session = Depends(get_session)
):
    try:
        if not check_database_exists():
            raise HTTPException(
                status_code=500,
                detail="Database file not found. Please ensure the application is properly initialized."
            )
        
        user_uuid = UUID(user_id)
        user = session.query(User).filter(User.id == user_uuid).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        speeches = session.query(Speech).filter(Speech.user_id == user_uuid).all()
        
        serialized_user = {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name
        }
        
        serialized_speeches = [
            {
                "id": str(speech.id),
                "title": speech.title,
                "content": speech.content,
                "source_type": speech.source_type,
                "created_at": speech.created_at.isoformat()
            }
            for speech in speeches
        ]
        
        return templates.TemplateResponse(
            "user_speeches.html",
            {"request": request, "user": serialized_user, "speeches": serialized_speeches}
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except OperationalError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred. Please ensure the database is properly configured."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")