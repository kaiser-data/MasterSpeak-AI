# main.py

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import all_routers
from backend.database.database import init_db, engine
from backend.seed_db import seed_database
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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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