# routes/database_routes.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database.models import Speech
from database.database import get_session

router = APIRouter()

templates = Jinja2Templates(directory="../frontend/templates")

@router.get("/database", response_class=HTMLResponse)
async def read_database(request: Request, session: Session = Depends(get_session)):
    speeches = session.exec(select(Speech)).all()
    serialized_speeches = [speech.dict() for speech in speeches]
    return templates.TemplateResponse(
        "database.html",
        {"request": request, "speeches": serialized_speeches}
    )