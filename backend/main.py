from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database.models import Speech, User
from database.database import engine, get_session
from sqlmodel import Session, select
from uuid import UUID  # Import UUID

app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory="../frontend/templates")

# Root/Home Page
@app.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})



# Database Page
@app.get("/database", response_class=HTMLResponse)
async def read_database(request: Request):
    # Query all entries from the database using the session context manager
    with get_session() as session:
        speeches = session.exec(select(Speech)).all()  # Fetch all Speech records
        # Serialize the Speech objects into dictionaries
        serialized_speeches = [speech.dict() for speech in speeches]
    return templates.TemplateResponse(
        "database.html",
        {"request": request, "speeches": serialized_speeches}
    )
# Upload & Analysis Page
@app.get("/upload-analysis", response_class=HTMLResponse)
async def read_upload_analysis(request: Request):
    return templates.TemplateResponse("upload_analysis.html", {"request": request})

# About Page
@app.get("/about", response_class=HTMLResponse)
async def read_about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

# Contact Page
@app.get("/contact", response_class=HTMLResponse)
async def read_contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

# Users Page
@app.get("/users", response_class=HTMLResponse)
async def read_users(request: Request):
    with get_session() as session:
        users = session.exec(select(User)).all()  # Fetch all users
        # Serialize users into dictionaries
        serialized_users = [user.dict() for user in users]
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "users": serialized_users}
    )

@app.get("/users/{user_id}/speeches", response_class=HTMLResponse)
async def read_user_speeches(request: Request, user_id: str):
    try:
        # Convert the user_id string to a UUID object
        user_uuid = UUID(user_id)
    except ValueError:
        # Handle invalid UUID format
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Invalid user ID format"}
        )

    with get_session() as session:
        # Fetch the user by UUID
        user = session.get(User, user_uuid)
        if not user:
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "message": "User not found"}
            )
        # Serialize the user and their speeches
        serialized_user = {
            "id": user.id,
            "email": user.email,
        }
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
        {"request": request, "user": serialized_user, "speeches": serialized_speeches})