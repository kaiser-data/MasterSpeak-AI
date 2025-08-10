# backend/tests/test_analysis_text_optional_user_id.py

import pytest
import httpx
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_text_analysis_without_user_id():
    """Test that text analysis works without user_id (anonymous)"""
    from backend.main import app
    
    client = TestClient(app)
    
    # Test multipart/form-data request without user_id
    response = client.post(
        "/api/v1/analysis/text",
        files={"text": (None, "hello world test analysis")},
        data={"prompt_type": "default"}
    )
    
    # Should not return 422 (validation error)
    assert response.status_code != 422
    # Should be either 200 (success) or 4xx/5xx (but not validation error)
    assert response.status_code in range(200, 600)

@pytest.mark.asyncio 
async def test_simple_text_analysis_without_user_id():
    """Test that simple text analysis works without user_id"""
    from backend.main import app
    
    client = TestClient(app)
    
    response = client.post(
        "/api/v1/analysis/simple-text", 
        files={"text": (None, "hello world test")},
        data={"prompt_type": "default"}
    )
    
    # Should not return 422 (validation error)
    assert response.status_code != 422
    # Simple endpoint should return 200 with mock data
    if response.status_code == 200:
        data = response.json()
        assert "speech_id" in data
        assert "feedback" in data
        assert "word_count" in data