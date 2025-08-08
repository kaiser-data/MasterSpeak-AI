# main.py

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
import time
import os
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
    # Create mock exception class for when slowapi is not available
    class RateLimitExceeded(Exception):
        pass
    rate_limit_exceeded_handler = None
from backend.routes import all_routers, auth_router, analyze_router
from backend.api.v1 import api_router
from backend.database.database import init_db, engine, get_session
from backend.seed_db import seed_database
from backend.config import settings
from pathlib import Path
import logging
import asyncio
from contextlib import asynccontextmanager
from backend.logging_config import setup_logging, generate_request_id, set_request_id, log_performance_event

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup with robust logging
    process_start_time = time.time()
    app.state.process_start_time = process_start_time
    logger.info("==> Starting MasterSpeak API (API-only mode)")
    
    # Optional DB health check during startup
    db_ok = None
    if os.getenv("HEALTHCHECK_DB", "false").lower() == "true":
        try:
            logger.info("DB ping: Testing connection...")
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
            db_ok = True
            logger.info("DB ping: OK")
        except Exception as e:
            db_ok = False
            logger.warning("DB ping: FAILED (%s) — continuing startup", e)
    
    try:
        await init_db()
        logger.info("Database tables initialized")
        
        # Run migration for is_verified column
        try:
            from backend.migrations.add_is_verified import migrate_add_is_verified
            await migrate_add_is_verified()
        except Exception as e:
            logger.warning(f"Migration failed (continuing startup): {e}")
        
        await seed_database()
        logger.info("Database seeded")
        
        logger.info("==> MasterSpeak API ready for requests")
        
        yield
        
        # Shutdown
        logger.info("<== Shutting down MasterSpeak API")
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
if RATE_LIMITING_AVAILABLE and rate_limit_exceeded_handler:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Add security middleware first
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.trusted_hosts
)

# Add CORS middleware second (before other middleware and routers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_origin_regex=settings.ALLOWED_ORIGIN_REGEX,
    allow_credentials=False,  # Keep False unless we truly use cookies
    allow_methods=["*"],      # Includes OPTIONS
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

logger.info(f"Environment: {settings.ENV}")
logger.info(f"Trusted hosts: {settings.trusted_hosts}")
logger.info(f"CORS allowed origins: {settings.allowed_origins}")
logger.info(f"CORS origin regex: {settings.ALLOWED_ORIGIN_REGEX}")

# Log more detailed CORS configuration for debugging
logger.info("CORS configured with:")
logger.info(f"  - Origins: {settings.allowed_origins}")
logger.info(f"  - Regex pattern: {settings.ALLOWED_ORIGIN_REGEX}")
logger.info(f"  - Allow credentials: False")
logger.info(f"  - Allow methods: *")
logger.info(f"  - Allow headers: *")

# Request logging and tracing middleware
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    # Skip processing for OPTIONS requests (preflight) - let CORS handle it
    if request.method == "OPTIONS":
        return await call_next(request)
    
    # Generate and set request ID
    request_id = generate_request_id()
    set_request_id(request_id)
    
    # Add request ID to request state for access in handlers
    request.state.request_id = request_id
    
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    
    # Log request with structured data
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={
            'event_type': 'request_start',
            'method': request.method,
            'path': request.url.path,
            'client_ip': client_ip,
            'user_agent': request.headers.get('user-agent', 'unknown'),
            'request_id': request_id
        }
    )
    
    response = await call_next(request)
    
    # Calculate response time
    process_time = time.time() - start_time
    process_time_ms = process_time * 1000
    
    # Log response with structured data  
    logger.info(
        f"Response: {response.status_code} - {process_time_ms:.2f}ms",
        extra={
            'event_type': 'request_complete',
            'method': request.method,
            'path': request.url.path,
            'status_code': response.status_code,
            'response_time_ms': process_time_ms,
            'client_ip': client_ip,
            'request_id': request_id
        }
    )
    
    # Log performance metrics for slow requests
    if process_time_ms > 500:  # Slow request threshold
        log_performance_event(
            endpoint=request.url.path,
            response_time_ms=process_time_ms,
            status_code=response.status_code,
            method=request.method
        )
    
    # Add request ID to response headers for debugging
    response.headers["X-Request-ID"] = request_id
    
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

# CORS middleware already added above - removed duplicate

# API-only mode: no static files or templates
logger.info("Running in API-only mode - no static files or templates")

# Health check endpoint
@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint for monitoring and load balancers"""
    try:
        uptime_seconds = time.time() - getattr(app.state, 'process_start_time', time.time())
        
        health_data = {
            "status": "ok",
            "service": "MasterSpeak AI",
            "version": "1.0.0",
            "uptime_seconds": round(uptime_seconds, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "environment": settings.ENV
        }
        
        # Optional DB check only if flag is set
        if os.getenv("HEALTHCHECK_DB", "false").lower() == "true":
            try:
                async with get_session() as session:
                    await session.execute("SELECT 1")
                health_data["db_ok"] = True
            except Exception:
                health_data["db_ok"] = False
        
        return JSONResponse(health_data)
    except Exception as e:
        # Never crash /health
        logger.error(f"Health check error: {e}")
        return JSONResponse({
            "status": "ok", 
            "error": "health_check_failed",
            "timestamp": datetime.utcnow().isoformat()
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

# Root route - redirect to API documentation
@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

# Include JSON API routers only
app.include_router(api_router, prefix="/api/v1")
app.include_router(auth_router)
app.include_router(analyze_router)
logger.info("API-only routers loaded: auth, analyze, api/v1")