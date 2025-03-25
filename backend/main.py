from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory="../frontend/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Render the main page with sample data.
    """
    # Simulate some dynamic data
    speeches = [
        {"id": 1, "clarity_score": 8, "structure_score": 7, "filler_word_count": 5},
        {"id": 2, "clarity_score": 9, "structure_score": 6, "filler_word_count": 3},
    ]
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "speeches": speeches,
            "current_user": {"is_authenticated": True},  # Simulate logged-in user
        },
    )