"""
Analysis service for MasterSpeak-AI.
Provides business logic layer for analysis operations with idempotent behavior.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.analysis import (
    Analysis, 
    AnalysisCreate, 
    AnalysisResponse, 
    AnalysisListResponse
)
from backend.repositories.analysis_repo import AnalysisRepository
from backend.utils.logging import logger, log_analysis_event


class AnalysisService:
    """
    Business logic service for analysis operations.
    
    Features:
    - Idempotent analysis persistence
    - User ownership validation
    - Business rule enforcement
    - Event logging for audit trail
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AnalysisRepository(session)
    
    async def save_analysis(
        self,
        user_id: UUID,
        speech_id: UUID,
        transcript: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
        summary: Optional[str] = None,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Save analysis with idempotent behavior.
        
        Args:
            user_id: User UUID
            speech_id: Speech UUID  
            transcript: Optional transcript content
            metrics: Optional structured metrics
            summary: Optional AI-generated summary
            feedback: Required analysis feedback
            
        Returns:
            Dictionary with analysis data and metadata
            
        Raises:
            ValueError: If feedback is missing or speech not found
            PermissionError: If user doesn't own the speech
        """
        
        # Validate required feedback
        if not feedback:
            raise ValueError("Feedback is required for analysis completion")
        
        # Validate speech ownership (basic check - could be expanded)
        # TODO: Add speech ownership validation by querying Speech table
        
        try:
            # Create analysis data
            analysis_data = AnalysisCreate(
                user_id=user_id,
                speech_id=speech_id,
                transcript=transcript,
                metrics=metrics,
                summary=summary,
                feedback=feedback
            )
            
            # Attempt idempotent creation
            analysis, is_new = await self.repo.create(analysis_data)
            
            # Log analysis event
            log_analysis_event(
                event="analysis_persisted" if is_new else "analysis_retrieved",
                analysis_id=str(analysis.id),
                speech_id=str(speech_id),
                user_id=str(user_id),
                is_new_record=is_new,
                has_transcript=transcript is not None,
                has_metrics=metrics is not None,
                has_summary=summary is not None
            )
            
            # Return response with metadata
            return {
                "analysis_id": analysis.id,
                "speech_id": analysis.speech_id,
                "user_id": analysis.user_id,
                "created_at": analysis.created_at,
                "is_duplicate": not is_new,
                "transcript": analysis.transcript,
                "metrics": analysis.metrics,
                "summary": analysis.summary,
                "feedback": analysis.feedback
            }
            
        except Exception as e:
            # Log failure event
            log_analysis_event(
                event="analysis_persist_failed",
                speech_id=str(speech_id),
                user_id=str(user_id),
                error=str(e),
                has_transcript=transcript is not None,
                has_metrics=metrics is not None,
                has_summary=summary is not None
            )
            
            logger.error(
                f"Failed to save analysis",
                operation="save_analysis",
                user_id=str(user_id),
                speech_id=str(speech_id),
                error=str(e)
            )
            raise
    
    async def get_recent(self, user_id: UUID, limit: int = 5) -> List[AnalysisResponse]:
        """
        Get recent analyses for dashboard display.
        
        Args:
            user_id: User UUID
            limit: Maximum number of analyses to return (default 5)
            
        Returns:
            List of recent analysis responses
        """
        try:
            analyses = await self.repo.get_recent_by_user(user_id, limit)
            
            # Convert to response models
            response_list = [
                AnalysisResponse(
                    analysis_id=analysis.id,
                    speech_id=analysis.speech_id,
                    user_id=analysis.user_id,
                    transcript=analysis.transcript,
                    metrics=analysis.metrics,
                    summary=analysis.summary,
                    feedback=analysis.feedback,
                    created_at=analysis.created_at,
                    updated_at=analysis.updated_at
                )
                for analysis in analyses
            ]
            
            logger.info(
                f"Retrieved {len(response_list)} recent analyses",
                operation="get_recent_analyses",
                user_id=str(user_id),
                count=len(response_list),
                limit=limit
            )
            
            return response_list
            
        except Exception as e:
            logger.error(
                f"Failed to get recent analyses",
                operation="get_recent_analyses",
                user_id=str(user_id),
                limit=limit,
                error=str(e)
            )
            raise
    
    async def get_analyses_page(
        self, 
        user_id: UUID, 
        page: int = 1, 
        limit: int = 20
    ) -> AnalysisListResponse:
        """
        Get paginated analyses for list page.
        
        Args:
            user_id: User UUID
            page: Page number (1-based)
            limit: Page size (default 20, max 100)
            
        Returns:
            Paginated analysis list response
        """
        try:
            # Calculate offset
            offset = (page - 1) * limit
            
            # Get analyses and total count
            analyses, total_count = await self.repo.list_by_user(user_id, limit, offset)
            
            # Convert to response models
            items = [
                AnalysisResponse(
                    analysis_id=analysis.id,
                    speech_id=analysis.speech_id,
                    user_id=analysis.user_id,
                    transcript=analysis.transcript,
                    metrics=analysis.metrics,
                    summary=analysis.summary,
                    feedback=analysis.feedback,
                    created_at=analysis.created_at,
                    updated_at=analysis.updated_at
                )
                for analysis in analyses
            ]
            
            # Calculate pagination metadata
            total_pages = (total_count + limit - 1) // limit
            has_next = page < total_pages
            has_previous = page > 1
            
            response = AnalysisListResponse(
                items=items,
                total=total_count,
                page=page,
                page_size=len(items),
                has_next=has_next,
                has_previous=has_previous
            )
            
            logger.info(
                f"Retrieved page {page} of analyses",
                operation="get_analyses_page",
                user_id=str(user_id),
                page=page,
                page_size=len(items),
                total_count=total_count,
                total_pages=total_pages
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Failed to get analyses page",
                operation="get_analyses_page",
                user_id=str(user_id),
                page=page,
                limit=limit,
                error=str(e)
            )
            raise
    
    async def get_analysis_by_id(
        self, 
        analysis_id: UUID, 
        user_id: UUID
    ) -> Optional[AnalysisResponse]:
        """
        Get single analysis by ID with user ownership validation.
        
        Args:
            analysis_id: Analysis UUID
            user_id: User UUID for ownership validation
            
        Returns:
            Analysis response if found and owned by user, None otherwise
            
        Raises:
            PermissionError: If analysis exists but not owned by user
        """
        try:
            analysis = await self.repo.get_by_id(analysis_id)
            
            if not analysis:
                logger.info(
                    f"Analysis not found",
                    operation="get_analysis_by_id",
                    analysis_id=str(analysis_id),
                    user_id=str(user_id)
                )
                return None
            
            # Validate ownership
            if analysis.user_id != user_id:
                logger.warning(
                    f"Analysis access denied - ownership mismatch",
                    operation="get_analysis_by_id",
                    analysis_id=str(analysis_id),
                    requesting_user_id=str(user_id),
                    actual_user_id=str(analysis.user_id)
                )
                raise PermissionError("Analysis not owned by user")
            
            response = AnalysisResponse(
                analysis_id=analysis.id,
                speech_id=analysis.speech_id,
                user_id=analysis.user_id,
                transcript=analysis.transcript,
                metrics=analysis.metrics,
                summary=analysis.summary,
                feedback=analysis.feedback,
                created_at=analysis.created_at,
                updated_at=analysis.updated_at
            )
            
            logger.info(
                f"Retrieved analysis by ID",
                operation="get_analysis_by_id",
                analysis_id=str(analysis_id),
                user_id=str(user_id)
            )
            
            return response
            
        except PermissionError:
            # Re-raise permission errors
            raise
        except Exception as e:
            logger.error(
                f"Failed to get analysis by ID",
                operation="get_analysis_by_id",
                analysis_id=str(analysis_id),
                user_id=str(user_id),
                error=str(e)
            )
            raise
    
    async def search_analyses(
        self,
        user_id: UUID,
        search_query: Optional[str] = None,
        min_clarity_score: Optional[float] = None,
        max_clarity_score: Optional[float] = None,
        min_structure_score: Optional[float] = None,
        max_structure_score: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        limit: int = 20
    ) -> AnalysisListResponse:
        """
        Search and filter analyses with multiple criteria.
        
        Args:
            user_id: User UUID
            search_query: Text search in feedback and summary
            min_clarity_score: Minimum clarity score filter
            max_clarity_score: Maximum clarity score filter
            min_structure_score: Minimum structure score filter
            max_structure_score: Maximum structure score filter
            start_date: Filter analyses after this date
            end_date: Filter analyses before this date
            page: Page number (1-based)
            limit: Page size (default 20, max 100)
            
        Returns:
            Paginated search results
        """
        try:
            # Calculate offset
            offset = (page - 1) * limit
            
            # Perform search
            analyses, total_count = await self.repo.search_analyses(
                user_id=user_id,
                search_query=search_query,
                min_clarity_score=min_clarity_score,
                max_clarity_score=max_clarity_score,
                min_structure_score=min_structure_score,
                max_structure_score=max_structure_score,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                offset=offset
            )
            
            # Convert to response models
            items = [
                AnalysisResponse(
                    analysis_id=analysis.id,
                    speech_id=analysis.speech_id,
                    user_id=analysis.user_id,
                    transcript=analysis.transcript,
                    metrics=analysis.metrics,
                    summary=analysis.summary,
                    feedback=analysis.feedback,
                    created_at=analysis.created_at,
                    updated_at=analysis.updated_at
                )
                for analysis in analyses
            ]
            
            # Calculate pagination metadata
            total_pages = (total_count + limit - 1) // limit
            has_next = page < total_pages
            has_previous = page > 1
            
            response = AnalysisListResponse(
                items=items,
                total=total_count,
                page=page,
                page_size=len(items),
                has_next=has_next,
                has_previous=has_previous
            )
            
            # Log search operation (without PII)
            logger.info(
                f"Search completed - found {len(items)} results",
                operation="search_analyses",
                user_id=str(user_id),
                page=page,
                page_size=len(items),
                total_count=total_count,
                total_pages=total_pages,
                has_search_query=bool(search_query and search_query.strip()),
                has_score_filters=any([
                    min_clarity_score is not None,
                    max_clarity_score is not None,
                    min_structure_score is not None,
                    max_structure_score is not None
                ]),
                has_date_filters=bool(start_date or end_date)
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Failed to search analyses",
                operation="search_analyses",
                user_id=str(user_id),
                page=page,
                limit=limit,
                error=str(e)
            )
            raise
    
    async def get_analysis_by_id_public(self, analysis_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get analysis by ID without user ownership validation (for sharing).
        
        Args:
            analysis_id: Analysis UUID
            
        Returns:
            Analysis data dictionary if found, None otherwise
        """
        try:
            analysis = await self.repo.get_by_id(analysis_id)
            
            if not analysis:
                return None
            
            # Return as dictionary for export/share compatibility
            return {
                "analysis_id": analysis.id,
                "speech_id": analysis.speech_id,
                "user_id": analysis.user_id,
                "transcript": analysis.transcript,
                "metrics": analysis.metrics,
                "summary": analysis.summary,
                "feedback": analysis.feedback,
                "created_at": analysis.created_at,
                "updated_at": analysis.updated_at
            }
            
        except Exception as e:
            logger.error(
                f"Failed to get analysis by ID (public)",
                operation="get_analysis_by_id_public",
                analysis_id=str(analysis_id),
                error=str(e)
            )
            raise


# Standalone helper functions for export/share functionality
async def get_analysis_by_id(analysis_id: UUID, session: AsyncSession, user_id: UUID) -> Optional[Dict[str, Any]]:
    """
    Get analysis by ID with user ownership validation (for export).
    
    Args:
        analysis_id: Analysis UUID
        session: Database session
        user_id: User UUID for ownership validation
        
    Returns:
        Analysis data dictionary if found and owned by user, None otherwise
    """
    service = AnalysisService(session)
    
    try:
        analysis_response = await service.get_analysis_by_id(analysis_id, user_id)
        
        if not analysis_response:
            return None
        
        # Convert response to dictionary for export compatibility
        return {
            "analysis_id": analysis_response.analysis_id,
            "speech_id": analysis_response.speech_id,
            "user_id": analysis_response.user_id,
            "transcript": analysis_response.transcript,
            "metrics": analysis_response.metrics,
            "summary": analysis_response.summary,
            "feedback": analysis_response.feedback,
            "created_at": analysis_response.created_at,
            "updated_at": analysis_response.updated_at
        }
        
    except PermissionError:
        # Return None for permission errors to indicate "not found"
        return None
    except Exception:
        # Re-raise other exceptions
        raise


async def get_analysis_by_id_public(analysis_id: UUID, session: AsyncSession) -> Optional[Dict[str, Any]]:
    """
    Get analysis by ID without user ownership validation (for public sharing).
    
    Args:
        analysis_id: Analysis UUID
        session: Database session
        
    Returns:
        Analysis data dictionary if found, None otherwise
    """
    service = AnalysisService(session)
    return await service.get_analysis_by_id_public(analysis_id)