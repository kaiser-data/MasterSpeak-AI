# routes/__init__.py

from .user_routes import router as user_router
from .database_routes import router as database_router
from .analyze_routes import router as analyze_router
from .general_routes import router as general_router
from .auth_routes import router as auth_router  # Import the auth router

all_routers = [
    user_router,
    database_router,
    analyze_router,
    general_router,
    auth_router,
]