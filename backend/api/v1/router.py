# backend/api/v1/router.py

from fastapi import APIRouter
from .endpoints import health, auth, analysis, users, speeches, transcription, export, share
from .endpoints.analysis_alias import router as analysis_alias_router
from .routes import analyses

api_router = APIRouter()

# Health endpoints (no prefix needed)
api_router.include_router(
    health.router,
    tags=["Health"]
)

# Authentication endpoints  
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Analysis endpoints
api_router.include_router(
    analysis.router, 
    prefix="/analysis",
    tags=["Analysis"]
)

# User management endpoints
api_router.include_router(
    users.router,
    prefix="/users", 
    tags=["Users"]
)

# Speech management endpoints
api_router.include_router(
    speeches.router,
    prefix="/speeches",
    tags=["Speeches"]
)

# Transcription endpoints
api_router.include_router(
    transcription.router,
    prefix="/transcription",
    tags=["Transcription"]
)

# Analyses list endpoints (Agent C)
api_router.include_router(
    analyses.router,
    prefix="/analyses",
    tags=["Analyses"]
)

# Export endpoints (Agent D)
api_router.include_router(
    export.router,
    prefix="/analyses",
    tags=["Export"]
)

# Share endpoints (Agent D)
api_router.include_router(
    share.router,
    prefix="/share",
    tags=["Share"]
)

# Analysis alias endpoints (DISABLED - causing duplicate routes)
# The main analysis.router already provides /api/v1/analysis/text
# api_router.include_router(
#     analysis_alias_router,
#     tags=["Analysis-Alias"]
# )