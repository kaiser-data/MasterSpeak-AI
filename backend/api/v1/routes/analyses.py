"""
Analysis REST API routes for MasterSpeak-AI.
Provides endpoints for analysis persistence and retrieval.
"""

from typing import Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.database import get_session
from backend.models.analysis import (
    AnalysisComplete, 
    AnalysisResponse, 
    AnalysisListResponse
)
from backend.services.analysis_service import AnalysisService
from backend.utils.logging import logger, get_request_id, set_user_id
from backend.middleware.rate_limit import rate_limit


router = APIRouter()


async def get_analysis_service(session: AsyncSession = Depends(get_session)) -> AnalysisService:
    """Dependency to get analysis service instance."""
    return AnalysisService(session)


# TODO: Replace with proper authentication dependency
async def get_current_user() -> Dict[str, Any]:
    """
    Temporary mock authentication dependency.
    Replace with actual authentication logic.
    """
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",  # Mock user ID
        "email": "test@example.com"
    }


@router.post("/complete", response_model=Dict[str, Any])
@rate_limit(capacity=10, refill_rate=10/60)  # 10 requests per minute
async def complete_analysis(
    analysis_data: AnalysisComplete,
    service: AnalysisService = Depends(get_analysis_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Complete analysis with idempotent behavior.
    
    Creates a new analysis or returns existing one for the same user+speech combination.
    Enforces unique constraint on (user_id, speech_id).
    
    Returns:
        - 201: New analysis created
        - 200: Existing analysis returned (idempotent)
        - 400: Invalid request data
        - 403: Speech not owned by user
        - 422: Validation error
    """
    request_id = get_request_id()
    user_id = UUID(current_user["id"])
    
    # Set user context for logging
    set_user_id(str(user_id))
    
    try:
        # Log the analysis completion request
        logger.info(
            f"Analysis completion requested",
            operation="complete_analysis",
            user_id=str(user_id),
            speech_id=str(analysis_data.speech_id),
            request_id=request_id,
            has_transcript=analysis_data.transcript is not None,
            has_metrics=analysis_data.metrics is not None,
            has_summary=analysis_data.summary is not None
        )
        
        # Validate user ownership of speech_id
        if analysis_data.user_id != user_id:
            logger.warning(
                f"Analysis completion denied - user mismatch",
                operation="complete_analysis",
                requesting_user_id=str(user_id),
                data_user_id=str(analysis_data.user_id),
                speech_id=str(analysis_data.speech_id),
                request_id=request_id
            )
            raise HTTPException(
                status_code=403,
                detail="Cannot create analysis for another user's speech"
            )
        
        # Save analysis with idempotent behavior
        result = await service.save_analysis(
            user_id=user_id,
            speech_id=analysis_data.speech_id,
            transcript=analysis_data.transcript,
            metrics=analysis_data.metrics,
            summary=analysis_data.summary,
            feedback=analysis_data.feedback
        )
        
        # Log successful completion
        logger.info(
            f"Analysis completed successfully",
            operation="complete_analysis",
            user_id=str(user_id),
            speech_id=str(analysis_data.speech_id),
            analysis_id=str(result["analysis_id"]),
            is_duplicate=result["is_duplicate"],
            request_id=request_id
        )
        
        return result
        
    except ValueError as e:
        logger.error(
            f"Analysis completion validation error: {str(e)}",
            operation="complete_analysis",
            user_id=str(user_id),
            speech_id=str(analysis_data.speech_id),
            request_id=request_id,
            error=str(e)
        )
        raise HTTPException(status_code=400, detail=str(e))
        
    except PermissionError as e:
        logger.error(
            f"Analysis completion permission error: {str(e)}",
            operation="complete_analysis",
            user_id=str(user_id),
            speech_id=str(analysis_data.speech_id),
            request_id=request_id,
            error=str(e)
        )
        raise HTTPException(status_code=403, detail=str(e))
        
    except Exception as e:
        logger.error(
            f"Analysis completion failed: {str(e)}",
            operation="complete_analysis",
            user_id=str(user_id),
            speech_id=str(analysis_data.speech_id),
            request_id=request_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500, 
            detail="Internal server error during analysis completion"
        )


@router.get("", response_model=AnalysisListResponse)
async def list_analyses(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Page size (max 100)"),
    service: AnalysisService = Depends(get_analysis_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> AnalysisListResponse:
    """
    Get paginated list of user's analyses.
    
    Args:
        page: Page number (1-based, default 1)
        limit: Page size (default 20, max 100)
        
    Returns:
        Paginated list of analyses with metadata
    """
    request_id = get_request_id()
    user_id = UUID(current_user["id"])
    
    # Set user context for logging
    set_user_id(str(user_id))
    
    try:
        logger.info(
            f"Analyses list requested",
            operation="list_analyses",
            user_id=str(user_id),
            page=page,
            limit=limit,
            request_id=request_id
        )
        
        # Get paginated analyses
        result = await service.get_analyses_page(
            user_id=user_id,
            page=page,
            limit=limit
        )
        
        logger.info(
            f"Analyses list retrieved successfully",
            operation="list_analyses",
            user_id=str(user_id),
            page=page,
            returned_count=len(result.items),
            total_count=result.total,
            request_id=request_id
        )
        
        return result
        
    except Exception as e:
        logger.error(
            f"Analyses list retrieval failed: {str(e)}",
            operation="list_analyses",
            user_id=str(user_id),
            page=page,
            limit=limit,
            request_id=request_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500, 
            detail="Internal server error during analyses retrieval"
        )


@router.get("/recent", response_model=list[AnalysisResponse])
async def get_recent_analyses(
    limit: int = Query(5, ge=1, le=10, description="Number of recent analyses (max 10)"),
    service: AnalysisService = Depends(get_analysis_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> list[AnalysisResponse]:
    """
    Get recent analyses for dashboard display.
    
    Args:
        limit: Number of recent analyses to return (default 5, max 10)
        
    Returns:
        List of recent analyses
    """
    request_id = get_request_id()
    user_id = UUID(current_user["id"])
    
    # Set user context for logging
    set_user_id(str(user_id))
    
    try:
        logger.info(
            f"Recent analyses requested",
            operation="get_recent_analyses",
            user_id=str(user_id),
            limit=limit,
            request_id=request_id
        )
        
        # Get recent analyses
        result = await service.get_recent(user_id=user_id, limit=limit)
        
        logger.info(
            f"Recent analyses retrieved successfully",
            operation="get_recent_analyses",
            user_id=str(user_id),
            returned_count=len(result),
            limit=limit,
            request_id=request_id
        )
        
        return result
        
    except Exception as e:
        logger.error(
            f"Recent analyses retrieval failed: {str(e)}",
            operation="get_recent_analyses",
            user_id=str(user_id),
            limit=limit,
            request_id=request_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500, 
            detail="Internal server error during recent analyses retrieval"
        )


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: UUID,
    service: AnalysisService = Depends(get_analysis_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> AnalysisResponse:
    """
    Get single analysis by ID.
    
    Validates user ownership of the analysis.
    
    Args:
        analysis_id: Analysis UUID
        
    Returns:
        Analysis details
        
    Raises:
        404: Analysis not found
        403: Analysis not owned by user
    """
    request_id = get_request_id()
    user_id = UUID(current_user["id"])
    
    # Set user context for logging
    set_user_id(str(user_id))
    
    try:
        logger.info(
            f"Analysis details requested",
            operation="get_analysis",
            user_id=str(user_id),
            analysis_id=str(analysis_id),
            request_id=request_id
        )
        
        # Get analysis with ownership validation
        result = await service.get_analysis_by_id(
            analysis_id=analysis_id,
            user_id=user_id
        )
        
        if not result:
            logger.info(
                f"Analysis not found",
                operation="get_analysis",
                user_id=str(user_id),
                analysis_id=str(analysis_id),
                request_id=request_id
            )
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        logger.info(
            f"Analysis details retrieved successfully",
            operation="get_analysis",
            user_id=str(user_id),
            analysis_id=str(analysis_id),
            request_id=request_id
        )
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except PermissionError as e:
        logger.warning(
            f"Analysis access denied: {str(e)}",
            operation="get_analysis",
            user_id=str(user_id),
            analysis_id=str(analysis_id),
            request_id=request_id,
            error=str(e)
        )
        raise HTTPException(status_code=403, detail="Analysis not owned by user")
        
    except Exception as e:
        logger.error(
            f"Analysis retrieval failed: {str(e)}",
            operation="get_analysis",
            user_id=str(user_id),
            analysis_id=str(analysis_id),
            request_id=request_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500, 
            detail="Internal server error during analysis retrieval"
        )


@router.get("/search", response_model=AnalysisListResponse)
@rate_limit(capacity=20, refill_rate=20/60)  # 20 searches per minute
async def search_analyses(
    q: Optional[str] = Query(None, description="Search query in feedback and summary"),
    min_clarity: Optional[float] = Query(None, ge=0, le=10, description="Minimum clarity score"),
    max_clarity: Optional[float] = Query(None, ge=0, le=10, description="Maximum clarity score"),
    min_structure: Optional[float] = Query(None, ge=0, le=10, description="Minimum structure score"),
    max_structure: Optional[float] = Query(None, ge=0, le=10, description="Maximum structure score"),
    start_date: Optional[str] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date filter (ISO format)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    service: AnalysisService = Depends(get_analysis_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> AnalysisListResponse:
    """
    Search and filter analyses with multiple criteria.
    
    Args:
        q: Text search in feedback and summary
        min_clarity: Minimum clarity score filter (0-10)
        max_clarity: Maximum clarity score filter (0-10)
        min_structure: Minimum structure score filter (0-10)
        max_structure: Maximum structure score filter (0-10)
        start_date: Start date filter (ISO format)
        end_date: End date filter (ISO format)
        page: Page number (1-based)
        limit: Page size (max 100)
        
    Returns:
        Paginated search results
    """
    request_id = get_request_id()
    user_id = UUID(current_user["id"])
    
    # Set user context for logging
    set_user_id(str(user_id))
    
    try:
        # Parse date filters
        start_datetime = None
        end_datetime = None
        
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use ISO format.")
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use ISO format.")
        
        # Validate date range
        if start_datetime and end_datetime and start_datetime > end_datetime:
            raise HTTPException(status_code=400, detail="start_date must be before end_date")
        
        # Validate score ranges
        if min_clarity is not None and max_clarity is not None and min_clarity > max_clarity:
            raise HTTPException(status_code=400, detail="min_clarity must be <= max_clarity")
        
        if min_structure is not None and max_structure is not None and min_structure > max_structure:
            raise HTTPException(status_code=400, detail="min_structure must be <= max_structure")
        
        logger.info(
            f"Analysis search requested",
            operation="search_analyses",
            user_id=str(user_id),
            has_query=bool(q and q.strip()),
            has_score_filters=any([min_clarity, max_clarity, min_structure, max_structure]),
            has_date_filters=bool(start_datetime or end_datetime),
            page=page,
            limit=limit,
            request_id=request_id
        )
        
        # Perform search
        result = await service.search_analyses(
            user_id=user_id,
            search_query=q,
            min_clarity_score=min_clarity,
            max_clarity_score=max_clarity,
            min_structure_score=min_structure,
            max_structure_score=max_structure,
            start_date=start_datetime,
            end_date=end_datetime,
            page=page,
            limit=limit
        )
        
        logger.info(
            f"Analysis search completed successfully",
            operation="search_analyses",
            user_id=str(user_id),
            returned_count=len(result.items),
            total_count=result.total,
            page=page,
            request_id=request_id
        )
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            f"Analysis search failed: {str(e)}",
            operation="search_analyses",
            user_id=str(user_id),
            page=page,
            limit=limit,
            request_id=request_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500, 
            detail="Internal server error during analysis search"
        )