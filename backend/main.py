from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database.models import Speech, User
from database.database import engine, get_session
from sqlmodel import Session, select
from openai_service import analyze_text_with_gpt
import uuid
from datetime import datetime



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

# Analyze Text Page
@app.get("/analyze-text", response_class=HTMLResponse)
async def analyze_text_form(request: Request):
    return templates.TemplateResponse(
        "analyze_text.html",
        {"request": request}
    )

@app.post("/analyze-text", response_class=JSONResponse)
async def analyze_text(request: Request, text: str = Form(...)):
    try:
        # Analyze the text using OpenAI
        analysis_result = analyze_text_with_gpt(text)

        # Save the speech and analysis to the database
        with get_session() as session:
            speech = Speech(
                id=uuid.uuid4(),
                user_id=None,  # Replace with actual user ID if available
                source_type="text",
                content=text,
                timestamp=datetime.utcnow()
            )
            session.add(speech)
            session.commit()

            # Save the analysis
            speech_analysis = SpeechAnalysis(
                id=uuid.uuid4(),
                speech_id=speech.id,
                word_count=len(text.split()),
                estimated_duration=len(text.split()) / 150,  # Approx. words per minute
                clarity_score=analysis_result["Klarheit"],
                structure_score=analysis_result["Struktur"],
                filler_word_count=analysis_result["Füllwörter"],
                created_at=datetime.utcnow()
            )
            session.add(speech_analysis)
            session.commit()

        return JSONResponse(content={
            "message": "Text successfully analyzed.",
            "analysis": analysis_result
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# File Upload and Analysis
@app.post("/upload-analysis", response_class=JSONResponse)
async def upload_and_analyze(file: UploadFile = File(...)):
    try:
        # Read the uploaded file content
        content = await file.read()
        text = content.decode("utf-8")

        # Analyze the text using OpenAI
        analysis_result = analyze_text_with_gpt(text)

        # Save the speech and analysis to the database
        with get_session() as session:
            speech = Speech(
                id=uuid.uuid4(),
                user_id=None,  # Replace with actual user ID if available
                source_type="text",
                content=text,
                timestamp=datetime.utcnow()
            )
            session.add(speech)
            session.commit()

            # Save the analysis
            speech_analysis = SpeechAnalysis(
                id=uuid.uuid4(),
                speech_id=speech.id,
                word_count=len(text.split()),
                estimated_duration=len(text.split()) / 150,  # Approx. words per minute
                clarity_score=analysis_result["Klarheit"],
                structure_score=analysis_result["Struktur"],
                filler_word_count=analysis_result["Füllwörter"],
                created_at=datetime.utcnow()
            )
            session.add(speech_analysis)
            session.commit()

        return JSONResponse(content={
            "message": "File successfully analyzed.",
            "analysis": analysis_result
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)