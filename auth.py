from fastapi import FastAPI
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.manager import BaseUserManager
from fastapi_users.models import BaseUserDB
from fastapi_users.password import PasswordHelper
from sqlalchemy.orm import sessionmaker
from .models import User  # Replace with your actual User model
from .database import engine

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a session factory for database connections
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize SQLAlchemyUserDatabase for user management
user_db = SQLAlchemyUserDatabase(User, SessionLocal)

# Custom UserManager class
class UserManager(BaseUserManager[User, BaseUserDB]):
    """
    Custom user manager to handle user-related operations.
    """
    user_db_model = User
    reset_password_token_secret = "RESET_SECRET"  # Use environment variables in production
    verification_token_secret = "VERIFICATION_SECRET"  # Use environment variables in production

    async def on_after_register(self, user: User, request=None):
        """
        Actions to perform after a user registers.
        """
        logger.info(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user: User, token: str, request=None):
        """
        Actions to perform after a user requests a password reset.
        """
        logger.info(f"User {user.id} requested a password reset. Token: {token}")

    async def on_after_request_verify(self, user: User, token: str, request=None):
        """
        Actions to perform after a user requests email verification.
        """
        logger.info(f"User {user.id} requested email verification. Token: {token}")

# Initialize FastAPIUsers
fastapi_users = FastAPIUsers(
    user_db,
    [JWTAuthentication(secret="SECRET", lifetime_seconds=3600)],  # Use environment variables in production
    User,
    BaseUserDB,
    PasswordHelper(),
    UserManager,
)

# Authentication backends
auth_backend = fastapi_users.auth_backends[0]  # JWTAuthentication backend

# Include authentication routes in the FastAPI app
def include_auth_routes(app: FastAPI):
    """
    Include authentication routes in the FastAPI application.
    """
    app.include_router(
        fastapi_users.get_auth_router(auth_backend),
        prefix="/auth",
        tags=["Auth"],
    )
    app.include_router(
        fastapi_users.get_register_router(),
        prefix="/auth",
        tags=["Auth"],
    )
    app.include_router(
        fastapi_users.get_reset_password_router(),
        prefix="/auth",
        tags=["Auth"],
    )
    app.include_router(
        fastapi_users.get_verify_router(),
        prefix="/auth",
        tags=["Auth"],
    )

# Example usage
# In your main.py, call `include_auth_routes(app)` to add authentication routes