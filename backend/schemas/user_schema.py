from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class UserBase(BaseModel):
    """
    Base schema for user-related data.
    """
    email: str = Field(..., description="Email address of the user (must be unique)")

    class Config:
        orm_mode = True  # Enable ORM mode for compatibility with SQLModel/SQLAlchemy

class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """
    hashed_password: str = Field(..., min_length=8, description="Hashed password of the user")

class UserRead(UserBase):
    """
    Schema for returning user data.
    """
    id: UUID = Field(..., description="Unique identifier for the user")

class UserUpdate(BaseModel):
    """
    Schema for updating an existing user.
    """
    email: Optional[str] = Field(None, description="Updated email address")
    hashed_password: Optional[str] = Field(None, description="Updated hashed password")