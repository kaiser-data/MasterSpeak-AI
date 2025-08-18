"""
Enhanced token bucket rate limiting middleware for MasterSpeak-AI.
Applies to all mutating endpoints (POST, PUT, PATCH, DELETE) with configurable limits.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from collections import defaultdict
import json

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from backend.utils.logging import logger, get_request_id, get_user_id


class TokenBucket:
    """Token bucket implementation for rate limiting."""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket.
        
        Args:
            capacity: Maximum number of tokens in bucket
            refill_rate: Tokens per second refill rate
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were consumed, False if insufficient tokens
        """
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """Get time to wait until tokens are available."""
        self._refill()
        
        if self.tokens >= tokens:
            return 0.0
        
        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate


class RateLimitConfig:
    """Rate limiting configuration for different endpoints."""
    
    # Default limits (tokens per minute)
    DEFAULT_CAPACITY = 60
    DEFAULT_REFILL_RATE = 1.0  # 1 token per second = 60 per minute
    
    # Endpoint-specific configurations
    ENDPOINT_LIMITS = {
        # Authentication endpoints - more restrictive
        '/api/v1/auth/jwt/login': (5, 5/60),  # 5 requests per minute
        '/api/v1/auth/register': (3, 3/60),   # 3 requests per minute
        '/api/v1/auth/reset-password': (2, 2/60),  # 2 requests per minute
        
        # Analysis endpoints - moderate limits
        '/api/v1/analysis/text': (10, 10/60),     # 10 requests per minute
        '/api/v1/analysis/upload': (5, 5/60),     # 5 requests per minute
        '/api/v1/analysis/complete': (10, 10/60), # 10 requests per minute
        
        # Export endpoints - restricted
        '/api/v1/analyses/*/export': (3, 3/60),   # 3 requests per minute
        '/api/v1/share/*': (5, 5/60),             # 5 requests per minute
        
        # General write operations
        '/api/v1/speeches/*': (15, 15/60),        # 15 requests per minute (DELETE)
        '/api/v1/users/*': (10, 10/60),           # 10 requests per minute
    }
    
    # HTTP methods that should be rate limited
    RATE_LIMITED_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}
    
    @classmethod
    def get_limit_for_endpoint(cls, path: str, method: str) -> Tuple[int, float]:
        """Get rate limit configuration for endpoint."""
        if method not in cls.RATE_LIMITED_METHODS:
            return cls.DEFAULT_CAPACITY, cls.DEFAULT_REFILL_RATE
        
        # Check for exact path match
        if path in cls.ENDPOINT_LIMITS:
            return cls.ENDPOINT_LIMITS[path]
        
        # Check for wildcard matches
        for pattern, (capacity, rate) in cls.ENDPOINT_LIMITS.items():
            if '*' in pattern:
                pattern_parts = pattern.split('*')
                if len(pattern_parts) == 2:
                    prefix, suffix = pattern_parts
                    if path.startswith(prefix) and path.endswith(suffix):
                        return capacity, rate
        
        return cls.DEFAULT_CAPACITY, cls.DEFAULT_REFILL_RATE


class TokenBucketRateLimiter:
    """Token bucket rate limiter with in-memory storage."""
    
    def __init__(self):
        self.buckets: Dict[str, TokenBucket] = {}
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    def get_client_key(self, request: Request) -> str:
        """Get unique key for client (IP + User ID if authenticated)."""
        client_ip = request.client.host if request.client else "unknown"
        user_id = get_user_id()
        
        if user_id:
            return f"user:{user_id}"
        return f"ip:{client_ip}"
    
    def get_bucket(self, key: str, capacity: int, refill_rate: float) -> TokenBucket:
        """Get or create token bucket for key."""
        if key not in self.buckets:
            self.buckets[key] = TokenBucket(capacity, refill_rate)
        return self.buckets[key]
    
    def is_allowed(self, request: Request) -> Tuple[bool, Optional[float]]:
        """Check if request is allowed under rate limits."""
        method = request.method
        path = request.url.path
        
        # Only rate limit mutating operations
        if method not in RateLimitConfig.RATE_LIMITED_METHODS:
            return True, None
        
        # Get rate limit configuration
        capacity, refill_rate = RateLimitConfig.get_limit_for_endpoint(path, method)
        
        # Get client bucket
        client_key = self.get_client_key(request)
        bucket = self.get_bucket(client_key, capacity, refill_rate)
        
        # Try to consume token
        if bucket.consume():
            return True, None
        
        # Return wait time if rate limited
        wait_time = bucket.get_wait_time()
        return False, wait_time
    
    def cleanup_old_buckets(self):
        """Remove unused buckets to prevent memory leaks."""
        now = time.time()
        if now - self.last_cleanup < self.cleanup_interval:
            return
        
        # Remove buckets that haven't been used recently
        cutoff_time = now - self.cleanup_interval
        keys_to_remove = []
        
        for key, bucket in self.buckets.items():
            if bucket.last_refill < cutoff_time:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.buckets[key]
        
        self.last_cleanup = now
        
        if keys_to_remove:
            logger.debug(
                f"Cleaned up {len(keys_to_remove)} unused rate limit buckets",
                operation="rate_limit_cleanup",
                buckets_removed=len(keys_to_remove)
            )


# Global rate limiter instance
rate_limiter = TokenBucketRateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using token bucket algorithm."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        
        # Cleanup old buckets periodically
        rate_limiter.cleanup_old_buckets()
        
        # Check rate limit
        is_allowed, wait_time = rate_limiter.is_allowed(request)
        
        if not is_allowed:
            # Log rate limit violation
            client_key = rate_limiter.get_client_key(request)
            request_id = get_request_id()
            
            logger.warning(
                f"Rate limit exceeded for {client_key}",
                operation="rate_limit_exceeded",
                client_key=client_key,
                method=request.method,
                path=request.url.path,
                wait_time_seconds=wait_time,
                request_id=request_id
            )
            
            # Calculate retry after header
            retry_after = int(wait_time) + 1
            reset_time = datetime.utcnow() + timedelta(seconds=retry_after)
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Too many {request.method} requests to {request.url.path}",
                    "retry_after": retry_after,
                    "wait_time_seconds": wait_time,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "reset_time": reset_time.isoformat() + "Z",
                    "request_id": request_id,
                    "rate_limit_type": "token_bucket"
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Type": "token_bucket",
                    "X-RateLimit-Reset": reset_time.isoformat() + "Z",
                    "X-Request-ID": request_id or ""
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to successful responses
        if hasattr(response, 'headers'):
            response.headers["X-RateLimit-Type"] = "token_bucket"
            if get_request_id():
                response.headers["X-Request-ID"] = get_request_id()
        
        return response


# Decorator for applying rate limits to specific endpoints
def rate_limit(capacity: int, refill_rate: float):
    """
    Decorator to apply custom rate limits to specific endpoints.
    
    Args:
        capacity: Maximum tokens in bucket
        refill_rate: Tokens per second refill rate
    """
    def decorator(func):
        # Store rate limit config in function metadata
        func._rate_limit_capacity = capacity
        func._rate_limit_refill_rate = refill_rate
        return func
    return decorator


# Utility functions
def get_rate_limit_status(request: Request) -> dict:
    """Get current rate limit status for client."""
    client_key = rate_limiter.get_client_key(request)
    method = request.method
    path = request.url.path
    
    capacity, refill_rate = RateLimitConfig.get_limit_for_endpoint(path, method)
    bucket = rate_limiter.get_bucket(client_key, capacity, refill_rate)
    
    return {
        "client_key": client_key,
        "method": method,
        "path": path,
        "capacity": capacity,
        "refill_rate": refill_rate,
        "current_tokens": int(bucket.tokens),
        "is_rate_limited": method in RateLimitConfig.RATE_LIMITED_METHODS,
        "wait_time_seconds": bucket.get_wait_time() if bucket.tokens < 1 else 0,
    }


def reset_rate_limit(request: Request) -> bool:
    """Reset rate limit for client (admin function)."""
    client_key = rate_limiter.get_client_key(request)
    
    if client_key in rate_limiter.buckets:
        del rate_limiter.buckets[client_key]
        logger.info(
            f"Rate limit reset for {client_key}",
            operation="rate_limit_reset",
            client_key=client_key
        )
        return True
    
    return False


# Configuration validation
def validate_rate_limit_config():
    """Validate rate limiting configuration."""
    errors = []
    
    for endpoint, (capacity, refill_rate) in RateLimitConfig.ENDPOINT_LIMITS.items():
        if capacity <= 0:
            errors.append(f"Invalid capacity for {endpoint}: {capacity}")
        if refill_rate <= 0:
            errors.append(f"Invalid refill_rate for {endpoint}: {refill_rate}")
        if capacity < refill_rate * 60:  # Less than 1 minute of tokens
            errors.append(f"Capacity too low for {endpoint}: {capacity} < {refill_rate * 60}")
    
    if errors:
        logger.error(
            "Rate limiting configuration errors",
            operation="config_validation",
            errors=errors
        )
        raise ValueError(f"Rate limiting configuration errors: {errors}")
    
    logger.info(
        "Rate limiting configuration validated",
        operation="config_validation",
        endpoints_configured=len(RateLimitConfig.ENDPOINT_LIMITS)
    )


# Initialize and validate configuration
validate_rate_limit_config()