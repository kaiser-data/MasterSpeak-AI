# main.py

import os
import uuid
import logging
from typing import Callable, Awaitable, Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.datastructures import Headers
import re
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
    # Create mock exception class for when slowapi is not available
    class RateLimitExceeded(Exception):
        pass
    rate_limit_exceeded_handler = None
from backend.routes import all_routers, auth_router, analyze_router
from backend.api.v1 import api_router
from backend.debug_routes import router as debug_router
from backend.simple_analysis_routes import router as simple_router
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
    
    # Log deployment verification info
    commit_sha = os.getenv("RAILWAY_GIT_COMMIT_SHA", os.getenv("COMMIT_SHA", "unknown"))
    logger.info(f"🚀 Deployment Info: COMMIT_SHA={commit_sha}")
    
    # Verify schema and route registration
    from fastapi.routing import APIRoute
    try:
        from backend.schemas.analysis_schema import AnalyzeTextRequest
        fld = AnalyzeTextRequest.model_fields.get("user_id")
        logger.info("🔍 AnalyzeTextRequest.user_id required=%s", getattr(fld, "is_required", None))
    except Exception as e:
        logger.warning("Schema introspection failed: %r", e)

    def _log_text_route():
        for r in app.routes:
            if isinstance(r, APIRoute) and r.path == "/api/v1/analysis/text":
                logger.info("🔗 /api/v1/analysis/text -> %s.%s methods=%s",
                           r.endpoint.__module__, r.endpoint.__name__, sorted(r.methods))
    app.add_event_handler("startup", _log_text_route)

    try:
        await init_db()
        logger.info("Database tables initialized")
        
        # Run migration for is_verified column
        try:
            from backend.migrations.add_is_verified import migrate_add_is_verified
            await migrate_add_is_verified()
        except Exception as e:
            logger.warning(f"Migration failed (continuing startup): {e}")
        
        try:
            await seed_database()
            logger.info("Database seeded")
        except Exception as e:
            logger.warning(f"Database seeding failed (continuing startup): {e}")
            # Continue startup even if seeding fails
        
        logger.info("==> MasterSpeak API ready for requests")
        
        yield
        
        # Shutdown
        logger.info("<== Shutting down MasterSpeak API")
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during startup/shutdown: {str(e)}")
        raise

# ── CORS (edit ALLOWED_ORIGINS via env) ────────────────────────────────────────
# Example: ALLOWED_ORIGINS="https://<VERCEL_DOMAIN>,http://localhost:3000"
ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://master-speak-ai.vercel.app").split(",") if o.strip()
]

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    expose_headers=["X-Request-ID"],
)
# Trust Railway proxy and localhost - expand trusted_hosts to include Railway domain
trusted_hosts = settings.trusted_hosts + ["masterspeak-ai-production.up.railway.app"]
app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

logger.info(f"Environment: {settings.ENV}")
logger.info(f"Trusted hosts: {settings.trusted_hosts}")
logger.info(f"CORS allowed origins: {ALLOWED_ORIGINS}")

# ── Helpers: restore body so downstream can read it ────────────────────────────
async def _set_body(request: Request, body: bytes) -> None:
    async def receive() -> Dict[str, Any]:
        return {"type": "http.request", "body": body, "more_body": False}
    # Starlette private API, but canonical for re-injecting the body
    request._receive = receive  # type: ignore[attr-defined]

# ── Hardened middleware (replaces your current request_middleware) ─────────────
@app.middleware("http")
async def request_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    # Buffer body for methods that usually send one, then restore it
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        body = await request.body()
        request.state.body = body
        await _set_body(request, body)
    try:
        response = await call_next(request)
    except Exception as e:
        logging.exception("X-Request-ID=%s %s %s crashed", request_id, request.method, request.url.path)
        raise
    # Tag every successful response so the UI can show request IDs in Network tab
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
    logger.exception(f"Validation error on {request.url.path}: {exc.errors()}")
    request_id = getattr(request.state, 'request_id', 'unknown')
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Add generic exception handler for 500 errors to log stack traces
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error on {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
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
                from sqlalchemy import text
                async with AsyncSessionLocal() as session:
                    await session.execute(text("SELECT 1"))
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
        from backend.database.database import AsyncSessionLocal
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        db_status = f"disconnected: {str(e)[:100]}"
    
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

# DEBUG: Test endpoint to verify response format
@app.get("/api/v1/test-analysis-response")
async def test_analysis_response():
    """Return test analysis response in exact format frontend expects"""
    return JSONResponse({
        "success": True,
        "speech_id": "test-speech-id-12345",
        "analysis": {
            "clarity_score": 8,
            "structure_score": 7,
            "filler_word_count": 3,
            "feedback": "🧪 TEST: This is a test feedback message to verify the frontend display is working correctly. If you can see this, the frontend component is working and the issue is in the API call flow."
        }
    })

# Include JSON API routers only
app.include_router(api_router, prefix="/api/v1")
app.include_router(auth_router)
# app.include_router(analyze_router)  # DISABLED: legacy routes, conflicts with /api/v1
app.include_router(debug_router, prefix="/debug")
# app.include_router(simple_router)  # DISABLED: legacy simple routes, use /api/v1 instead
logger.info("API-only routers loaded: auth, api/v1, debug (legacy analyze/simple disabled)")