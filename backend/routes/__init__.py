# routes/__init__.py

# Legacy routes - removed for API-only mode
# Only auth_routes and analyze_routes have some API functionality left

from .auth_routes import router as auth_router

all_routers = [
    auth_router,
]