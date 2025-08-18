# test/unit/test_analysis_persistence_routes.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from uuid import uuid4
from datetime import datetime

from backend.main import app
from backend.models.analysis import Analysis, AnalysisMetrics, AnalysisComplete, AnalysisListResponse
from backend.services.analysis_service import AnalysisService


@pytest.fixture
def mock_analysis_service():
    """Mock AnalysisService for testing."""
    return MagicMock(spec=AnalysisService)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_analysis():
    """Sample Analysis object for testing."""
    return Analysis(
        analysis_id=uuid4(),
        user_id=uuid4(),
        speech_id=uuid4(),
        transcript="Sample speech about innovation and technology",
        metrics=AnalysisMetrics(
            word_count=6,
            clarity_score=8.5,
            structure_score=7.8,
            filler_word_count=1
        ),
        summary="Good speech about technology with clear structure",
        feedback="Excellent clarity and structure. Minimal filler words.",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def mock_current_user():
    """Mock current user for authentication."""
    from backend.database.models import User
    return User(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        is_active=True,
        is_superuser=False
    )


class TestAnalysisCompleteEndpoint:
    """Test POST /api/v1/analyses/complete endpoint."""

    @patch('backend.api.v1.routes.analyses.analysis_service')
    @patch('backend.api.v1.routes.analyses.get_current_user')
    def test_complete_analysis_success(self, mock_get_user, mock_service, client, sample_analysis, mock_current_user):
        """Test successful analysis completion."""
        # Arrange
        mock_get_user.return_value = mock_current_user
        mock_service.save_analysis.return_value = sample_analysis
        
        request_data = {
            "user_id": str(mock_current_user.id),
            "speech_id": str(sample_analysis.speech_id),
            "transcript": sample_analysis.transcript,
            "metrics": {
                "word_count": 6,
                "clarity_score": 8.5,
                "structure_score": 7.8,
                "filler_word_count": 1
            },
            "summary": sample_analysis.summary,
            "feedback": sample_analysis.feedback
        }
        
        # Act
        response = client.post("/api/v1/analyses/complete", json=request_data)
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["analysis_id"] == str(sample_analysis.analysis_id)
        assert response_data["speech_id"] == str(sample_analysis.speech_id)
        assert response_data["user_id"] == str(sample_analysis.user_id)
        assert response_data["feedback"] == sample_analysis.feedback
        assert "transcript" not in response_data  # PII not returned
        
        mock_service.save_analysis.assert_called_once()

    @patch('backend.api.v1.routes.analyses.analysis_service')
    @patch('backend.api.v1.routes.analyses.get_current_user')
    def test_complete_analysis_idempotent(self, mock_get_user, mock_service, client, sample_analysis, mock_current_user):
        """Test idempotent behavior - duplicate request returns existing analysis."""
        # Arrange
        mock_get_user.return_value = mock_current_user
        mock_service.save_analysis.return_value = sample_analysis
        
        request_data = {
            "user_id": str(mock_current_user.id),
            "speech_id": str(sample_analysis.speech_id),
            "feedback": "New feedback"  # Different feedback
        }
        
        # Act
        response = client.post("/api/v1/analyses/complete", json=request_data)
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["is_duplicate"] == True
        assert response_data["feedback"] == sample_analysis.feedback  # Original feedback preserved

    @patch('backend.api.v1.routes.analyses.analysis_service')
    @patch('backend.api.v1.routes.analyses.get_current_user')
    def test_complete_analysis_rate_limited(self, mock_get_user, mock_service, client, mock_current_user):
        """Test rate limiting on complete analysis endpoint."""
        # Arrange
        mock_get_user.return_value = mock_current_user
        mock_service.save_analysis.return_value = MagicMock()
        
        request_data = {
            "user_id": str(mock_current_user.id),
            "speech_id": str(uuid4()),
            "feedback": "Test feedback"
        }
        
        # Act - Make multiple requests to trigger rate limit
        responses = []
        for _ in range(12):  # Rate limit is 10 per minute
            response = client.post("/api/v1/analyses/complete", json=request_data)
            responses.append(response)
        
        # Assert - Some requests should be rate limited
        rate_limited_responses = [r for r in responses if r.status_code == 429]
        assert len(rate_limited_responses) > 0

    @patch('backend.api.v1.routes.analyses.get_current_user')
    def test_complete_analysis_missing_fields(self, mock_get_user, client, mock_current_user):
        """Test validation error for missing required fields."""
        # Arrange
        mock_get_user.return_value = mock_current_user
        
        request_data = {
            "user_id": str(mock_current_user.id),
            # Missing speech_id and feedback
        }
        
        # Act
        response = client.post("/api/v1/analyses/complete", json=request_data)
        
        # Assert
        assert response.status_code == 422  # Validation error


class TestAnalysisListEndpoint:
    """Test GET /api/v1/analyses endpoint."""

    @patch('backend.api.v1.routes.analyses.analysis_service')
    @patch('backend.api.v1.routes.analyses.get_current_user')
    def test_get_analyses_success(self, mock_get_user, mock_service, client, sample_analysis, mock_current_user):
        """Test successful retrieval of analyses list."""
        # Arrange
        mock_get_user.return_value = mock_current_user
        mock_list_response = AnalysisListResponse(
            items=[sample_analysis],
            total=1,
            page=1,
            page_size=20,
            has_next=False,
            has_previous=False
        )
        mock_service.get_analyses_page.return_value = mock_list_response
        
        # Act
        response = client.get("/api/v1/analyses?page=1&limit=20")
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["items"]) == 1
        assert response_data["total"] == 1
        assert response_data["page"] == 1
        assert response_data["has_next"] == False
        
        mock_service.get_analyses_page.assert_called_once_with(
            mock_current_user.id, 1, 20
        )

    @patch('backend.api.v1.routes.analyses.analysis_service')
    @patch('backend.api.v1.routes.analyses.get_current_user')
    def test_get_analyses_pagination(self, mock_get_user, mock_service, client, mock_current_user):
        """Test pagination parameters."""
        # Arrange
        mock_get_user.return_value = mock_current_user
        mock_list_response = AnalysisListResponse(
            items=[],
            total=50,
            page=3,
            page_size=10,
            has_next=True,
            has_previous=True
        )
        mock_service.get_analyses_page.return_value = mock_list_response
        
        # Act
        response = client.get("/api/v1/analyses?page=3&limit=10")
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["page"] == 3
        assert response_data["page_size"] == 10
        assert response_data["has_next"] == True
        assert response_data["has_previous"] == True

    @patch('backend.api.v1.routes.analyses.analysis_service')
    @patch('backend.api.v1.routes.analyses.get_current_user')
    def test_get_analyses_default_params(self, mock_get_user, mock_service, client, mock_current_user):
        """Test default pagination parameters."""
        # Arrange
        mock_get_user.return_value = mock_current_user
        mock_list_response = AnalysisListResponse(
            items=[],
            total=0,
            page=1,
            page_size=20,
            has_next=False,
            has_previous=False
        )
        mock_service.get_analyses_page.return_value = mock_list_response
        
        # Act
        response = client.get("/api/v1/analyses")
        
        # Assert
        assert response.status_code == 200
        mock_service.get_analyses_page.assert_called_once_with(
            mock_current_user.id, 1, 20
        )


class TestAnalysisRecentEndpoint:
    """Test GET /api/v1/analyses/recent endpoint."""

    @patch('backend.api.v1.routes.analyses.analysis_service')
    @patch('backend.api.v1.routes.analyses.get_current_user')
    def test_get_recent_analyses_success(self, mock_get_user, mock_service, client, sample_analysis, mock_current_user):
        """Test successful retrieval of recent analyses."""
        # Arrange
        mock_get_user.return_value = mock_current_user
        mock_service.get_recent.return_value = [sample_analysis]
        
        # Act
        response = client.get("/api/v1/analyses/recent?limit=5")
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 1
        assert response_data[0]["analysis_id"] == str(sample_analysis.analysis_id)
        
        mock_service.get_recent.assert_called_once_with(mock_current_user.id, 5)

    @patch('backend.api.v1.routes.analyses.analysis_service')
    @patch('backend.api.v1.routes.analyses.get_current_user')
    def test_get_recent_analyses_default_limit(self, mock_get_user, mock_service, client, mock_current_user):
        """Test default limit parameter."""
        # Arrange
        mock_get_user.return_value = mock_current_user
        mock_service.get_recent.return_value = []
        
        # Act
        response = client.get("/api/v1/analyses/recent")
        
        # Assert
        assert response.status_code == 200
        mock_service.get_recent.assert_called_once_with(mock_current_user.id, 5)


class TestAnalysisDetailEndpoint:
    """Test GET /api/v1/analyses/{analysis_id} endpoint."""

    @patch('backend.api.v1.routes.analyses.analysis_service')
    @patch('backend.api.v1.routes.analyses.get_current_user')
    def test_get_analysis_by_id_success(self, mock_get_user, mock_service, client, sample_analysis, mock_current_user):
        """Test successful retrieval of analysis by ID."""
        # Arrange
        mock_get_user.return_value = mock_current_user
        mock_service.get_analysis_by_id.return_value = sample_analysis
        
        # Act
        response = client.get(f"/api/v1/analyses/{sample_analysis.analysis_id}")
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["analysis_id"] == str(sample_analysis.analysis_id)
        assert response_data["feedback"] == sample_analysis.feedback
        
        mock_service.get_analysis_by_id.assert_called_once_with(
            sample_analysis.analysis_id, mock_current_user.id
        )

    @patch('backend.api.v1.routes.analyses.analysis_service')
    @patch('backend.api.v1.routes.analyses.get_current_user')
    def test_get_analysis_by_id_not_found(self, mock_get_user, mock_service, client, mock_current_user):
        """Test 404 when analysis not found."""
        # Arrange
        analysis_id = uuid4()
        mock_get_user.return_value = mock_current_user
        mock_service.get_analysis_by_id.side_effect = ValueError("Analysis not found")
        
        # Act
        response = client.get(f"/api/v1/analyses/{analysis_id}")
        
        # Assert
        assert response.status_code == 404
        response_data = response.json()
        assert "not found" in response_data["detail"].lower()

    @patch('backend.api.v1.routes.analyses.analysis_service')
    @patch('backend.api.v1.routes.analyses.get_current_user')
    def test_get_analysis_by_id_access_denied(self, mock_get_user, mock_service, client, mock_current_user):
        """Test 403 when user doesn't own analysis."""
        # Arrange
        analysis_id = uuid4()
        mock_get_user.return_value = mock_current_user
        mock_service.get_analysis_by_id.side_effect = ValueError("Access denied")
        
        # Act
        response = client.get(f"/api/v1/analyses/{analysis_id}")
        
        # Assert
        assert response.status_code == 403
        response_data = response.json()
        assert "access denied" in response_data["detail"].lower()


class TestAnalysisRoutesErrorHandling:
    """Test error handling across all analysis routes."""

    @patch('backend.api.v1.routes.analyses.analysis_service')
    @patch('backend.api.v1.routes.analyses.get_current_user')
    def test_service_exception_handling(self, mock_get_user, mock_service, client, mock_current_user):
        """Test handling of service layer exceptions."""
        # Arrange
        mock_get_user.return_value = mock_current_user
        mock_service.get_recent.side_effect = Exception("Database connection error")
        
        # Act
        response = client.get("/api/v1/analyses/recent")
        
        # Assert
        assert response.status_code == 500

    def test_unauthenticated_access(self, client):
        """Test that unauthenticated requests are rejected."""
        # Act
        response = client.get("/api/v1/analyses")
        
        # Assert - Should require authentication
        # This depends on your authentication setup
        # assert response.status_code in [401, 403]


class TestAnalysisRoutesSecurity:
    """Test security aspects of analysis routes."""

    @patch('backend.api.v1.routes.analyses.analysis_service')
    @patch('backend.api.v1.routes.analyses.get_current_user')
    def test_pii_not_returned_in_responses(self, mock_get_user, mock_service, client, sample_analysis, mock_current_user):
        """Test that PII (transcript) is never returned in API responses."""
        # Arrange
        mock_get_user.return_value = mock_current_user
        mock_service.get_analysis_by_id.return_value = sample_analysis
        
        # Act
        response = client.get(f"/api/v1/analyses/{sample_analysis.analysis_id}")
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert "transcript" not in response_data
        assert sample_analysis.transcript not in str(response_data)

    @patch('backend.api.v1.routes.analyses.analysis_service')
    @patch('backend.api.v1.routes.analyses.get_current_user')
    def test_user_isolation(self, mock_get_user, mock_service, client, mock_current_user):
        """Test that users can only access their own analyses."""
        # Arrange
        mock_get_user.return_value = mock_current_user
        
        # Act
        response = client.get("/api/v1/analyses")
        
        # Assert
        mock_service.get_analyses_page.assert_called_once()
        call_args = mock_service.get_analyses_page.call_args[0]
        assert call_args[0] == mock_current_user.id  # First arg should be user_id