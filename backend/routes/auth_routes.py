from fastapi import APIRouter, Depends, Request
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, JWTStrategy, CookieTransport
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from uuid import UUID
from fastapi_users.manager import BaseUserManager
import logging

from backend.database.models import User
from backend.database.database import AsyncSessionLocal
from backend.schemas.user_schema import UserRead, UserCreate, UserUpdate
from backend.config import settings
from backend.services.email_service import email_service
try:
    from backend.middleware import limiter, RateLimits
except ImportError:
    # Mock limiter for when slowapi is not available
    class MockLimiter:
        def limit(self, limit_string):
            def decorator(func):
                return func
            return decorator
    limiter = MockLimiter()
    RateLimits = type('RateLimits', (), {
        'API_READ': '30/minute',
        'AUTH_LOGIN': '5/minute',
        'AUTH_REGISTER': '3/minute', 
        'AUTH_RESET_PASSWORD': '2/minute'
    })()

logger = logging.getLogger(__name__)

# Dependency to get the user DB with async session
async def get_user_db() -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield SQLAlchemyUserDatabase(session, User)  # Correct order: session first, then User model
        finally:
            pass  # Session cleanup handled by context manager

# Custom UserManager with secure configuration
class UserManager(BaseUserManager[User, UUID]):
    reset_password_token_secret = settings.RESET_SECRET
    verification_token_secret = settings.VERIFICATION_SECRET

    async def on_after_register(self, user: User, request=None):
        logger.info(f"User {user.id} has registered.")
        # Auto-verify user on registration (email verification disabled for now)
        if not user.is_verified:
            user.is_verified = True
            logger.info(f"User {user.email} auto-verified on registration")
        # Email verification disabled - users can sign in immediately

    async def on_after_forgot_password(self, user: User, token: str, request=None):
        logger.info(f"User {user.id} requested a password reset.")
        # Send password reset email
        try:
            success = email_service.send_password_reset_email(
                to_email=user.email,
                token=token,
                user_name=user.full_name
            )
            if success:
                logger.info(f"Password reset email sent to {user.email}")
            else:
                logger.warning(f"Failed to send password reset email to {user.email}")
        except Exception as e:
            logger.error(f"Error sending password reset email to {user.email}: {e}")

    async def on_after_request_verify(self, user: User, token: str, request=None):
        logger.info(f"User {user.id} requested email verification.")
        # Send verification email
        try:
            success = email_service.send_verification_email(
                to_email=user.email,
                token=token,
                user_name=user.full_name
            )
            if success:
                logger.info(f"Verification email sent to {user.email}")
            else:
                logger.warning(f"Failed to send verification email to {user.email}")
        except Exception as e:
            logger.error(f"Error sending verification email to {user.email}: {e}")

# Dependency to get the UserManager
async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

# JWT Strategy with secure configuration
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.SECRET_KEY,
        lifetime_seconds=settings.JWT_LIFETIME_SECONDS
    )

# Auth Backend with secure configuration
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=CookieTransport(
        cookie_name="access_token",
        cookie_max_age=settings.JWT_LIFETIME_SECONDS,
        cookie_secure=settings.ENV == "production",  # Secure cookies in production
        cookie_httponly=True,  # Prevent XSS attacks
        cookie_samesite="lax"  # CSRF protection
    ),
    get_strategy=get_jwt_strategy,
)

# FastAPIUsers instance
fastapi_users = FastAPIUsers[User, UUID](
    get_user_manager=get_user_manager,
    auth_backends=[auth_backend],
)

# Define a router for authentication routes
router = APIRouter()

# Include FastAPIUsers authentication routes
router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Custom routes
@router.get("/users/me", response_model=UserRead)
@limiter.limit(RateLimits.API_READ)
async def read_current_user(
    request: Request,
    user: User = Depends(fastapi_users.current_user(active=True))
):
    return user

# Export the router
__all__ = ["router", "fastapi_users"]