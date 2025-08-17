# backend/api/v1/endpoints/share.py

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
from datetime import datetime
import logging
import os

from backend.database.database import get_session
from backend.database.models import User
from backend.models.analysis import Analysis
from backend.database.models import Speech, SpeechAnalysis
from backend.models.share_token import (
    ShareToken, 
    ShareTokenCreate, 
    ShareTokenResponse, 
    SharedAnalysisResponse
)

# Import auth dependency
try:
    from backend.dependencies.auth import get_current_user
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    def get_current_user():
        return None

# Import rate limiting
try:
    from backend.middleware.rate_limiting import limiter, RateLimits, create_rate_limit_decorator
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    RATE_LIMITING_AVAILABLE = False
    def create_rate_limit_decorator(limit: str):
        def decorator(func):
            return func
        return decorator
    
    class MockRateLimits:
        API_READ = '30/minute'
        SHARE_CREATE = '10/minute'
        SHARE_ACCESS = '60/minute'
    RateLimits = MockRateLimits()

router = APIRouter()
logger = logging.getLogger(__name__)

# Configuration flags
EXPORT_ENABLED = os.getenv("EXPORT_ENABLED", "0") == "1"
ALLOW_TRANSCRIPT_SHARE = os.getenv("ALLOW_TRANSCRIPT_SHARE", "0") == "1"

def check_export_enabled():
    """Middleware to check if export functionality is enabled."""
    if not EXPORT_ENABLED:
        raise HTTPException(
            status_code=404, 
            detail="Sharing functionality is not enabled"
        )

def safe_log_token_access(token: str, analysis_id: UUID):
    """Safely log token access without exposing sensitive data."""
    # Only log first 8 characters of token for audit trail
    safe_token = token[:8] + "..." if len(token) > 8 else token
    logger.info(f"Share token access: {safe_token} -> analysis {analysis_id}")

@router.post("/{analysis_id}", response_model=ShareTokenResponse, summary="Create Share Link")
@create_rate_limit_decorator(RateLimits.SHARE_CREATE if RATE_LIMITING_AVAILABLE else "10/minute")
async def create_share_link(
    request: Request,
    analysis_id: UUID,
    token_request: ShareTokenCreate,
    session: AsyncSession = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user) if AUTH_AVAILABLE else None
) -> ShareTokenResponse:
    """
    Create a shareable tokenized link for an analysis (owner only).
    
    Args:
        analysis_id: UUID of the analysis to share
        token_request: Share token configuration (expiration days)
        
    Returns:
        ShareTokenResponse: Share URL and token metadata
        
    Requires:
        - Valid authentication (owner only)
        - EXPORT_ENABLED=1 environment variable
    """
    check_export_enabled()
    
    if not AUTH_AVAILABLE or not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Verify analysis exists and user owns it
        result = await session.execute(
            select(Analysis).where(Analysis.id == analysis_id)
        )
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        if analysis.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if analysis_id matches the request
        if token_request.analysis_id != analysis_id:
            raise HTTPException(status_code=400, detail="Analysis ID mismatch")
        
        # Create share token
        share_token, raw_token = ShareToken.create_token(
            analysis_id=analysis_id,
            expires_in_days=token_request.expires_in_days
        )
        
        # Save to database
        session.add(share_token)
        await session.commit()
        await session.refresh(share_token)
        
        # Build share URL (adjust base URL based on environment)
        base_url = os.getenv("FRONTEND_URL", "https://masterspeak-ai.vercel.app")
        share_url = f"{base_url}/share/{raw_token}"
        
        logger.info(f"Share link created by user {current_user.id} for analysis {analysis_id}")
        
        return ShareTokenResponse(
            share_url=share_url,
            expires_at=share_token.expires_at,
            token_id=share_token.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating share link for analysis {analysis_id}: {str(e)}")
        if session.in_transaction():
            await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create share link")

@router.get("/{token}", response_model=SharedAnalysisResponse, summary="Access Shared Analysis")
@create_rate_limit_decorator(RateLimits.SHARE_ACCESS if RATE_LIMITING_AVAILABLE else "60/minute")
async def get_shared_analysis(
    request: Request,
    token: str,
    session: AsyncSession = Depends(get_session)
) -> SharedAnalysisResponse:
    """
    Access a shared analysis using a share token (public endpoint).
    
    Args:
        token: Share token for accessing the analysis
        
    Returns:
        SharedAnalysisResponse: Redacted analysis data (no PII in logs)
        
    Security:
        - Rate limited to prevent abuse
        - No sensitive data in logs
        - Transcript excluded unless ALLOW_TRANSCRIPT_SHARE=1
        - Token expiration enforced
    """
    check_export_enabled()
    
    try:
        # Hash the provided token for database lookup
        hashed_token = ShareToken.hash_token(token)
        
        # Find valid, non-expired token
        token_result = await session.execute(
            select(ShareToken).where(
                ShareToken.hashed_token == hashed_token,
                ShareToken.expires_at > datetime.utcnow()
            )
        )
        share_token = token_result.scalar_one_or_none()
        
        if not share_token:
            raise HTTPException(status_code=404, detail="Share link not found or expired")
        
        # Get the analysis
        analysis_result = await session.execute(
            select(Analysis).where(Analysis.id == share_token.analysis_id)
        )
        analysis = analysis_result.scalar_one_or_none()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get related speech for context (title, etc.)
        speech_result = await session.execute(
            select(Speech).where(Speech.id == analysis.speech_id)
        )
        speech = speech_result.scalar_one_or_none()
        
        # Get legacy analysis data if available
        legacy_result = await session.execute(
            select(SpeechAnalysis).where(SpeechAnalysis.speech_id == analysis.speech_id)
        )
        speech_analysis = legacy_result.scalar_one_or_none()
        
        # Build response with redacted data
        response_data = {
            "analysis_id": analysis.id,
            "speech_id": analysis.speech_id,
            "user_id": analysis.user_id,
            "metrics": analysis.metrics,
            "summary": analysis.summary,
            "feedback": analysis.feedback,
            "created_at": analysis.created_at,
            "shared": True,
            "transcript_included": False
        }
        
        # Add legacy metrics if available
        if speech_analysis:
            # Merge legacy metrics into main metrics
            if not response_data["metrics"]:
                response_data["metrics"] = {}
            
            response_data["metrics"].update({
                "word_count": speech_analysis.word_count,
                "clarity_score": speech_analysis.clarity_score,
                "structure_score": speech_analysis.structure_score,
                "filler_word_count": speech_analysis.filler_word_count
            })
        
        # Conditionally include transcript
        if ALLOW_TRANSCRIPT_SHARE:
            if analysis.transcript:
                response_data["transcript"] = analysis.transcript
                response_data["transcript_included"] = True
            elif speech and speech.content:
                response_data["transcript"] = speech.content
                response_data["transcript_included"] = True
        
        # Safe logging (no PII)
        safe_log_token_access(token, analysis.id)
        
        return SharedAnalysisResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accessing shared analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to access shared analysis")