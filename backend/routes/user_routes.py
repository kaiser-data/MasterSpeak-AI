# routes/user_routes.py

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from backend.database.models import User, Speech
from backend.database.database import get_session
from backend.utils import check_database_exists, serialize_user
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter()

# Configure Jinja2 templates with absolute path
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "templates")
templates = Jinja2Templates(directory=templates_dir)


@router.get("/users", response_class=HTMLResponse)
async def read_users(request: Request, session: AsyncSession = Depends(get_session)):
    """
    Display all users in the system.
    """
    try:
        if not check_database_exists():
            raise HTTPException(
                status_code=500,
                detail="Database file not found. Please ensure the application is properly initialized."
            )
        
        result = await session.execute(select(User))
        users = result.scalars().all()
        serialized_users = [serialize_user(user) for user in users]
        
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

@router.get("/users/{user_id}", response_class=HTMLResponse)
async def read_user(
    request: Request,
    user_id: str,
    session: Session = Depends(get_session)
):
    """
    Display details of a specific user.
    """
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
        
        serialized_user = {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser
        }
        
        return templates.TemplateResponse(
            "user_detail.html",
            {"request": request, "user": serialized_user}
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

@router.get("/users/{user_id}/speeches", response_class=HTMLResponse)
async def read_user_speeches(
    request: Request,
    user_id: str,
    session: Session = Depends(get_session)
):
    """
    Display all speeches for a specific user.
    """
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
                "created_at": speech.created_at.isoformat(),
                "feedback": speech.feedback
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