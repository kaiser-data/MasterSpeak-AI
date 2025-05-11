# backend/api/v1/endpoints/users.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from backend.database.models import User, Speech
from backend.database.database import get_session
from backend.schemas.user_schema import UserRead
from backend.middleware import limiter, RateLimits
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[UserRead], summary="Get All Users")
@limiter.limit(RateLimits.API_READ)
async def get_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
) -> List[UserRead]:
    """
    Get all users with pagination
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[UserRead]: List of users
    """
    try:
        result = await session.execute(
            select(User).offset(skip).limit(limit).order_by(User.email)
        )
        users = result.scalars().all()
        return users
    except Exception as e:
        logger.error(f"Error in get_users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=UserRead, summary="Get User by ID")
@limiter.limit(RateLimits.API_READ)
async def get_user(
    request: Request,
    user_id: UUID,
    session: AsyncSession = Depends(get_session)
) -> UserRead:
    """
    Get a specific user by ID
    
    Args:
        user_id: UUID of the user
        
    Returns:
        UserRead: User information
    """
    try:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/statistics", summary="Get User Statistics")
@limiter.limit(RateLimits.API_READ)
async def get_user_statistics(
    request: Request,
    user_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """
    Get statistics for a specific user
    
    Args:
        user_id: UUID of the user
        
    Returns:
        Dict with user statistics
    """
    try:
        # Verify user exists
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get speech count
        speech_result = await session.execute(
            select(Speech).where(Speech.user_id == user_id)
        )
        speeches = speech_result.scalars().all()
        
        # Calculate statistics
        total_speeches = len(speeches)
        total_words = sum(len(speech.content.split()) for speech in speeches)
        avg_words = total_words / total_speeches if total_speeches > 0 else 0

        return {
            "user_id": user_id,
            "email": user.email,
            "full_name": user.full_name,
            "total_speeches": total_speeches,
            "total_words_analyzed": total_words,
            "average_words_per_speech": round(avg_words, 2),
            "is_active": user.is_active,
            "created_at": user.created_at if hasattr(user, 'created_at') else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_user_statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))