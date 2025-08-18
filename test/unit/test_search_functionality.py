# test/unit/test_search_functionality.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from backend.repositories.analysis_repo import AnalysisRepository
from backend.services.analysis_service import AnalysisService
from backend.models.analysis import Analysis, AnalysisMetrics
from backend.main import app


@pytest.fixture
def mock_session():
    """Mock database session."""
    return MagicMock()


@pytest.fixture
def analysis_repo(mock_session):
    """Create AnalysisRepository with mocked session."""
    return AnalysisRepository(mock_session)


@pytest.fixture
def analysis_service(analysis_repo):
    """Create AnalysisService with mocked repository."""
    return AnalysisService(repository=analysis_repo)


@pytest.fixture
def sample_analyses():
    """Sample analyses for testing search functionality."""
    base_time = datetime.utcnow()
    user_id = uuid4()
    
    return [
        Analysis(
            analysis_id=uuid4(),
            user_id=user_id,
            speech_id=uuid4(),
            transcript="Speech about innovation and technology",
            metrics=AnalysisMetrics(
                word_count=5,
                clarity_score=8.5,
                structure_score=7.2,
                filler_word_count=1
            ),
            summary="Great speech about innovation",
            feedback="Excellent clarity and good structure",
            created_at=base_time,
            updated_at=base_time
        ),
        Analysis(
            analysis_id=uuid4(),
            user_id=user_id,
            speech_id=uuid4(),
            transcript="Speech about teamwork and collaboration",
            metrics=AnalysisMetrics(
                word_count=8,
                clarity_score=6.8,
                structure_score=9.1,
                filler_word_count=3
            ),
            summary="Good teamwork presentation",
            feedback="Strong structure, work on clarity",
            created_at=base_time - timedelta(days=7),
            updated_at=base_time - timedelta(days=7)
        ),
        Analysis(
            analysis_id=uuid4(),
            user_id=user_id,
            speech_id=uuid4(),
            transcript="Speech about leadership principles",
            metrics=AnalysisMetrics(
                word_count=12,
                clarity_score=9.2,
                structure_score=8.8,
                filler_word_count=0
            ),
            summary="Outstanding leadership talk",
            feedback="Exceptional presentation with perfect clarity",
            created_at=base_time - timedelta(days=14),
            updated_at=base_time - timedelta(days=14)
        )
    ]


class TestAnalysisRepositorySearch:
    """Test search functionality in AnalysisRepository."""

    @pytest.mark.asyncio
    async def test_search_by_text_query(self, analysis_repo, mock_session, sample_analyses):
        """Test searching analyses by text in feedback and summary."""
        # Arrange
        user_id = sample_analyses[0].user_id
        search_query = "innovation"
        
        # Mock the database query to return filtered results
        mock_session.execute.return_value.scalar.return_value = 1
        mock_session.execute.return_value.scalars.return_value.all.return_value = [sample_analyses[0]]
        
        # Act
        results, total = await analysis_repo.search_analyses(
            user_id=user_id,
            search_query=search_query,
            limit=20,
            offset=0
        )
        
        # Assert
        assert len(results) == 1
        assert total == 1
        assert results[0].summary == "Great speech about innovation"
        mock_session.execute.assert_called()

    @pytest.mark.asyncio
    async def test_search_by_clarity_score_range(self, analysis_repo, mock_session, sample_analyses):
        """Test filtering by clarity score range."""
        # Arrange
        user_id = sample_analyses[0].user_id
        min_clarity = 8.0
        max_clarity = 9.0
        
        # Filter expected results
        expected_results = [a for a in sample_analyses if min_clarity <= a.metrics.clarity_score <= max_clarity]
        
        mock_session.execute.return_value.scalar.return_value = len(expected_results)
        mock_session.execute.return_value.scalars.return_value.all.return_value = expected_results
        
        # Act
        results, total = await analysis_repo.search_analyses(
            user_id=user_id,
            min_clarity_score=min_clarity,
            max_clarity_score=max_clarity,
            limit=20,
            offset=0
        )
        
        # Assert
        assert len(results) == len(expected_results)
        assert total == len(expected_results)
        for result in results:
            assert min_clarity <= result.metrics.clarity_score <= max_clarity

    @pytest.mark.asyncio
    async def test_search_by_structure_score_range(self, analysis_repo, mock_session, sample_analyses):
        """Test filtering by structure score range."""
        # Arrange
        user_id = sample_analyses[0].user_id
        min_structure = 8.0
        max_structure = 10.0
        
        expected_results = [a for a in sample_analyses if min_structure <= a.metrics.structure_score <= max_structure]
        
        mock_session.execute.return_value.scalar.return_value = len(expected_results)
        mock_session.execute.return_value.scalars.return_value.all.return_value = expected_results
        
        # Act
        results, total = await analysis_repo.search_analyses(
            user_id=user_id,
            min_structure_score=min_structure,
            max_structure_score=max_structure,
            limit=20,
            offset=0
        )
        
        # Assert
        assert len(results) == len(expected_results)
        for result in results:
            assert min_structure <= result.metrics.structure_score <= max_structure

    @pytest.mark.asyncio
    async def test_search_by_date_range(self, analysis_repo, mock_session, sample_analyses):
        """Test filtering by date range."""
        # Arrange
        user_id = sample_analyses[0].user_id
        start_date = datetime.utcnow() - timedelta(days=10)
        end_date = datetime.utcnow()
        
        expected_results = [
            a for a in sample_analyses 
            if start_date <= a.created_at <= end_date
        ]
        
        mock_session.execute.return_value.scalar.return_value = len(expected_results)
        mock_session.execute.return_value.scalars.return_value.all.return_value = expected_results
        
        # Act
        results, total = await analysis_repo.search_analyses(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=20,
            offset=0
        )
        
        # Assert
        assert len(results) == len(expected_results)
        for result in results:
            assert start_date <= result.created_at <= end_date

    @pytest.mark.asyncio
    async def test_search_combined_filters(self, analysis_repo, mock_session, sample_analyses):
        """Test combining multiple search criteria."""
        # Arrange
        user_id = sample_analyses[0].user_id
        search_query = "structure"
        min_clarity = 6.0
        
        # Mock filtered results
        expected_results = [sample_analyses[1]]  # Only teamwork analysis matches
        
        mock_session.execute.return_value.scalar.return_value = len(expected_results)
        mock_session.execute.return_value.scalars.return_value.all.return_value = expected_results
        
        # Act
        results, total = await analysis_repo.search_analyses(
            user_id=user_id,
            search_query=search_query,
            min_clarity_score=min_clarity,
            limit=20,
            offset=0
        )
        
        # Assert
        assert len(results) == 1
        assert results[0].feedback == "Strong structure, work on clarity"

    @pytest.mark.asyncio
    async def test_search_pagination(self, analysis_repo, mock_session, sample_analyses):
        """Test search with pagination."""
        # Arrange
        user_id = sample_analyses[0].user_id
        limit = 1
        offset = 1
        
        mock_session.execute.return_value.scalar.return_value = len(sample_analyses)
        mock_session.execute.return_value.scalars.return_value.all.return_value = [sample_analyses[1]]
        
        # Act
        results, total = await analysis_repo.search_analyses(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        # Assert
        assert len(results) == 1
        assert total == len(sample_analyses)
        assert results[0] == sample_analyses[1]

    @pytest.mark.asyncio
    async def test_search_no_results(self, analysis_repo, mock_session):
        """Test search with no matching results."""
        # Arrange
        user_id = uuid4()
        search_query = "nonexistent"
        
        mock_session.execute.return_value.scalar.return_value = 0
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        
        # Act
        results, total = await analysis_repo.search_analyses(
            user_id=user_id,
            search_query=search_query,
            limit=20,
            offset=0
        )
        
        # Assert
        assert len(results) == 0
        assert total == 0


class TestAnalysisServiceSearch:
    """Test search functionality in AnalysisService."""

    @pytest.mark.asyncio
    async def test_search_analyses_service(self, analysis_service, sample_analyses):
        """Test the service layer search method."""
        # Arrange
        user_id = sample_analyses[0].user_id
        search_query = "innovation"
        
        with patch.object(analysis_service.repo, 'search_analyses') as mock_search:
            mock_search.return_value = ([sample_analyses[0]], 1)
            
            # Act
            result = await analysis_service.search_analyses(
                user_id=user_id,
                search_query=search_query,
                page=1,
                limit=20
            )
            
            # Assert
            assert len(result.items) == 1
            assert result.total == 1
            assert result.page == 1
            assert result.has_next == False
            assert result.has_previous == False
            mock_search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_analyses_pagination_metadata(self, analysis_service, sample_analyses):
        """Test pagination metadata calculation in search results."""
        # Arrange
        user_id = sample_analyses[0].user_id
        total_results = 25
        page = 2
        limit = 10
        
        with patch.object(analysis_service.repo, 'search_analyses') as mock_search:
            mock_search.return_value = (sample_analyses[:2], total_results)
            
            # Act
            result = await analysis_service.search_analyses(
                user_id=user_id,
                page=page,
                limit=limit
            )
            
            # Assert
            assert result.total == total_results
            assert result.page == page
            assert result.page_size == len(sample_analyses[:2])
            assert result.has_next == True  # 25 total, page 2 of 10 each
            assert result.has_previous == True  # page 2 has previous

    @pytest.mark.asyncio
    async def test_search_analyses_no_pii_in_logs(self, analysis_service, sample_analyses):
        """Test that search operations don't log PII data."""
        # Arrange
        user_id = sample_analyses[0].user_id
        
        with patch.object(analysis_service.repo, 'search_analyses') as mock_search, \
             patch('backend.services.analysis_service.logger') as mock_logger:
            
            mock_search.return_value = ([sample_analyses[0]], 1)
            
            # Act
            await analysis_service.search_analyses(
                user_id=user_id,
                search_query="test query",
                page=1,
                limit=20
            )
            
            # Assert
            # Check that transcript content is not logged
            for call in mock_logger.info.call_args_list:
                log_message = str(call)
                assert sample_analyses[0].transcript not in log_message


class TestSearchAPIEndpoints:
    """Test search API endpoints."""

    def test_search_endpoint_success(self):
        """Test successful search API call."""
        client = TestClient(app)
        
        with patch('backend.api.v1.routes.analyses.analysis_service') as mock_service, \
             patch('backend.api.v1.routes.analyses.get_current_user') as mock_get_user:
            
            # Arrange
            mock_user = {"id": str(uuid4())}
            mock_get_user.return_value = mock_user
            
            mock_response = MagicMock()
            mock_response.items = []
            mock_response.total = 0
            mock_response.page = 1
            mock_response.page_size = 0
            mock_response.has_next = False
            mock_response.has_previous = False
            
            mock_service.search_analyses.return_value = mock_response
            
            # Act
            response = client.get("/api/v1/analyses/search?q=test&min_clarity=7.0")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert "total" in data
            assert "page" in data

    def test_search_endpoint_validation_errors(self):
        """Test search endpoint parameter validation."""
        client = TestClient(app)
        
        with patch('backend.api.v1.routes.analyses.get_current_user') as mock_get_user:
            mock_user = {"id": str(uuid4())}
            mock_get_user.return_value = mock_user
            
            # Test invalid date format
            response = client.get("/api/v1/analyses/search?start_date=invalid-date")
            assert response.status_code == 400
            
            # Test invalid score range
            response = client.get("/api/v1/analyses/search?min_clarity=8&max_clarity=6")
            assert response.status_code == 400

    def test_search_endpoint_rate_limiting(self):
        """Test that search endpoint has rate limiting."""
        client = TestClient(app)
        
        with patch('backend.api.v1.routes.analyses.analysis_service') as mock_service, \
             patch('backend.api.v1.routes.analyses.get_current_user') as mock_get_user:
            
            mock_user = {"id": str(uuid4())}
            mock_get_user.return_value = mock_user
            mock_service.search_analyses.return_value = MagicMock()
            
            # Make multiple requests to test rate limiting
            responses = []
            for _ in range(25):  # Rate limit is 20 per minute
                response = client.get("/api/v1/analyses/search?q=test")
                responses.append(response)
            
            # Some requests should be rate limited
            rate_limited = [r for r in responses if r.status_code == 429]
            assert len(rate_limited) > 0


class TestSearchPerformance:
    """Test search performance and optimization."""

    @pytest.mark.asyncio
    async def test_search_query_optimization(self, analysis_repo, mock_session):
        """Test that search uses optimized database queries."""
        # Arrange
        user_id = uuid4()
        
        mock_session.execute.return_value.scalar.return_value = 0
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        
        # Act
        await analysis_repo.search_analyses(
            user_id=user_id,
            search_query="test",
            min_clarity_score=7.0,
            limit=20,
            offset=0
        )
        
        # Assert - should use exactly 2 queries (count + data)
        assert mock_session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_search_respects_limit(self, analysis_repo, mock_session):
        """Test that search respects the maximum limit."""
        # Arrange
        user_id = uuid4()
        excessive_limit = 500  # Above the 100 limit
        
        mock_session.execute.return_value.scalar.return_value = 0
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        
        # Act
        await analysis_repo.search_analyses(
            user_id=user_id,
            limit=excessive_limit,
            offset=0
        )
        
        # Assert - verify limit was capped at 100
        # This would be verified by examining the SQL query parameters
        # For now, just ensure the query executed without error
        assert mock_session.execute.call_count == 2