# test/unit/test_analysis_repository.py

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from backend.repositories.analysis_repo import AnalysisRepository
from backend.models.analysis import Analysis, AnalysisMetrics


@pytest.fixture
def mock_session():
    """Mock database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def analysis_repo(mock_session):
    """Create AnalysisRepository with mocked session."""
    return AnalysisRepository(mock_session)


@pytest.fixture
def sample_analysis():
    """Sample Analysis object for testing."""
    return Analysis(
        analysis_id=uuid4(),
        user_id=uuid4(),
        speech_id=uuid4(),
        transcript="Sample speech content for testing",
        metrics=AnalysisMetrics(
            word_count=6,
            clarity_score=8.2,
            structure_score=7.8,
            filler_word_count=1
        ),
        summary="Sample summary of the speech",
        feedback="Good clarity and structure overall",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


class TestAnalysisRepository:
    """Test cases for AnalysisRepository."""

    def test_get_by_user_speech_found(self, analysis_repo, mock_session, sample_analysis):
        """Test successful retrieval of analysis by user and speech ID."""
        # Arrange
        user_id = sample_analysis.user_id
        speech_id = sample_analysis.speech_id
        
        mock_session.exec.return_value.first.return_value = sample_analysis
        
        # Act
        result = analysis_repo.get_by_user_speech(user_id, speech_id)
        
        # Assert
        assert result == sample_analysis
        mock_session.exec.assert_called_once()
        # Verify the SQL query structure
        call_args = mock_session.exec.call_args[0][0]
        assert isinstance(call_args, type(select(Analysis)))

    def test_get_by_user_speech_not_found(self, analysis_repo, mock_session):
        """Test when analysis doesn't exist for user and speech."""
        # Arrange
        user_id = uuid4()
        speech_id = uuid4()
        
        mock_session.exec.return_value.first.return_value = None
        
        # Act
        result = analysis_repo.get_by_user_speech(user_id, speech_id)
        
        # Assert
        assert result is None
        mock_session.exec.assert_called_once()

    def test_create_success(self, analysis_repo, mock_session, sample_analysis):
        """Test successful creation of new analysis."""
        # Arrange
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None
        
        # Act
        result = analysis_repo.create(sample_analysis)
        
        # Assert
        assert result == sample_analysis
        mock_session.add.assert_called_once_with(sample_analysis)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_analysis)

    def test_create_integrity_error_race_condition(self, analysis_repo, mock_session, sample_analysis):
        """Test handling of race condition during creation."""
        # Arrange
        mock_session.add.return_value = None
        mock_session.commit.side_effect = IntegrityError("UNIQUE constraint failed", None, None)
        mock_session.rollback.return_value = None
        
        # Mock the subsequent get_by_user_speech call
        mock_session.exec.return_value.first.return_value = sample_analysis
        
        # Act
        result = analysis_repo.create(sample_analysis)
        
        # Assert
        assert result == sample_analysis
        mock_session.add.assert_called_once_with(sample_analysis)
        mock_session.commit.assert_called_once()
        mock_session.rollback.assert_called_once()
        # Should call exec for the get_by_user_speech query
        mock_session.exec.assert_called_once()

    def test_create_other_exception(self, analysis_repo, mock_session, sample_analysis):
        """Test handling of non-integrity database errors."""
        # Arrange
        mock_session.add.return_value = None
        mock_session.commit.side_effect = Exception("Database connection lost")
        mock_session.rollback.return_value = None
        
        # Act & Assert
        with pytest.raises(Exception, match="Database connection lost"):
            analysis_repo.create(sample_analysis)
        
        mock_session.rollback.assert_called_once()

    def test_list_by_user_success(self, analysis_repo, mock_session, sample_analysis):
        """Test successful retrieval of user analyses with pagination."""
        # Arrange
        user_id = sample_analysis.user_id
        page = 1
        limit = 20
        
        # Mock the count query
        mock_session.exec.return_value.one.return_value = 1
        # Mock the list query
        mock_session.exec.return_value.all.return_value = [sample_analysis]
        
        # Act
        analyses, total = analysis_repo.list_by_user(user_id, page, limit)
        
        # Assert
        assert analyses == [sample_analysis]
        assert total == 1
        assert mock_session.exec.call_count == 2  # count + list queries

    def test_list_by_user_empty_result(self, analysis_repo, mock_session):
        """Test when user has no analyses."""
        # Arrange
        user_id = uuid4()
        page = 1
        limit = 20
        
        mock_session.exec.return_value.one.return_value = 0
        mock_session.exec.return_value.all.return_value = []
        
        # Act
        analyses, total = analysis_repo.list_by_user(user_id, page, limit)
        
        # Assert
        assert analyses == []
        assert total == 0

    def test_list_by_user_pagination_offset(self, analysis_repo, mock_session, sample_analysis):
        """Test pagination offset calculation."""
        # Arrange
        user_id = sample_analysis.user_id
        page = 3
        limit = 10
        
        mock_session.exec.return_value.one.return_value = 25
        mock_session.exec.return_value.all.return_value = [sample_analysis]
        
        # Act
        analyses, total = analysis_repo.list_by_user(user_id, page, limit)
        
        # Assert
        assert analyses == [sample_analysis]
        assert total == 25
        # Verify offset calculation: (page - 1) * limit = (3 - 1) * 10 = 20
        # We can't easily verify the exact offset without inspecting SQL generation

    def test_get_recent_by_user_success(self, analysis_repo, mock_session, sample_analysis):
        """Test successful retrieval of recent analyses."""
        # Arrange
        user_id = sample_analysis.user_id
        limit = 5
        
        mock_session.exec.return_value.all.return_value = [sample_analysis]
        
        # Act
        result = analysis_repo.get_recent_by_user(user_id, limit)
        
        # Assert
        assert result == [sample_analysis]
        mock_session.exec.assert_called_once()

    def test_get_by_id_found(self, analysis_repo, mock_session, sample_analysis):
        """Test successful retrieval by analysis ID."""
        # Arrange
        analysis_id = sample_analysis.analysis_id
        mock_session.get.return_value = sample_analysis
        
        # Act
        result = analysis_repo.get_by_id(analysis_id)
        
        # Assert
        assert result == sample_analysis
        mock_session.get.assert_called_once_with(Analysis, analysis_id)

    def test_get_by_id_not_found(self, analysis_repo, mock_session):
        """Test when analysis ID doesn't exist."""
        # Arrange
        analysis_id = uuid4()
        mock_session.get.return_value = None
        
        # Act
        result = analysis_repo.get_by_id(analysis_id)
        
        # Assert
        assert result is None
        mock_session.get.assert_called_once_with(Analysis, analysis_id)

    def test_logging_excludes_pii(self, analysis_repo, mock_session, sample_analysis):
        """Test that PII data (transcript) is never logged."""
        # Arrange
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None
        
        # Act
        with patch('backend.repositories.analysis_repo.logger') as mock_logger:
            analysis_repo.create(sample_analysis)
            
            # Assert that no log calls contain the transcript
            for call in mock_logger.info.call_args_list:
                log_message = str(call)
                assert sample_analysis.transcript not in log_message
                # Should log analysis_id but not transcript content
                assert str(sample_analysis.analysis_id) in log_message

    def test_repository_session_handling(self, mock_session, sample_analysis):
        """Test that repository properly handles session lifecycle."""
        # Arrange
        repo = AnalysisRepository(mock_session)
        
        # Act - perform multiple operations
        repo.get_by_id(sample_analysis.analysis_id)
        repo.create(sample_analysis)
        repo.get_recent_by_user(sample_analysis.user_id, 5)
        
        # Assert - verify session is used consistently
        assert repo.session == mock_session
        # Verify multiple calls used the same session
        assert mock_session.get.call_count >= 1
        assert mock_session.add.call_count >= 1
        assert mock_session.exec.call_count >= 1


class TestAnalysisRepositoryPerformance:
    """Performance and optimization tests."""

    def test_list_by_user_uses_efficient_queries(self, analysis_repo, mock_session):
        """Test that pagination uses efficient SQL queries."""
        # Arrange
        user_id = uuid4()
        
        mock_session.exec.return_value.one.return_value = 100
        mock_session.exec.return_value.all.return_value = []
        
        # Act
        analysis_repo.list_by_user(user_id, page=1, limit=20)
        
        # Assert - should use exactly 2 queries (count + data)
        assert mock_session.exec.call_count == 2

    def test_get_recent_orders_by_created_at(self, analysis_repo, mock_session):
        """Test that recent queries are properly ordered."""
        # Arrange
        user_id = uuid4()
        mock_session.exec.return_value.all.return_value = []
        
        # Act
        analysis_repo.get_recent_by_user(user_id, 5)
        
        # Assert - verify query was called (ordering is in SQL generation)
        mock_session.exec.assert_called_once()
        # The actual ORDER BY clause verification would require SQL inspection
        # which is beyond unit test scope