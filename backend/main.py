# main.py

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from backend.routes import all_routers
from backend.database.database import init_db, engine
from backend.seed_db import seed_database
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Starting database initialization...")
        init_db()
        logger.info("Database initialized successfully")
        
        logger.info("Starting database seeding...")
        seed_database()
        logger.info("Database seeded successfully")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

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

# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down database connections...")
    engine.dispose()
    logger.info("Database connections closed")