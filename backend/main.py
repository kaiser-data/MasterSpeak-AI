# main.py

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
import time
try:
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from backend.middleware import limiter, rate_limit_exceeded_handler, RateLimits
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    print("SlowAPI not available - rate limiting disabled")
    RATE_LIMITING_AVAILABLE = False
    limiter = None
    RateLimits = None
from backend.routes import all_routers
from backend.api.v1 import api_router
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

app = FastAPI(
    title="MasterSpeak AI",
    description="Advanced Speech Analysis API with AI-powered feedback",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add rate limiting (if available)
if RATE_LIMITING_AVAILABLE:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Configure CORS with secure settings
allowed_origins = [
    origin.strip() 
    for origin in settings.ALLOWED_ORIGINS.split(",")
    if origin.strip()
]

# Add wildcard for development
if settings.ENV == "development":
    allowed_origins.append("http://localhost:*")

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"] if settings.ENV == "development" else ["yourdomain.com"]
)

# Request logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response

# Global exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

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

# Health check endpoint
@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint for monitoring and load balancers"""
    return JSONResponse({
        "status": "healthy",
        "service": "MasterSpeak AI",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENV
    })

# API status endpoint
@app.get("/api/status")
async def api_status(request: Request):
    """Detailed API status information"""
    try:
        # Test database connection
        from backend.database.database import get_session
        async with get_session() as session:
            await session.execute("SELECT 1")
            db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return JSONResponse({
        "api": "online",
        "database": db_status,
        "version": "1.0.0",
        "environment": settings.ENV,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": time.time() - getattr(api_status, 'start_time', time.time())
    })

# Initialize start time for uptime calculation
api_status.start_time = time.time()

# Root route - redirect to home
@app.get("/")
async def root():
    return RedirectResponse(url="/home")

# Include API v1 router (RESTful JSON API)
app.include_router(api_router, prefix="/api/v1")

# Include legacy HTML routers (for backward compatibility)
for router in all_routers:
    app.include_router(router)