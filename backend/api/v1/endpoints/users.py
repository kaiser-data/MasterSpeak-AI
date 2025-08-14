# backend/api/v1/endpoints/users.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from backend.database.models import User, Speech, SpeechAnalysis
from backend.database.database import get_session
from backend.schemas.user_schema import UserRead
from backend.middleware import limiter, RateLimits
from backend.routes.auth_routes import fastapi_users
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

# Admin endpoints for user management
@router.get("/admin/count", summary="Get User Count (Admin)")
@limiter.limit(RateLimits.API_READ)
async def get_user_count(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    """
    Get total number of users (superuser only)
    
    Returns:
        Dict with user count and statistics
    """
    try:
        # Count total users
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        # Count active users
        active_users = [user for user in users if user.is_active]
        superusers = [user for user in users if user.is_superuser]
        
        return {
            "total_users": len(users),
            "active_users": len(active_users),
            "superusers": len(superusers),
            "inactive_users": len(users) - len(active_users)
        }
        
    except Exception as e:
        logger.error(f"Error in get_user_count: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/admin/delete-all", summary="Delete All Users (Admin)")
@limiter.limit("1/minute")  # Very restrictive rate limit
async def delete_all_users(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    """
    Delete ALL users and their data (superuser only)
    ⚠️ WARNING: This is a destructive operation that cannot be undone!
    
    Returns:
        Dict with deletion count
    """
    try:
        logger.warning(f"🚨 ADMIN ACTION: User {current_user.email} is deleting all users")
        
        # Count users before deletion
        result = await session.execute(select(User))
        user_count = len(result.scalars().all())
        
        if user_count == 0:
            return {"message": "No users to delete", "deleted_count": 0}
        
        # Delete in correct order due to foreign key constraints
        # 1. Delete all speech analyses
        await session.execute(delete(SpeechAnalysis))
        logger.info("🗑️ Deleted all speech analyses")
        
        # 2. Delete all speeches  
        await session.execute(delete(Speech))
        logger.info("🗑️ Deleted all speeches")
        
        # 3. Delete all users
        await session.execute(delete(User))
        logger.info("🗑️ Deleted all users")
        
        await session.commit()
        
        logger.warning(f"🚨 COMPLETED: Deleted {user_count} users and all their data")
        
        return {
            "message": "All users and their data have been deleted",
            "deleted_count": user_count,
            "warning": "This action cannot be undone"
        }
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Error in delete_all_users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete users: {str(e)}")

@router.delete("/admin/delete-inactive", summary="Delete Inactive Users (Admin)")
@limiter.limit("5/minute")
async def delete_inactive_users(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    """
    Delete only inactive users and their data (superuser only)
    
    Returns:
        Dict with deletion count
    """
    try:
        logger.warning(f"🚨 ADMIN ACTION: User {current_user.email} is deleting inactive users")
        
        # Get inactive users
        result = await session.execute(select(User).where(User.is_active == False))
        inactive_users = result.scalars().all()
        inactive_user_ids = [user.id for user in inactive_users]
        
        if not inactive_users:
            return {"message": "No inactive users to delete", "deleted_count": 0}
        
        # Delete data for inactive users
        # 1. Delete analyses for inactive users' speeches
        speeches_result = await session.execute(select(Speech).where(Speech.user_id.in_(inactive_user_ids)))
        speech_ids = [speech.id for speech in speeches_result.scalars().all()]
        
        if speech_ids:
            await session.execute(delete(SpeechAnalysis).where(SpeechAnalysis.speech_id.in_(speech_ids)))
        
        # 2. Delete speeches for inactive users
        await session.execute(delete(Speech).where(Speech.user_id.in_(inactive_user_ids)))
        
        # 3. Delete inactive users
        await session.execute(delete(User).where(User.is_active == False))
        
        await session.commit()
        
        deleted_count = len(inactive_users)
        logger.warning(f"🚨 COMPLETED: Deleted {deleted_count} inactive users and their data")
        
        return {
            "message": f"Deleted {deleted_count} inactive users and their data",
            "deleted_count": deleted_count,
            "deleted_users": [{"id": str(user.id), "email": user.email} for user in inactive_users]
        }
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Error in delete_inactive_users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete inactive users: {str(e)}")