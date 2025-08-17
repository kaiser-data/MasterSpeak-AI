"""
Analysis repository for MasterSpeak-AI.
Provides data access layer with idempotent operations and pagination.
"""

from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, or_, text
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from backend.models.analysis import Analysis, AnalysisCreate
from backend.utils.logging import log_database_operation, logger


class AnalysisRepository:
    """
    Repository for Analysis entity with idempotent operations.
    
    Features:
    - Idempotent create with unique constraint handling
    - Efficient pagination with count queries
    - User ownership validation
    - Performance-optimized queries with proper indexing
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_user_speech(
        self, 
        user_id: UUID, 
        speech_id: UUID
    ) -> Optional[Analysis]:
        """
        Get analysis by user_id and speech_id combination.
        
        Args:
            user_id: User UUID
            speech_id: Speech UUID
            
        Returns:
            Analysis instance if found, None otherwise
        """
        start_time = datetime.utcnow()
        
        try:
            query = select(Analysis).where(
                and_(
                    Analysis.user_id == user_id,
                    Analysis.speech_id == speech_id
                )
            )
            
            result = await self.session.execute(query)
            analysis = result.scalar_one_or_none()
            
            # Log the database operation
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            log_database_operation(
                operation="select",
                table="analysis",
                duration_ms=duration_ms,
                found=analysis is not None,
                user_id=str(user_id),
                speech_id=str(speech_id)
            )
            
            return analysis
            
        except Exception as e:
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            logger.error(
                f"Failed to get analysis by user_speech",
                operation="get_by_user_speech",
                duration_ms=duration_ms,
                user_id=str(user_id),
                speech_id=str(speech_id),
                error=str(e)
            )
            raise
    
    async def create(self, analysis_data: AnalysisCreate) -> Tuple[Analysis, bool]:
        """
        Create analysis with idempotent behavior.
        
        Args:
            analysis_data: Analysis creation data
            
        Returns:
            Tuple of (Analysis, is_new_record)
            - Analysis: Created or existing analysis
            - is_new_record: True if created, False if already existed
            
        Raises:
            Exception: If creation fails for reasons other than uniqueness
        """
        start_time = datetime.utcnow()
        
        try:
            # First, try to find existing analysis
            existing = await self.get_by_user_speech(
                analysis_data.user_id, 
                analysis_data.speech_id
            )
            
            if existing:
                # Return existing analysis
                duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                log_database_operation(
                    operation="create_idempotent",
                    table="analysis",
                    duration_ms=duration_ms,
                    is_duplicate=True,
                    user_id=str(analysis_data.user_id),
                    speech_id=str(analysis_data.speech_id)
                )
                return existing, False
            
            # Create new analysis
            analysis = Analysis(
                user_id=analysis_data.user_id,
                speech_id=analysis_data.speech_id,
                transcript=analysis_data.transcript,
                metrics=analysis_data.metrics,
                summary=analysis_data.summary,
                feedback=analysis_data.feedback,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.session.add(analysis)
            await self.session.commit()
            await self.session.refresh(analysis)
            
            # Log successful creation
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            log_database_operation(
                operation="create",
                table="analysis",
                duration_ms=duration_ms,
                affected_rows=1,
                analysis_id=str(analysis.id),
                user_id=str(analysis_data.user_id),
                speech_id=str(analysis_data.speech_id)
            )
            
            return analysis, True
            
        except IntegrityError as e:
            # Handle race condition where another request created the same analysis
            await self.session.rollback()
            
            # Try to get the existing analysis again
            existing = await self.get_by_user_speech(
                analysis_data.user_id, 
                analysis_data.speech_id
            )
            
            if existing:
                duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                log_database_operation(
                    operation="create_race_condition",
                    table="analysis",
                    duration_ms=duration_ms,
                    is_duplicate=True,
                    user_id=str(analysis_data.user_id),
                    speech_id=str(analysis_data.speech_id)
                )
                return existing, False
            else:
                # Unexpected integrity error
                logger.error(
                    f"Integrity error creating analysis: {str(e)}",
                    operation="create_analysis",
                    user_id=str(analysis_data.user_id),
                    speech_id=str(analysis_data.speech_id),
                    error=str(e)
                )
                raise
                
        except Exception as e:
            await self.session.rollback()
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            logger.error(
                f"Failed to create analysis",
                operation="create_analysis",
                duration_ms=duration_ms,
                user_id=str(analysis_data.user_id),
                speech_id=str(analysis_data.speech_id),
                error=str(e)
            )
            raise
    
    async def list_by_user(
        self, 
        user_id: UUID, 
        limit: int = 20, 
        offset: int = 0
    ) -> Tuple[List[Analysis], int]:
        """
        Get paginated list of analyses for a user.
        
        Args:
            user_id: User UUID
            limit: Maximum number of records to return (max 100)
            offset: Number of records to skip
            
        Returns:
            Tuple of (analyses_list, total_count)
        """
        start_time = datetime.utcnow()
        
        try:
            # Enforce maximum limit
            limit = min(limit, 100)
            
            # Query for analyses with pagination
            query = (
                select(Analysis)
                .where(Analysis.user_id == user_id)
                .order_by(desc(Analysis.created_at))
                .limit(limit)
                .offset(offset)
            )
            
            result = await self.session.execute(query)
            analyses = result.scalars().all()
            
            # Get total count for pagination metadata
            count_query = select(func.count(Analysis.id)).where(Analysis.user_id == user_id)
            count_result = await self.session.execute(count_query)
            total_count = count_result.scalar()
            
            # Log the database operation
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            log_database_operation(
                operation="list_paginated",
                table="analysis",
                duration_ms=duration_ms,
                affected_rows=len(analyses),
                total_count=total_count,
                user_id=str(user_id),
                limit=limit,
                offset=offset
            )
            
            return list(analyses), total_count
            
        except Exception as e:
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            logger.error(
                f"Failed to list analyses by user",
                operation="list_by_user",
                duration_ms=duration_ms,
                user_id=str(user_id),
                limit=limit,
                offset=offset,
                error=str(e)
            )
            raise
    
    async def get_by_id(self, analysis_id: UUID) -> Optional[Analysis]:
        """
        Get analysis by ID.
        
        Args:
            analysis_id: Analysis UUID
            
        Returns:
            Analysis instance if found, None otherwise
        """
        start_time = datetime.utcnow()
        
        try:
            query = select(Analysis).where(Analysis.id == analysis_id)
            result = await self.session.execute(query)
            analysis = result.scalar_one_or_none()
            
            # Log the database operation
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            log_database_operation(
                operation="get_by_id",
                table="analysis",
                duration_ms=duration_ms,
                found=analysis is not None,
                analysis_id=str(analysis_id)
            )
            
            return analysis
            
        except Exception as e:
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            logger.error(
                f"Failed to get analysis by id",
                operation="get_by_id",
                duration_ms=duration_ms,
                analysis_id=str(analysis_id),
                error=str(e)
            )
            raise
    
    async def get_recent_by_user(self, user_id: UUID, limit: int = 5) -> List[Analysis]:
        """
        Get recent analyses for a user (for dashboard display).
        
        Args:
            user_id: User UUID
            limit: Maximum number of records to return (default 5)
            
        Returns:
            List of recent analyses
        """
        start_time = datetime.utcnow()
        
        try:
            # Enforce reasonable limit for recent items
            limit = min(limit, 10)
            
            query = (
                select(Analysis)
                .where(Analysis.user_id == user_id)
                .order_by(desc(Analysis.created_at))
                .limit(limit)
            )
            
            result = await self.session.execute(query)
            analyses = result.scalars().all()
            
            # Log the database operation
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            log_database_operation(
                operation="get_recent",
                table="analysis",
                duration_ms=duration_ms,
                affected_rows=len(analyses),
                user_id=str(user_id),
                limit=limit
            )
            
            return list(analyses)
            
        except Exception as e:
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            logger.error(
                f"Failed to get recent analyses",
                operation="get_recent_by_user",
                duration_ms=duration_ms,
                user_id=str(user_id),
                limit=limit,
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
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Analysis], int]:
        """
        Search and filter analyses for a user with multiple criteria.
        
        Args:
            user_id: User UUID
            search_query: Text search in feedback and summary
            min_clarity_score: Minimum clarity score filter
            max_clarity_score: Maximum clarity score filter
            min_structure_score: Minimum structure score filter
            max_structure_score: Maximum structure score filter
            start_date: Filter analyses after this date
            end_date: Filter analyses before this date
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            Tuple of (filtered_analyses, total_count)
        """
        start_time = datetime.utcnow()
        
        try:
            # Enforce maximum limit
            limit = min(limit, 100)
            
            # Build base query
            query = select(Analysis).where(Analysis.user_id == user_id)
            
            # Add text search conditions
            if search_query and search_query.strip():
                search_term = f"%{search_query.strip()}%"
                query = query.where(
                    or_(
                        Analysis.feedback.ilike(search_term),
                        Analysis.summary.ilike(search_term)
                    )
                )
            
            # Add score filters
            if min_clarity_score is not None:
                query = query.where(
                    Analysis.metrics['clarity_score'].astext.cast(text('FLOAT')) >= min_clarity_score
                )
            
            if max_clarity_score is not None:
                query = query.where(
                    Analysis.metrics['clarity_score'].astext.cast(text('FLOAT')) <= max_clarity_score
                )
            
            if min_structure_score is not None:
                query = query.where(
                    Analysis.metrics['structure_score'].astext.cast(text('FLOAT')) >= min_structure_score
                )
            
            if max_structure_score is not None:
                query = query.where(
                    Analysis.metrics['structure_score'].astext.cast(text('FLOAT')) <= max_structure_score
                )
            
            # Add date filters
            if start_date:
                query = query.where(Analysis.created_at >= start_date)
            
            if end_date:
                query = query.where(Analysis.created_at <= end_date)
            
            # Get total count for pagination
            count_query = select(func.count(Analysis.id)).select_from(query.alias())
            count_result = await self.session.execute(count_query)
            total_count = count_result.scalar()
            
            # Apply pagination and ordering
            paginated_query = (
                query
                .order_by(desc(Analysis.created_at))
                .limit(limit)
                .offset(offset)
            )
            
            result = await self.session.execute(paginated_query)
            analyses = result.scalars().all()
            
            # Log the database operation (without PII)
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            log_database_operation(
                operation="search_analyses",
                table="analysis",
                duration_ms=duration_ms,
                affected_rows=len(analyses),
                total_count=total_count,
                user_id=str(user_id),
                has_search_query=bool(search_query and search_query.strip()),
                has_score_filters=any([
                    min_clarity_score is not None,
                    max_clarity_score is not None,
                    min_structure_score is not None,
                    max_structure_score is not None
                ]),
                has_date_filters=bool(start_date or end_date),
                limit=limit,
                offset=offset
            )
            
            return list(analyses), total_count
            
        except Exception as e:
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            logger.error(
                f"Failed to search analyses",
                operation="search_analyses",
                duration_ms=duration_ms,
                user_id=str(user_id),
                error=str(e)
            )
            raise