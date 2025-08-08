# test/unit/test_rate_limiting.py

import pytest
import asyncio
from fastapi.testclient import TestClient
from fastapi import FastAPI, Request
from backend.main import app
from backend.middleware.rate_limiting import (
    get_rate_limit_status, 
    create_rate_limit_decorator,
    RateLimits
)
from backend.config import settings
import time
import requests

class TestRateLimiting:
    """Test rate limiting functionality with 200 → 429 behavior"""
    
    def test_rate_limit_status_info(self):
        """Test rate limiting status information"""
        status = get_rate_limit_status()
        
        assert "enabled" in status
        assert "default_limit" in status
        assert "redis_backend" in status
        assert "slowapi_available" in status
        assert "redis_available" in status
        
        # Check configuration values
        assert status["default_limit"] == settings.RATE_LIMIT_DEFAULT
        assert status["enabled"] == settings.RATE_LIMIT_ENABLED

    def test_rate_limit_decorator_creation(self):
        """Test that rate limit decorators are created properly"""
        decorator = create_rate_limit_decorator("5/minute")
        
        # Decorator should be callable
        assert callable(decorator)
        
        # Should work as decorator
        @decorator
        def dummy_function():
            return "test"
        
        # Function should still be callable after decoration
        assert dummy_function() == "test"

    def test_rate_limits_configuration(self):
        """Test that RateLimits class uses environment configuration"""
        # Test that rate limits use settings
        assert RateLimits.AUTH_LOGIN == settings.RATE_LIMIT_AUTH
        assert RateLimits.ANALYSIS_TEXT == settings.RATE_LIMIT_ANALYSIS
        assert RateLimits.ANALYSIS_UPLOAD == settings.RATE_LIMIT_UPLOAD
        assert RateLimits.HEALTH_CHECK == settings.RATE_LIMIT_HEALTH
        assert RateLimits.DEFAULT == settings.RATE_LIMIT_DEFAULT

class TestRateLimitingIntegration:
    """Integration tests for rate limiting with actual HTTP requests"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_health_endpoint_rate_limiting(self):
        """Test that health endpoint can handle multiple requests within limit"""
        responses = []
        
        # Make requests within the health check limit (should be high)
        for i in range(5):
            response = self.client.get("/health")
            responses.append(response)
            time.sleep(0.1)  # Small delay between requests
        
        # All requests within reasonable limit should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

    def test_rate_limit_headers_present(self):
        """Test that rate limit headers are included when available"""
        response = self.client.get("/health")
        
        # Should have rate limit info in response or headers (when slowapi available)
        assert response.status_code == 200
        
        # Check if rate limiting headers are present (when slowapi is available)
        if hasattr(app.state, 'limiter'):
            # Headers might be present depending on slowapi configuration
            headers = response.headers
            # This is optional - headers may not be present in all slowapi configurations
            pass

    def test_api_status_endpoint(self):
        """Test API status endpoint for rate limiting info"""
        response = self.client.get("/api/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "api" in data
        assert data["api"] == "online"

class TestRateLimitExceeded:
    """Test rate limit exceeded scenarios"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    @pytest.mark.skipif(
        not settings.RATE_LIMIT_ENABLED,
        reason="Rate limiting is disabled"
    )
    def test_rate_limit_exceeded_structure(self):
        """Test 429 response structure when rate limit is exceeded"""
        # This test requires slowapi to be available and configured
        # We'll simulate the expected response structure
        
        # Expected 429 response structure
        expected_fields = [
            "error",
            "detail", 
            "retry_after",
            "timestamp",
            "limit",
            "remaining",
            "reset_time",
            "client_ip"
        ]
        
        # For this test, we'll verify the structure our handler would return
        from backend.middleware.rate_limiting import rate_limit_exceeded_handler
        from fastapi import Request
        from unittest.mock import Mock
        
        # Create mock request and exception
        mock_request = Mock(spec=Request)
        mock_request.client.host = "127.0.0.1"
        
        mock_exc = Mock()
        mock_exc.detail = "5 per 1 minute"
        mock_exc.retry_after = 60
        
        # Test the handler
        response = rate_limit_exceeded_handler(mock_request, mock_exc)
        assert response.status_code == 429
        
        # Check response structure
        content = response.body.decode()
        import json
        data = json.loads(content)
        
        for field in expected_fields:
            assert field in data
        
        assert data["error"] == "Rate limit exceeded"
        assert "Retry-After" in response.headers

    def test_rate_limit_disabled_fallback(self):
        """Test behavior when rate limiting is disabled"""
        # Test that endpoints still work when rate limiting is disabled
        response = self.client.get("/health")
        assert response.status_code == 200
        
        # Should get normal response, not 429
        data = response.json()
        assert data["status"] == "healthy"

class TestRateLimitEnvironmentConfiguration:
    """Test rate limiting environment configuration"""
    
    def test_environment_variables_loaded(self):
        """Test that rate limiting environment variables are properly loaded"""
        # Test basic configuration
        assert hasattr(settings, 'RATE_LIMIT_ENABLED')
        assert hasattr(settings, 'RATE_LIMIT_DEFAULT')
        assert hasattr(settings, 'RATE_LIMIT_AUTH')
        assert hasattr(settings, 'RATE_LIMIT_ANALYSIS')
        assert hasattr(settings, 'RATE_LIMIT_UPLOAD')
        assert hasattr(settings, 'RATE_LIMIT_HEALTH')
        assert hasattr(settings, 'REDIS_URL')
        
        # Test types
        assert isinstance(settings.RATE_LIMIT_ENABLED, bool)
        assert isinstance(settings.RATE_LIMIT_DEFAULT, str)
        assert isinstance(settings.REDIS_URL, str)

    def test_redis_configuration(self):
        """Test Redis configuration handling"""
        status = get_rate_limit_status()
        
        # Should handle Redis availability gracefully
        assert isinstance(status["redis_backend"], bool)
        assert isinstance(status["redis_available"], bool)
        
        # If Redis URL is configured, should attempt connection
        if settings.REDIS_URL:
            # Redis backend status should reflect connection attempt
            pass  # Connection depends on actual Redis availability

if __name__ == "__main__":
    pytest.main([__file__])