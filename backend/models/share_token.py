"""
ShareToken model for MasterSpeak-AI.
Provides secure tokenized sharing of analysis results with expiration.
"""

from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import secrets
import hashlib


class ShareToken(SQLModel, table=True):
    """
    Share token model for secure analysis sharing.
    
    Features:
    - Cryptographically secure token generation
    - Hashed token storage for security
    - Automatic expiration (default 7 days)
    - Links to specific analysis results
    - Audit trail with creation timestamps
    """
    
    # Primary fields
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    analysis_id: UUID = Field(foreign_key="analysis.id", index=True)
    
    # Security fields
    hashed_token: str = Field(description="SHA-256 hash of the share token")
    expires_at: datetime = Field(description="Token expiration timestamp", index=True)
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    @classmethod
    def create_token(cls, analysis_id: UUID, expires_in_days: int = 7) -> tuple['ShareToken', str]:
        """
        Create a new share token with cryptographically secure random token.
        
        Args:
            analysis_id: UUID of the analysis to share
            expires_in_days: Number of days until token expires (default 7)
            
        Returns:
            tuple: (ShareToken instance, raw_token_string)
        """
        # Generate cryptographically secure token (32 bytes = 256 bits)
        raw_token = secrets.token_urlsafe(32)
        
        # Hash the token for database storage
        hashed_token = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
        
        # Calculate expiration time
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create token instance
        token = cls(
            analysis_id=analysis_id,
            hashed_token=hashed_token,
            expires_at=expires_at
        )
        
        return token, raw_token
    
    @staticmethod
    def hash_token(raw_token: str) -> str:
        """
        Hash a raw token for comparison against stored hashes.
        
        Args:
            raw_token: The raw token string to hash
            
        Returns:
            str: SHA-256 hash of the token
        """
        return hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
    
    def is_expired(self) -> bool:
        """
        Check if the token has expired.
        
        Returns:
            bool: True if token is expired, False otherwise
        """
        return datetime.utcnow() > self.expires_at


class ShareTokenCreate(SQLModel):
    """
    Pydantic model for share token creation requests.
    """
    analysis_id: UUID
    expires_in_days: Optional[int] = 7


class ShareTokenResponse(SQLModel):
    """
    Pydantic model for share token creation responses.
    """
    share_url: str
    expires_at: datetime
    token_id: UUID


class SharedAnalysisResponse(SQLModel):
    """
    Pydantic model for shared analysis responses (redacted).
    Excludes sensitive information like transcripts unless explicitly allowed.
    """
    analysis_id: UUID
    speech_id: UUID
    metrics: Optional[dict] = None
    summary: Optional[str] = None
    feedback: str
    created_at: datetime
    
    # Conditionally included fields
    transcript: Optional[str] = None
    
    # Metadata
    shared: bool = Field(default=True, description="Indicates this is a shared view")
    transcript_included: bool = Field(default=False, description="Whether transcript is included")