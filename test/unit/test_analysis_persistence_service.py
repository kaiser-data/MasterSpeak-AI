# test/unit/test_analysis_persistence_service.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime
from sqlmodel import Session

from backend.services.analysis_service import AnalysisService
from backend.repositories.analysis_repo import AnalysisRepository
from backend.models.analysis import Analysis, AnalysisMetrics, AnalysisComplete
from backend.database.models import User, Speech


@pytest.fixture
def mock_analysis_repo():
    """Mock AnalysisRepository for testing."""
    return MagicMock(spec=AnalysisRepository)


@pytest.fixture
def mock_session():
    """Mock database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def analysis_service(mock_analysis_repo):
    """Create AnalysisService with mocked dependencies."""
    return AnalysisService(repository=mock_analysis_repo)


@pytest.fixture
def sample_analysis_data():
    """Sample analysis data for testing."""
    return {
        "user_id": uuid4(),
        "speech_id": uuid4(),
        "transcript": "This is a test speech about innovation.",
        "metrics": AnalysisMetrics(
            word_count=8,
            clarity_score=8.5,
            structure_score=7.8,
            filler_word_count=2
        ),
        "summary": "Test speech about innovation with good clarity.",
        "feedback": "Great clarity and structure. Minimize filler words."
    }


@pytest.fixture
def sample_analysis(sample_analysis_data):
    """Sample Analysis object."""
    return Analysis(
        analysis_id=uuid4(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        **sample_analysis_data
    )


class TestAnalysisService:
    """Test cases for AnalysisService."""

    @pytest.mark.asyncio
    async def test_save_analysis_new_success(self, analysis_service, mock_analysis_repo, sample_analysis_data):
        """Test successful creation of new analysis."""
        # Arrange
        analysis_complete = AnalysisComplete(**sample_analysis_data)
        expected_analysis = Analysis(
            analysis_id=uuid4(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            **sample_analysis_data
        )
        
        mock_analysis_repo.get_by_user_speech.return_value = None  # No existing analysis
        mock_analysis_repo.create.return_value = expected_analysis
        
        # Act
        result = await analysis_service.save_analysis(analysis_complete)
        
        # Assert
        assert result == expected_analysis
        mock_analysis_repo.get_by_user_speech.assert_called_once_with(
            analysis_complete.user_id, 
            analysis_complete.speech_id
        )
        mock_analysis_repo.create.assert_called_once()
        
        # Verify the create call had correct data
        create_call_args = mock_analysis_repo.create.call_args[0][0]
        assert create_call_args.user_id == analysis_complete.user_id
        assert create_call_args.speech_id == analysis_complete.speech_id
        assert create_call_args.transcript == analysis_complete.transcript
        assert create_call_args.feedback == analysis_complete.feedback

    @pytest.mark.asyncio
    async def test_save_analysis_existing_idempotent(self, analysis_service, mock_analysis_repo, sample_analysis, sample_analysis_data):
        """Test idempotent behavior when analysis already exists."""
        # Arrange
        analysis_complete = AnalysisComplete(**sample_analysis_data)
        mock_analysis_repo.get_by_user_speech.return_value = sample_analysis
        
        # Act
        result = await analysis_service.save_analysis(analysis_complete)
        
        # Assert
        assert result == sample_analysis
        mock_analysis_repo.get_by_user_speech.assert_called_once_with(
            analysis_complete.user_id, 
            analysis_complete.speech_id
        )
        mock_analysis_repo.create.assert_not_called()  # Should not create new

    @pytest.mark.asyncio
    async def test_save_analysis_repository_error(self, analysis_service, mock_analysis_repo, sample_analysis_data):
        """Test handling of repository errors."""
        # Arrange
        analysis_complete = AnalysisComplete(**sample_analysis_data)
        mock_analysis_repo.get_by_user_speech.return_value = None
        mock_analysis_repo.create.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await analysis_service.save_analysis(analysis_complete)

    @pytest.mark.asyncio
    async def test_get_recent_success(self, analysis_service, mock_analysis_repo, sample_analysis):
        """Test successful retrieval of recent analyses."""
        # Arrange
        user_id = uuid4()
        limit = 5
        expected_analyses = [sample_analysis]
        mock_analysis_repo.get_recent_by_user.return_value = expected_analyses
        
        # Act
        result = await analysis_service.get_recent(user_id, limit)
        
        # Assert
        assert result == expected_analyses
        mock_analysis_repo.get_recent_by_user.assert_called_once_with(user_id, limit)

    @pytest.mark.asyncio
    async def test_get_analyses_page_success(self, analysis_service, mock_analysis_repo, sample_analysis):
        """Test successful retrieval of paginated analyses."""
        # Arrange
        user_id = uuid4()
        page = 1
        limit = 20
        expected_analyses = [sample_analysis]
        expected_total = 1
        
        mock_analysis_repo.list_by_user.return_value = (expected_analyses, expected_total)
        
        # Act
        result = await analysis_service.get_analyses_page(user_id, page, limit)
        
        # Assert
        assert result.items == expected_analyses
        assert result.total == expected_total
        assert result.page == page
        assert result.page_size == limit
        assert result.has_next == False
        assert result.has_previous == False
        
        mock_analysis_repo.list_by_user.assert_called_once_with(
            user_id=user_id, 
            page=page, 
            limit=limit
        )

    @pytest.mark.asyncio
    async def test_get_analyses_page_with_pagination(self, analysis_service, mock_analysis_repo, sample_analysis):
        """Test pagination metadata calculation."""
        # Arrange
        user_id = uuid4()
        page = 2
        limit = 10
        total = 25
        expected_analyses = [sample_analysis]
        
        mock_analysis_repo.list_by_user.return_value = (expected_analyses, total)
        
        # Act
        result = await analysis_service.get_analyses_page(user_id, page, limit)
        
        # Assert
        assert result.has_next == True  # 25 total, page 2 of 10 each = has page 3
        assert result.has_previous == True  # page 2 has previous page 1

    @pytest.mark.asyncio
    async def test_get_analysis_by_id_success(self, analysis_service, mock_analysis_repo, sample_analysis):
        """Test successful retrieval of analysis by ID."""
        # Arrange
        user_id = uuid4()
        analysis_id = uuid4()
        mock_analysis_repo.get_by_id.return_value = sample_analysis
        
        # Act
        result = await analysis_service.get_analysis_by_id(analysis_id, user_id)
        
        # Assert
        assert result == sample_analysis
        mock_analysis_repo.get_by_id.assert_called_once_with(analysis_id)

    @pytest.mark.asyncio
    async def test_get_analysis_by_id_not_found(self, analysis_service, mock_analysis_repo):
        """Test error when analysis not found."""
        # Arrange
        user_id = uuid4()
        analysis_id = uuid4()
        mock_analysis_repo.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Analysis not found"):
            await analysis_service.get_analysis_by_id(analysis_id, user_id)

    @pytest.mark.asyncio
    async def test_get_analysis_by_id_wrong_user(self, analysis_service, mock_analysis_repo, sample_analysis):
        """Test error when user doesn't own the analysis."""
        # Arrange
        wrong_user_id = uuid4()
        analysis_id = uuid4()
        mock_analysis_repo.get_by_id.return_value = sample_analysis
        
        # Act & Assert
        with pytest.raises(ValueError, match="Access denied"):
            await analysis_service.get_analysis_by_id(analysis_id, wrong_user_id)

    @pytest.mark.asyncio
    async def test_save_analysis_no_transcript_logged(self, analysis_service, mock_analysis_repo, sample_analysis_data):
        """Test that transcript is never logged (PII protection)."""
        # Arrange
        analysis_complete = AnalysisComplete(**sample_analysis_data)
        mock_analysis_repo.get_by_user_speech.return_value = None
        
        expected_analysis = Analysis(
            analysis_id=uuid4(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            **sample_analysis_data
        )
        mock_analysis_repo.create.return_value = expected_analysis
        
        # Act
        with patch('backend.services.analysis_service.logger') as mock_logger:
            await analysis_service.save_analysis(analysis_complete)
            
            # Assert that no log calls contain the transcript
            for call in mock_logger.info.call_args_list:
                log_message = str(call)
                assert sample_analysis_data["transcript"] not in log_message


class TestAnalysisServiceIntegration:
    """Integration tests with real repository but mocked database."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_analysis_flow(self, mock_session):
        """Test complete analysis flow with repository integration."""
        # Arrange
        repo = AnalysisRepository(mock_session)
        service = AnalysisService(repository=repo)
        
        user_id = uuid4()
        speech_id = uuid4()
        analysis_data = {
            "user_id": user_id,
            "speech_id": speech_id,
            "transcript": "Test speech content",
            "metrics": AnalysisMetrics(
                word_count=3,
                clarity_score=8.0,
                structure_score=7.5,
                filler_word_count=1
            ),
            "summary": "Brief test summary",
            "feedback": "Good overall performance"
        }
        
        # Mock repository methods to simulate database behavior
        with patch.object(repo, 'get_by_user_speech', return_value=None), \
             patch.object(repo, 'create') as mock_create:
            
            # Configure mock to return the analysis as if saved
            expected_analysis = Analysis(
                analysis_id=uuid4(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                **analysis_data
            )
            mock_create.return_value = expected_analysis
            
            # Act
            result = await service.save_analysis(AnalysisComplete(**analysis_data))
            
            # Assert
            assert result.user_id == user_id
            assert result.speech_id == speech_id
            assert result.feedback == "Good overall performance"
            mock_create.assert_called_once()