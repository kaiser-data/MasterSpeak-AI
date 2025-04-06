# backend/main.py

from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database.models import Speech, SpeechAnalysis, User
from database.database import get_session
from sqlmodel import Session, select
from pydantic import BaseModel

import uuid
from datetime import datetime
from openai_service import analyze_text_with_gpt

app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory="../frontend/templates")

# Hardcoded default user ID
DEFAULT_USER_ID = "52c3a53197a94910b78b3b858b63bf71"

# Pydantic model for request body
class AnalyzeRequest(BaseModel):
    user_id: str  # UUID of the user
    content: str  # Text to analyze
    source_type: str = "text"  # Default source type is 'text'

# --- Home Page ---
@app.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# --- Database Page ---
@app.get("/database", response_class=HTMLResponse)
async def read_database(request: Request, session: Session = Depends(get_session)):
    speeches = session.exec(select(Speech)).all()
    serialized_speeches = [speech.dict() for speech in speeches]
    return templates.TemplateResponse(
        "database.html",
        {"request": request, "speeches": serialized_speeches}
    )

# --- Analyze Text Page ---
@app.get("/analyze-text", response_class=HTMLResponse)
async def analyze_text_form(request: Request):
    return templates.TemplateResponse("analyze_text.html", {"request": request})

@app.post("/analyze-text", response_class=JSONResponse)
async def analyze_text(request: Request, text: str = Form(...), prompt_type: str = Form("default")):
    try:
        # Analyze the text using OpenAI with the specified prompt
        analysis_result = analyze_text_with_gpt(text, prompt_type)

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
                clarity_score=analysis_result["Clarity"],
                structure_score=analysis_result["Structure"],
                filler_word_count=analysis_result["Filler Words"],
                prompt=prompt_type,  # Store the prompt type
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


@app.get("/api/users/")
async def get_users(session: Session = Depends(get_session)):
    """
    Fetch all users from the database.
    """
    users = session.exec(select(User)).all()
    return [{"id": user.id, "email": user.email} for user in users]

# --- File Upload and Analysis ---
@app.get("/upload-analysis", response_class=HTMLResponse)
async def read_upload_analysis(request: Request):
    return templates.TemplateResponse("upload_analysis.html", {"request": request})

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
                clarity_score=analysis_result["Clarity"],
                structure_score=analysis_result["Structure"],
                filler_word_count=analysis_result["Filler Words"],
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

# --- Users Page ---
@app.get("/users", response_class=HTMLResponse)
async def read_users(request: Request):
    with get_session() as session:
        users = session.exec(select(User)).all()
        serialized_users = [{"id": user.id, "email": user.email} for user in users]
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "users": serialized_users}
    )
@app.get("/users/{user_id}/speeches", response_class=HTMLResponse)
async def read_user_speeches(
    request: Request,
    user_id: str,
    session: Session = Depends(get_session)
):
    try:
        # Convert the user_id string to a UUID object
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Invalid user ID format"}
        )
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
        {"request": request, "user": serialized_user, "speeches": serialized_speeches}
    )
# --- About and Contact Pages ---
@app.get("/about", response_class=HTMLResponse)
async def read_about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def read_contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.post("/api/speech/")
async def create_speech(
    user_id: str,
    content: str,
    source_type: str = "text",
    session: Session = Depends(get_session)
):
    """
    Create a new speech entry in the database and analyze the content.
    """
    user_id = DEFAULT_USER_ID
    # Fetch the user from the database
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Analyze the text using OpenAI
    try:
        analysis_result = analyze_text_with_gpt(content, prompt_type="default")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing text: {str(e)}")

    # Save the speech to the database
    speech = Speech(
        user_id=user.id,
        source_type=source_type,
        content=content,
        timestamp=datetime.utcnow()
    )
    session.add(speech)
    session.commit()
    session.refresh(speech)

    # Save the analysis results to the database
    speech_analysis = SpeechAnalysis(
        speech_id=speech.id,
        word_count=len(content.split()),
        estimated_duration=len(content.split()) / 150,  # Approx. 150 words per minute
        clarity_score=analysis_result.get("Clarity", 0),
        structure_score=analysis_result.get("Structure", 0),
        filler_word_count=analysis_result.get("Filler_Words", 0),
        prompt="Analyze the following text and return the result as JSON.",
        created_at=datetime.utcnow()
    )
    session.add(speech_analysis)
    session.commit()
    session.refresh(speech_analysis)

    # Format the result as Markdown
    markdown_result = "### Analysis Result:\n\n"
    for key, value in analysis_result.items():
        markdown_result += f"- **{key}**: {value}\n"

    return {"markdown_result": markdown_result, "json_result": analysis_result}


@app.post("/analyze-text")
async def analyze_text(request: AnalyzeRequest, session: Session = Depends(get_session)):
    """
    Analyze the provided text using OpenAI, save the result to the database,
    and return the result in Markdown format.
    """
    try:
        # Fetch the user from the database (assuming a default user for simplicity)
        user = session.exec(select(User).where(User.id == "default_user_id")).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Analyze the text using OpenAI
        analysis_result = analyze_text_with_gpt(request.text, prompt_type="default")

        # Save the speech to the database
        speech = Speech(
            user_id=user.id,
            source_type="text",
            content=request.text,
            timestamp=datetime.utcnow()
        )
        session.add(speech)
        session.commit()
        session.refresh(speech)

        # Save the analysis results to the database
        speech_analysis = SpeechAnalysis(
            speech_id=speech.id,
            word_count=len(request.text.split()),
            estimated_duration=len(request.text.split()) / 150,
            clarity_score=analysis_result.get("Clarity", 0),
            structure_score=analysis_result.get("Structure", 0),
            filler_word_count=analysis_result.get("Filler_Words", 0),
            prompt="Analyze the following text and return the result as JSON.",
            created_at=datetime.utcnow()
        )
        session.add(speech_analysis)
        session.commit()
        session.refresh(speech_analysis)

        # Format the result as Markdown
        markdown_result = "### Analysis Result:\n\n"
        for key, value in analysis_result.items():
            markdown_result += f"- **{key}**: {value}\n"

        return {"markdown_result": markdown_result, "json_result": analysis_result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing text: {str(e)}")


