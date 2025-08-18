"""
Unit tests for ShareToken model and functionality.
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.share_token import ShareToken, ShareTokenCreate, ShareTokenResponse, SharedAnalysisResponse
from backend.models.analysis import Analysis


class TestShareToken:
    """Test ShareToken model functionality."""
    
    def test_create_token(self):
        """Test token creation with proper hashing and expiration."""
        analysis_id = uuid4()
        
        # Create token
        token, raw_token = ShareToken.create_token(analysis_id, expires_in_days=7)
        
        # Verify token properties
        assert token.analysis_id == analysis_id
        assert token.hashed_token is not None
        assert len(token.hashed_token) == 64  # SHA-256 hex length
        assert token.expires_at > datetime.utcnow()
        assert token.created_at <= datetime.utcnow()
        
        # Verify raw token
        assert raw_token is not None
        assert len(raw_token) > 20  # URL-safe base64 should be reasonably long
        
        # Verify hash matches
        assert ShareToken.hash_token(raw_token) == token.hashed_token
    
    def test_hash_token(self):
        """Test token hashing function."""
        test_token = "test_token_123"
        
        hash1 = ShareToken.hash_token(test_token)
        hash2 = ShareToken.hash_token(test_token)
        
        # Same input should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex length
        
        # Different input should produce different hash
        hash3 = ShareToken.hash_token("different_token")
        assert hash1 != hash3
    
    def test_is_expired(self):
        """Test token expiration check."""
        analysis_id = uuid4()
        
        # Create expired token
        expired_token, _ = ShareToken.create_token(analysis_id, expires_in_days=-1)
        assert expired_token.is_expired() is True
        
        # Create valid token
        valid_token, _ = ShareToken.create_token(analysis_id, expires_in_days=7)
        assert valid_token.is_expired() is False
    
    def test_token_uniqueness(self):
        """Test that each token creation produces unique tokens."""
        analysis_id = uuid4()
        
        token1, raw1 = ShareToken.create_token(analysis_id)
        token2, raw2 = ShareToken.create_token(analysis_id)
        
        # Different raw tokens
        assert raw1 != raw2
        
        # Different hashed tokens
        assert token1.hashed_token != token2.hashed_token
        
        # Same analysis ID
        assert token1.analysis_id == token2.analysis_id


class TestShareTokenCreate:
    """Test ShareTokenCreate schema."""
    
    def test_valid_creation(self):
        """Test valid token creation request."""
        analysis_id = uuid4()
        
        request = ShareTokenCreate(
            analysis_id=analysis_id,
            expires_in_days=14
        )
        
        assert request.analysis_id == analysis_id
        assert request.expires_in_days == 14
    
    def test_default_expiration(self):
        """Test default expiration setting."""
        analysis_id = uuid4()
        
        request = ShareTokenCreate(analysis_id=analysis_id)
        
        assert request.expires_in_days == 7  # Default value


class TestShareTokenResponse:
    """Test ShareTokenResponse schema."""
    
    def test_response_creation(self):
        """Test share token response creation."""
        token_id = uuid4()
        share_url = "https://example.com/share/token123"
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        response = ShareTokenResponse(
            share_url=share_url,
            expires_at=expires_at,
            token_id=token_id
        )
        
        assert response.share_url == share_url
        assert response.expires_at == expires_at
        assert response.token_id == token_id


class TestSharedAnalysisResponse:
    """Test SharedAnalysisResponse schema."""
    
    def test_basic_response(self):
        """Test basic shared analysis response."""
        analysis_id = uuid4()
        speech_id = uuid4()
        user_id = uuid4()
        
        response = SharedAnalysisResponse(
            analysis_id=analysis_id,
            speech_id=speech_id,
            user_id=user_id,
            feedback="Test feedback",
            created_at=datetime.utcnow()
        )
        
        assert response.analysis_id == analysis_id
        assert response.speech_id == speech_id
        assert response.user_id == user_id
        assert response.feedback == "Test feedback"
        assert response.shared is True
        assert response.transcript_included is False
        assert response.transcript is None
    
    def test_response_with_transcript(self):
        """Test shared analysis response with transcript."""
        analysis_id = uuid4()
        speech_id = uuid4()
        user_id = uuid4()
        
        response = SharedAnalysisResponse(
            analysis_id=analysis_id,
            speech_id=speech_id,
            user_id=user_id,
            feedback="Test feedback",
            created_at=datetime.utcnow(),
            transcript="This is a test transcript",
            transcript_included=True
        )
        
        assert response.transcript == "This is a test transcript"
        assert response.transcript_included is True
    
    def test_response_with_metrics(self):
        """Test shared analysis response with metrics."""
        analysis_id = uuid4()
        speech_id = uuid4()
        user_id = uuid4()
        
        metrics = {
            "word_count": 150,
            "clarity_score": 8,
            "structure_score": 7,
            "filler_word_count": 3
        }
        
        response = SharedAnalysisResponse(
            analysis_id=analysis_id,
            speech_id=speech_id,
            user_id=user_id,
            feedback="Test feedback",
            created_at=datetime.utcnow(),
            metrics=metrics
        )
        
        assert response.metrics == metrics


@pytest.mark.asyncio
class TestShareTokenDatabase:
    """Test ShareToken database operations."""
    
    async def test_token_persistence(self, test_session: AsyncSession):
        """Test saving and retrieving tokens from database."""
        analysis_id = uuid4()
        
        # Create and save token
        token, raw_token = ShareToken.create_token(analysis_id, expires_in_days=7)
        test_session.add(token)
        await test_session.commit()
        await test_session.refresh(token)
        
        # Retrieve token
        result = await test_session.execute(
            select(ShareToken).where(ShareToken.id == token.id)
        )
        retrieved_token = result.scalar_one_or_none()
        
        assert retrieved_token is not None
        assert retrieved_token.analysis_id == analysis_id
        assert retrieved_token.hashed_token == token.hashed_token
        
    async def test_token_lookup_by_hash(self, test_session: AsyncSession):
        """Test looking up tokens by hash."""
        analysis_id = uuid4()
        
        # Create and save token
        token, raw_token = ShareToken.create_token(analysis_id)
        test_session.add(token)
        await test_session.commit()
        
        # Look up by hash
        hashed_token = ShareToken.hash_token(raw_token)
        result = await test_session.execute(
            select(ShareToken).where(ShareToken.hashed_token == hashed_token)
        )
        retrieved_token = result.scalar_one_or_none()
        
        assert retrieved_token is not None
        assert retrieved_token.id == token.id
        
    async def test_expired_token_query(self, test_session: AsyncSession):
        """Test filtering expired tokens."""
        analysis_id = uuid4()
        
        # Create expired token
        expired_token, _ = ShareToken.create_token(analysis_id, expires_in_days=-1)
        test_session.add(expired_token)
        
        # Create valid token
        valid_token, raw_token = ShareToken.create_token(analysis_id, expires_in_days=7)
        test_session.add(valid_token)
        
        await test_session.commit()
        
        # Query for valid tokens only
        result = await test_session.execute(
            select(ShareToken).where(
                ShareToken.hashed_token == ShareToken.hash_token(raw_token),
                ShareToken.expires_at > datetime.utcnow()
            )
        )
        retrieved_token = result.scalar_one_or_none()
        
        assert retrieved_token is not None
        assert retrieved_token.id == valid_token.id
        
        # Query for expired tokens should return none
        expired_hash = expired_token.hashed_token
        result = await test_session.execute(
            select(ShareToken).where(
                ShareToken.hashed_token == expired_hash,
                ShareToken.expires_at > datetime.utcnow()
            )
        )
        retrieved_expired = result.scalar_one_or_none()
        assert retrieved_expired is None