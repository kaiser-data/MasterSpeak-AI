from fastapi import APIRouter, Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, JWTStrategy, CookieTransport
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from uuid import UUID
from fastapi_users.manager import BaseUserManager

from database.models import User  # Your SQLAlchemy user model
from database.database import engine  # Your SQLAlchemy engine
from schemas.user_schema import UserRead, UserCreate, UserUpdate  # Import Pydantic schemas

# Create a session factory for database connections
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the user DB
async def get_user_db() -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    db = SessionLocal()
    try:
        yield SQLAlchemyUserDatabase(User, db)
    finally:
        db.close()

# Custom UserManager
class UserManager(BaseUserManager[User, UUID]):
    reset_password_token_secret = "RESET_SECRET"  # Use environment variables in production
    verification_token_secret = "VERIFICATION_SECRET"  # Use environment variables in production

    async def on_after_register(self, user: User, request=None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user: User, token: str, request=None):
        print(f"User {user.id} requested a password reset. Token: {token}")

    async def on_after_request_verify(self, user: User, token: str, request=None):
        print(f"User {user.id} requested email verification. Token: {token}")

# Dependency to get the UserManager
async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

# JWT Strategy
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret="SECRET", lifetime_seconds=3600)  # Use environment variables in production

# Auth Backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=CookieTransport(cookie_name="access_token", cookie_max_age=3600),
    get_strategy=get_jwt_strategy,
)

# FastAPIUsers instance
fastapi_users = FastAPIUsers[User, UUID](
    get_user_manager=get_user_manager,
    auth_backends=[auth_backend],
)

# Define a router for authentication routes
router = APIRouter()

# Include authentication routes
@router.get("/users/me", response_model=UserRead)
async def read_current_user(user: User = Depends(fastapi_users.current_user(active=True))):
    return user

# Export the router
__all__ = ["router"]