# backend/logging.py

import logging
import json
import uuid
from typing import Any, Dict, Optional
from datetime import datetime
from contextvars import ContextVar
from backend.config import settings

# Context variable to store request ID across async operations
request_id_context: ContextVar[str] = ContextVar('request_id', default='')

class StructuredFormatter(logging.Formatter):
    """
    Custom logging formatter that outputs structured JSON logs
    with request_id and removes secrets from log messages
    """
    
    SENSITIVE_KEYS = {
        'password', 'secret', 'key', 'token', 'authorization', 'auth',
        'api_key', 'openai_api_key', 'secret_key', 'reset_secret', 
        'verification_secret', 'redis_url', 'database_url'
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # Get request ID from context
        request_id = request_id_context.get('')
        
        # Create structured log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'request_id': request_id if request_id else None,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                              'filename', 'module', 'lineno', 'funcName', 'created', 
                              'msecs', 'relativeCreated', 'thread', 'threadName', 
                              'processName', 'process', 'exc_info', 'exc_text', 'stack_info']:
                    # Filter sensitive information
                    if isinstance(key, str) and any(sensitive in key.lower() for sensitive in self.SENSITIVE_KEYS):
                        log_entry[key] = '[REDACTED]'
                    else:
                        log_entry[key] = self._sanitize_value(value)
        
        return json.dumps(log_entry, default=str)
    
    def _sanitize_value(self, value: Any) -> Any:
        """Remove sensitive information from log values"""
        if isinstance(value, str):
            # Check if the string looks like a sensitive value
            value_lower = value.lower()
            if any(sensitive in value_lower for sensitive in self.SENSITIVE_KEYS):
                return '[REDACTED]'
            
            # Hide long tokens/keys (likely sensitive)
            if len(value) > 50 and not ' ' in value:
                return f"[REDACTED:{len(value)} chars]"
                
        elif isinstance(value, dict):
            return {k: self._sanitize_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._sanitize_value(item) for item in value]
        
        return value

def setup_logging():
    """
    Configure application logging with structured format and appropriate levels
    """
    # Determine log level based on environment
    if settings.ENV == "development":
        log_level = logging.DEBUG
    elif settings.ENV == "testing":
        log_level = logging.WARNING
    else:  # production
        log_level = logging.WARNING
    
    # Override with explicit LOG_LEVEL if set
    if hasattr(settings, 'LOG_LEVEL') and settings.LOG_LEVEL:
        log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.WARNING)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create console handler with structured formatter
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Use structured formatter for production, simple for development
    if settings.ENV == "production":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s',
            defaults={'request_id': lambda: request_id_context.get('')}
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Set specific logger levels
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING if settings.ENV == "production" else logging.INFO)
    logging.getLogger('fastapi').setLevel(logging.INFO)
    
    return root_logger

def get_request_id() -> str:
    """Get the current request ID from context"""
    return request_id_context.get('')

def set_request_id(request_id: str) -> None:
    """Set the request ID for the current context"""
    request_id_context.set(request_id)

def generate_request_id() -> str:
    """Generate a new request ID"""
    return str(uuid.uuid4())

def log_rate_limit_event(
    client_ip: str, 
    endpoint: str, 
    limit: str, 
    retry_after: int,
    user_agent: Optional[str] = None
) -> None:
    """
    Log rate limiting events with structured data for monitoring
    """
    logger = logging.getLogger('masterspeak.rate_limit')
    
    log_data = {
        'event_type': 'rate_limit_exceeded',
        'client_ip': client_ip,
        'endpoint': endpoint,
        'limit': limit,
        'retry_after': retry_after,
        'user_agent': user_agent,
        'severity': 'warning'
    }
    
    logger.warning(
        f"Rate limit exceeded for {client_ip} on {endpoint}",
        extra=log_data
    )

def log_security_event(
    event_type: str,
    client_ip: str,
    details: Dict[str, Any],
    severity: str = 'warning'
) -> None:
    """
    Log security-related events for monitoring and alerting
    """
    logger = logging.getLogger('masterspeak.security')
    
    log_data = {
        'event_type': f'security_{event_type}',
        'client_ip': client_ip,
        'severity': severity,
        **details
    }
    
    getattr(logger, severity.lower())(
        f"Security event: {event_type} from {client_ip}",
        extra=log_data
    )

def log_performance_event(
    endpoint: str,
    response_time_ms: float,
    status_code: int,
    method: str = 'GET'
) -> None:
    """
    Log performance metrics for monitoring slow endpoints
    """
    logger = logging.getLogger('masterspeak.performance')
    
    log_data = {
        'event_type': 'performance_metric',
        'endpoint': endpoint,
        'method': method,
        'response_time_ms': response_time_ms,
        'status_code': status_code,
        'severity': 'warning' if response_time_ms > 1000 else 'info'
    }
    
    if response_time_ms > 1000:  # Slow request threshold
        logger.warning(
            f"Slow request: {method} {endpoint} took {response_time_ms:.2f}ms",
            extra=log_data
        )
    else:
        logger.debug(
            f"Request: {method} {endpoint} - {response_time_ms:.2f}ms",
            extra=log_data
        )

# Initialize logging when module is imported
if not logging.getLogger().handlers:  # Avoid duplicate setup
    setup_logging()