# main.py

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import all_routers
from backend.database.database import init_db, engine
from backend.seed_db import seed_database
from backend.config import settings
from pathlib import Path
import logging
import asyncio
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        logger.info("Starting database initialization...")
        await init_db()
        logger.info("Database initialized successfully")
        
        logger.info("Starting database seeding...")
        await seed_database()
        logger.info("Database seeded successfully")
        
        yield
        
        # Shutdown
        logger.info("Shutting down database connections...")
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during startup/shutdown: {str(e)}")
        raise

app = FastAPI(lifespan=lifespan)

# Configure CORS with secure settings
allowed_origins = [
    origin.strip() 
    for origin in settings.ALLOWED_ORIGINS.split(",")
    if origin.strip()
]

# Add wildcard for development
if settings.ENV == "development":
    allowed_origins.append("http://localhost:*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["Content-Length", "X-Total-Count"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Configure templates
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "frontend" / "templates"))

# Mount static files directory
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "frontend" / "static")), name="static")

# Root route - redirect to home
@app.get("/")
async def root():
    return RedirectResponse(url="/home")

# Include all routers
for router in all_routers:
    app.include_router(router)