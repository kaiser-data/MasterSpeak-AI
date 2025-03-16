from fastapi_users import FastAPIUsers, UserManager
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.models import BaseUserDB
from fastapi_users.password import PasswordHelper
from .models import User
from .database import engine, SessionLocal

user_db = SQLAlchemyUserDatabase(User, SessionLocal())

class UserManager(UserManager[User]):
    user_db_model = User

fastapi_users = FastAPIUsers(
    user_db,
    UserManager,
    User,
    BaseUserDB,
    PasswordHelper(),
)

auth_backend = fastapi_users.auth.jwt.JWTAuthentication(
    secret="SECRET", lifetime_seconds=3600
)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth")
