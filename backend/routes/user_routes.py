# routes/user_routes.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from uuid import UUID
from backend.database.models import User, Speech, SpeechAnalysis
from backend.database.database import get_session

router = APIRouter()

templates = Jinja2Templates(directory="../frontend/templates")

@router.get("/users", response_class=HTMLResponse)
async def read_users(request: Request, session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    serialized_users = [{"id": user.id, "email": user.email} for user in users]
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "users": serialized_users}
    )

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