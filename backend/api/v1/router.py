# backend/api/v1/router.py

from fastapi import APIRouter
from .endpoints import health, auth, analysis, users, speeches
from .endpoints.analysis_alias import router as analysis_alias_router

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

# Analysis alias endpoints (DISABLED - causing duplicate routes)
# The main analysis.router already provides /api/v1/analysis/text
# api_router.include_router(
#     analysis_alias_router,
#     tags=["Analysis-Alias"]
# )