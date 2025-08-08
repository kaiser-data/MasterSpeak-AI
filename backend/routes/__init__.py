# routes/__init__.py

# API-only mode - legacy HTML routes removed

from .auth_routes import router as auth_router
from .analyze_routes import router as analyze_router

all_routers = [
    auth_router,
    analyze_router,
]