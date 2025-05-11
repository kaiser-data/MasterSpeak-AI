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
    
from fastapi import Request
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Create limiter instance (if available)
if SLOWAPI_AVAILABLE:
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["100/minute"]
    )
else:
    # Mock limiter for when slowapi is not available
    class MockLimiter:
        def limit(self, limit_string):
            def decorator(func):
                return func
            return decorator
    limiter = MockLimiter()

# Custom rate limit exceeded handler
def rate_limit_exceeded_handler(request: Request, exc):
    """
    Custom handler for rate limit exceeded errors.
    """
    if SLOWAPI_AVAILABLE:
        logger.warning(f"Rate limit exceeded for {get_remote_address(request)}: {getattr(exc, 'detail', str(exc))}")
        
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "detail": getattr(exc, 'detail', str(exc)),
                "retry_after": getattr(exc, "retry_after", None),
                "timestamp": "2025-08-08T01:51:03.201098"
            },
            headers={"Retry-After": str(getattr(exc, "retry_after", 60))}
        )
    else:
        # Fallback handler when slowapi is not available
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "detail": "Too many requests",
                "timestamp": "2025-08-08T01:51:03.201098"
            }
        )

# Rate limiting configurations for different endpoints
class RateLimits:
    """Rate limiting configurations for different endpoint types"""
    
    # Authentication endpoints - more restrictive
    AUTH_LOGIN = "5/minute"
    AUTH_REGISTER = "3/minute" 
    AUTH_RESET_PASSWORD = "2/minute"
    
    # Analysis endpoints - moderate limits
    ANALYSIS_TEXT = "10/minute"
    ANALYSIS_UPLOAD = "5/minute"
    
    # General API endpoints
    API_READ = "30/minute"
    API_WRITE = "15/minute"
    
    # Health/Status endpoints - very permissive
    HEALTH_CHECK = "60/minute"