from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from backend.database.database import init_db  # Assuming `engine` is defined in `database.py`
from backend.routes.routes import router as speech_router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan event manager for resource initialization and cleanup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events.
    - Initializes the database on startup.
    - Cleans up resources on shutdown (if needed).
    """
    logger.info("Starting up the application...")
    init_db()
    yield
    logger.info("Shutting down the application...")

# Initialize FastAPI app with lifespan management
app = FastAPI(
    title="Speech Analysis API",
    version="1.0",
    lifespan=lifespan,
)

# Root Endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint to welcome users.
    """
    return {"message": "Welcome to the Speech Analysis API"}

# Personalized Hello Endpoint
@app.get("/hello/{name}", tags=["Greetings"])
async def say_hello(name: str):
    """
    A personalized greeting endpoint.
    """
    if not name.strip():  # Validate input
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    return {"message": f"Hello {name}"}

# Include Speech Analysis Routes
app.include_router(speech_router, prefix="/speech", tags=["Speech Analysis"])

# Health Check Endpoint (Optional but recommended for monitoring)
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the application is running.
    """
    return {"status": "healthy"}