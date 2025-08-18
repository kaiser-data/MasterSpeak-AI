# backend/middleware/rate_limiting.py

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware
    SLOWAPI_AVAILABLE = True
except ImportError:
    SLOWAPI_AVAILABLE = False
    # Mock functions for when slowapi is not available
    def get_remote_address(request):
        return request.client.host if request.client else "unknown"

try:
    import redis
    REDIS_AVAILABLE = True
    Redis = redis.Redis  # Type alias for annotation
except ImportError:
    REDIS_AVAILABLE = False
    # Mock redis for type annotation when not available
    class Redis:
        pass
    
from fastapi import Request
from starlette.responses import JSONResponse
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Import settings
from backend.config import settings

# Import Sentry for 429 tagging (if available)
try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

# Import structured logging
from backend.logging_config import log_rate_limit_event, get_request_id

# Redis client setup with graceful fallback
redis_client: Optional[Redis] = None
if settings.REDIS_URL and settings.RATE_LIMIT_ENABLED and REDIS_AVAILABLE:
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        redis_client.ping()  # Test connection
        logger.info("Redis connected for rate limiting")
    except Exception as e:
        logger.warning(f"Redis unavailable, using in-memory rate limiting: {e}")
        redis_client = None

# Create limiter instance with Redis backend support
if SLOWAPI_AVAILABLE and settings.RATE_LIMIT_ENABLED:
    if redis_client and settings.REDIS_URL:
        try:
            limiter = Limiter(
                key_func=get_remote_address,
                default_limits=[settings.RATE_LIMIT_DEFAULT],
                storage_uri=settings.REDIS_URL
            )
            logger.info(f"Rate limiting enabled with Redis backend: {settings.RATE_LIMIT_DEFAULT}")
        except Exception as e:
            logger.warning(f"Failed to use Redis for rate limiting: {e}")
            limiter = Limiter(
                key_func=get_remote_address,
                default_limits=[settings.RATE_LIMIT_DEFAULT]
            )
            logger.info(f"Rate limiting enabled with in-memory backend: {settings.RATE_LIMIT_DEFAULT}")
    else:
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[settings.RATE_LIMIT_DEFAULT]
        )
        logger.info(f"Rate limiting enabled with in-memory backend: {settings.RATE_LIMIT_DEFAULT}")
elif settings.RATE_LIMIT_ENABLED:
    logger.warning("Rate limiting requested but SlowAPI not available")
    # Mock limiter for when slowapi is not available but rate limiting is enabled
    class MockLimiter:
        def limit(self, limit_string):
            def decorator(func):
                return func
            return decorator
    limiter = MockLimiter()
else:
    logger.info("Rate limiting disabled")
    # Mock limiter when rate limiting is disabled
    class MockLimiter:
        def limit(self, limit_string):
            def decorator(func):
                return func
            return decorator
    limiter = MockLimiter()

# Custom rate limit exceeded handler with enhanced response structure
def rate_limit_exceeded_handler(request: Request, exc):
    """
    Enhanced handler for rate limit exceeded errors with structured response.
    """
    client_ip = get_remote_address(request)
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    if SLOWAPI_AVAILABLE and settings.RATE_LIMIT_ENABLED:
        # Extract rate limit info from exception
        detail = getattr(exc, 'detail', 'Rate limit exceeded')
        retry_after = getattr(exc, 'retry_after', 60)
        
        # Parse rate limit from detail (e.g., "60 per 1 minute")
        limit_info = detail if isinstance(detail, str) else "60/minute"
        
        # Calculate reset time
        reset_time = datetime.utcnow()
        reset_time = reset_time.replace(second=0, microsecond=0)  # Round to minute
        if "minute" in limit_info:
            from datetime import timedelta
            reset_time += timedelta(minutes=1)
        reset_time_str = reset_time.isoformat() + "Z"
        
        # Enhanced logging with request ID and structured data
        request_id = get_request_id()
        logger.warning(
            f"Rate limit exceeded for {client_ip}: {detail}",
            extra={
                'event_type': 'rate_limit_exceeded',
                'client_ip': client_ip,
                'endpoint': request.url.path,
                'method': request.method,
                'limit': limit_info,
                'retry_after': retry_after,
                'request_id': request_id,
                'user_agent': request.headers.get('user-agent', 'unknown')
            }
        )
        
        # Log to structured rate limit logger
        log_rate_limit_event(
            client_ip=client_ip,
            endpoint=request.url.path,
            limit=limit_info,
            retry_after=retry_after,
            user_agent=request.headers.get('user-agent')
        )
        
        # Tag with Sentry if available
        if SENTRY_AVAILABLE and hasattr(settings, 'SENTRY_DSN') and settings.SENTRY_DSN:
            with sentry_sdk.configure_scope() as scope:
                scope.set_tag("event_type", "rate_limit_exceeded")
                scope.set_tag("client_ip", client_ip)
                scope.set_tag("endpoint", request.url.path)
                scope.set_tag("rate_limit", limit_info)
                scope.set_context("rate_limit", {
                    "client_ip": client_ip,
                    "endpoint": request.url.path,
                    "method": request.method,
                    "limit": limit_info,
                    "retry_after": retry_after,
                    "user_agent": request.headers.get('user-agent'),
                    "request_id": request_id
                })
                sentry_sdk.add_breadcrumb(
                    message=f"Rate limit exceeded: {client_ip} on {request.url.path}",
                    category="rate_limiting",
                    level="warning",
                    data={
                        "limit": limit_info,
                        "retry_after": retry_after
                    }
                )
        
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "detail": detail,
                "retry_after": retry_after,
                "timestamp": timestamp,
                "limit": limit_info,
                "remaining": 0,
                "reset_time": reset_time_str,
                "client_ip": client_ip,
                "request_id": request_id
            },
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": limit_info,
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": reset_time_str
            }
        )
    else:
        # Fallback handler when slowapi is not available or rate limiting is disabled
        request_id = get_request_id()
        logger.warning(f"Rate limit fallback triggered for {client_ip}",
                      extra={'request_id': request_id, 'client_ip': client_ip})
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "detail": "Too many requests",
                "timestamp": timestamp,
                "client_ip": client_ip,
                "request_id": request_id
            },
            headers={"Retry-After": "60"}
        )

# Enhanced rate limiting configurations using environment settings
class RateLimits:
    """Rate limiting configurations for different endpoint types with ENV overrides"""
    
    # Authentication endpoints - more restrictive
    AUTH_LOGIN = settings.RATE_LIMIT_AUTH
    AUTH_REGISTER = "3/minute"  # Keep restrictive for registration
    AUTH_RESET_PASSWORD = "2/minute"  # Keep restrictive for security
    
    # Analysis endpoints - configurable
    ANALYSIS_TEXT = settings.RATE_LIMIT_ANALYSIS
    ANALYSIS_UPLOAD = settings.RATE_LIMIT_UPLOAD
    
    # General API endpoints
    API_READ = "30/minute"
    API_WRITE = "15/minute"
    
    # Health/Status endpoints - configurable
    HEALTH_CHECK = settings.RATE_LIMIT_HEALTH
    
    # Share endpoints - moderate restriction
    SHARE_CREATE = "5/minute"
    SHARE_ACCESS = "60/minute"
    
    # Default fallback
    DEFAULT = settings.RATE_LIMIT_DEFAULT

# Utility functions for rate limiting
def get_rate_limit_status():
    """Get current rate limiting status and configuration"""
    return {
        "enabled": settings.RATE_LIMIT_ENABLED,
        "default_limit": settings.RATE_LIMIT_DEFAULT,
        "redis_backend": bool(redis_client),
        "redis_url": settings.REDIS_URL if settings.REDIS_URL else None,
        "slowapi_available": SLOWAPI_AVAILABLE,
        "redis_available": REDIS_AVAILABLE
    }

def create_rate_limit_decorator(limit: str):
    """Create a rate limit decorator with the specified limit"""
    if settings.RATE_LIMIT_ENABLED and SLOWAPI_AVAILABLE:
        return limiter.limit(limit)
    else:
        # Return a no-op decorator when rate limiting is disabled
        def decorator(func):
            return func
        return decorator