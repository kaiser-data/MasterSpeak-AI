# backend/api/v1/endpoints/export.py

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
import logging
import os
from io import BytesIO

from backend.database.database import get_session
from backend.services.export_service import export_service

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
    RateLimits = MockRateLimits()

router = APIRouter()
logger = logging.getLogger(__name__)

# Check if export is enabled
EXPORT_ENABLED = os.getenv("EXPORT_ENABLED", "0") == "1"

def check_export_enabled():
    """Middleware to check if export functionality is enabled."""
    if not EXPORT_ENABLED:
        raise HTTPException(
            status_code=404, 
            detail="Export functionality is not enabled"
        )

@router.get("/{analysis_id}/export", summary="Export Analysis as PDF")
@create_rate_limit_decorator(RateLimits.API_READ)
async def export_analysis_pdf(
    request: Request,
    analysis_id: UUID,
    include_transcript: bool = False,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user) if AUTH_AVAILABLE else None
) -> StreamingResponse:
    """
    Export analysis as PDF report (owner only).
    
    Args:
        analysis_id: UUID of the analysis to export
        include_transcript: Whether to include transcript in PDF
        
    Returns:
        StreamingResponse: PDF file download
        
    Requires:
        - Valid authentication (owner only)  
        - EXPORT_ENABLED=1 environment variable
        - reportlab package for PDF generation
    """
    check_export_enabled()
    
    if not AUTH_AVAILABLE or not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Import Analysis model here to avoid circular imports
        from backend.services.analyses import get_analysis_by_id
        
        # Get analysis with ownership verification
        analysis = await get_analysis_by_id(analysis_id, session, current_user.id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Generate PDF
        pdf_bytes = await export_service.render_pdf(
            analysis=analysis,
            include_transcript=include_transcript
        )
        
        # Generate safe filename
        title = "Analysis"
        filename = export_service.get_safe_filename(title, str(analysis_id), "pdf")
        
        logger.info(f"PDF export requested by user {current_user.id} for analysis {analysis_id}")
        
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting analysis {analysis_id} as PDF: {str(e)}")
        if "reportlab" in str(e):
            raise HTTPException(
                status_code=500, 
                detail="PDF generation not available. Please contact administrator."
            )
        raise HTTPException(status_code=500, detail="Export failed")