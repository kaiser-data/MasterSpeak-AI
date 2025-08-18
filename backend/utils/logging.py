"""
Structured logging utility for MasterSpeak-AI backend.
Provides request ID propagation, PII redaction, and consistent log formatting.
"""

import json
import logging
import re
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Union
from contextvars import ContextVar
from functools import wraps

# Context variables for request tracking
request_id_context: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_context: ContextVar[Optional[str]] = ContextVar('user_id', default=None)

# PII detection patterns
PII_PATTERNS = [
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL_REDACTED]'),
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), '[SSN_REDACTED]'),
    (re.compile(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'), '[CARD_REDACTED]'),
    (re.compile(r'\b\d{3}-\d{3}-\d{4}\b'), '[PHONE_REDACTED]'),
]

# Sensitive field names to redact
SENSITIVE_FIELDS = {
    'password', 'token', 'secret', 'key', 'transcript', 'content', 
    'audio', 'speech_content', 'transcription', 'api_key', 'auth_token'
}


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return f"req_{uuid.uuid4().hex[:12]}"


def set_request_id(request_id: str) -> None:
    """Set the request ID for the current context."""
    request_id_context.set(request_id)


def get_request_id() -> Optional[str]:
    """Get the current request ID."""
    return request_id_context.get()


def set_user_id(user_id: str) -> None:
    """Set the user ID for the current context."""
    user_id_context.set(user_id)


def get_user_id() -> Optional[str]:
    """Get the current user ID."""
    return user_id_context.get()


def redact_pii(text: str) -> str:
    """Redact PII from text using pattern matching."""
    if not isinstance(text, str):
        return text
    
    redacted = text
    for pattern, replacement in PII_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    
    return redacted


def sanitize_data(data: Any) -> Any:
    """Recursively sanitize data to remove or redact sensitive information."""
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            key_lower = key.lower()
            
            # Redact sensitive fields entirely
            if any(sensitive in key_lower for sensitive in SENSITIVE_FIELDS):
                sanitized[key] = '[REDACTED]'
            else:
                sanitized[key] = sanitize_data(value)
        return sanitized
    
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    
    elif isinstance(data, str):
        return redact_pii(data)
    
    else:
        return data


class StructuredLogger:
    """Structured logger with request ID propagation and PII redaction."""
    
    def __init__(self, service_name: str, logger_name: Optional[str] = None):
        self.service_name = service_name
        self.logger = logging.getLogger(logger_name or service_name)
    
    def _format_log_data(
        self,
        level: str,
        message: str,
        operation: Optional[str] = None,
        duration_ms: Optional[int] = None,
        **metadata
    ) -> Dict[str, Any]:
        """Format log data with standard fields."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level.upper(),
            "service": self.service_name,
            "message": redact_pii(message),
            "request_id": get_request_id(),
            "user_id": get_user_id(),
            "operation": operation,
            "duration_ms": duration_ms,
        }
        
        # Add sanitized metadata
        if metadata:
            log_data["metadata"] = sanitize_data(metadata)
        
        # Remove None values for cleaner logs
        return {k: v for k, v in log_data.items() if v is not None}
    
    def log(
        self,
        level: str,
        message: str,
        operation: Optional[str] = None,
        duration_ms: Optional[int] = None,
        **metadata
    ) -> None:
        """Log a structured message."""
        log_data = self._format_log_data(level, message, operation, duration_ms, **metadata)
        
        # Get the appropriate logging method
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(json.dumps(log_data))
    
    def debug(self, message: str, operation: Optional[str] = None, **metadata) -> None:
        self.log("debug", message, operation, **metadata)
    
    def info(self, message: str, operation: Optional[str] = None, **metadata) -> None:
        self.log("info", message, operation, **metadata)
    
    def warning(self, message: str, operation: Optional[str] = None, **metadata) -> None:
        self.log("warning", message, operation, **metadata)
    
    def error(self, message: str, operation: Optional[str] = None, **metadata) -> None:
        self.log("error", message, operation, **metadata)
    
    def critical(self, message: str, operation: Optional[str] = None, **metadata) -> None:
        self.log("critical", message, operation, **metadata)


# Global logger instances
logger = StructuredLogger("masterspeak_backend")
analysis_logger = StructuredLogger("analysis_service")
auth_logger = StructuredLogger("auth_service")
api_logger = StructuredLogger("api_handler")


def log_performance(operation: str, **metadata):
    """Decorator to log function performance."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            try:
                result = await func(*args, **kwargs)
                duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                logger.info(
                    f"{operation} completed successfully",
                    operation=operation,
                    duration_ms=duration,
                    **metadata
                )
                return result
            except Exception as e:
                duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                logger.error(
                    f"{operation} failed: {str(e)}",
                    operation=operation,
                    duration_ms=duration,
                    error_type=type(e).__name__,
                    error_message=redact_pii(str(e)),
                    **metadata
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            try:
                result = func(*args, **kwargs)
                duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                logger.info(
                    f"{operation} completed successfully",
                    operation=operation,
                    duration_ms=duration,
                    **metadata
                )
                return result
            except Exception as e:
                duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                logger.error(
                    f"{operation} failed: {str(e)}",
                    operation=operation,
                    duration_ms=duration,
                    error_type=type(e).__name__,
                    error_message=redact_pii(str(e)),
                    **metadata
                )
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def log_api_call(method: str, path: str, status_code: int, duration_ms: int, **metadata):
    """Log API call with standard format."""
    api_logger.info(
        f"API call: {method} {path} -> {status_code}",
        operation="api_call",
        duration_ms=duration_ms,
        method=method,
        path=redact_pii(path),
        status_code=status_code,
        **metadata
    )


def log_database_operation(
    operation: str,
    table: str,
    duration_ms: int,
    affected_rows: Optional[int] = None,
    **metadata
):
    """Log database operation with performance metrics."""
    logger.info(
        f"Database {operation} on {table}",
        operation=f"db_{operation}",
        duration_ms=duration_ms,
        table=table,
        affected_rows=affected_rows,
        **metadata
    )


def log_analysis_event(
    event: str,
    analysis_id: Optional[str] = None,
    speech_id: Optional[str] = None,
    **metadata
):
    """Log analysis-specific events."""
    analysis_logger.info(
        f"Analysis event: {event}",
        operation="analysis_event",
        event=event,
        analysis_id=analysis_id,
        speech_id=speech_id,
        **metadata
    )


def log_auth_event(
    event: str,
    user_id: Optional[str] = None,
    success: bool = True,
    **metadata
):
    """Log authentication events."""
    level = "info" if success else "warning"
    
    auth_logger.log(
        level,
        f"Auth event: {event}",
        operation="auth_event",
        event=event,
        auth_user_id=user_id,  # Use different key to avoid confusion with context user_id
        success=success,
        **metadata
    )


# Request ID middleware helper
def create_request_id_middleware():
    """Create middleware to set request ID for each request."""
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    from starlette.responses import Response
    
    class RequestIDMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            # Generate or extract request ID
            request_id = request.headers.get("x-request-id") or generate_request_id()
            set_request_id(request_id)
            
            # Process request
            start_time = datetime.utcnow()
            response = await call_next(request)
            duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Add request ID to response headers
            response.headers["x-request-id"] = request_id
            
            # Log API call
            log_api_call(
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                duration_ms=duration,
                query_params=dict(request.query_params) if request.query_params else None
            )
            
            return response
    
    return RequestIDMiddleware


# Configuration for structured logging
def configure_logging(log_level: str = "INFO", json_format: bool = True):
    """Configure logging for the application."""
    
    if json_format:
        # Use JSON formatter for structured logs
        formatter = logging.Formatter('%(message)s')
    else:
        # Use standard formatter for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)