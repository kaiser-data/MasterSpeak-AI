from fastapi_users import schemas
from pydantic import Field
from uuid import UUID
from typing import Optional

# Use FastAPIUsers base schemas for proper registration
class UserRead(schemas.BaseUser[UUID]):
    """Schema for returning user data"""
    full_name: Optional[str] = None
    is_verified: Optional[bool] = None

class UserCreate(schemas.BaseUserCreate):
    """Schema for creating a new user"""
    full_name: Optional[str] = None
    is_verified: Optional[bool] = False

class UserUpdate(schemas.BaseUserUpdate):
    """Schema for updating user data"""
    full_name: Optional[str] = None