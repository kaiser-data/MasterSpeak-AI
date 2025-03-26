from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database.models import Speech
from database.database import engine, get_session
from sqlmodel import Session, select
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
    return templates.TemplateResponse(
        "database.html",
        {"request": request, "speeches": speeches}
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
