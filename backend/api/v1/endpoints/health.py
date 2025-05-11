# backend/api/v1/endpoints/health.py

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import time
from backend.middleware import limiter, RateLimits
from backend.config import settings

router = APIRouter()

# Initialize start time for uptime calculation
start_time = time.time()

@router.get("/health")
@limiter.limit(RateLimits.HEALTH_CHECK)
async def health_check(request: Request):
    """
    Health check endpoint for monitoring and load balancers
    
    Returns:
        JSON response with service status, version, and timestamp
    """
    return JSONResponse({
        "status": "healthy",
        "service": "MasterSpeak AI",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENV
    })

@router.get("/status")
@limiter.limit(RateLimits.HEALTH_CHECK)
async def api_status(request: Request):
    """
    Detailed API status information including database connectivity
    
    Returns:
        JSON response with comprehensive system status
    """
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
        "uptime": time.time() - start_time
    })