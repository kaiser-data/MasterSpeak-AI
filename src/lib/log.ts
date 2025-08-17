import { env, isDevelopment, isProduction } from './env';

// Log levels in order of severity
export const LOG_LEVELS = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
} as const;

export type LogLevel = keyof typeof LOG_LEVELS;

// Structured log event interface
export interface LogEvent {
  level: LogLevel;
  message: string;
  operation?: string;
  duration_ms?: number;
  user_id?: string;
  request_id?: string;
  metadata?: Record<string, unknown>;
}

// Internal log data structure
interface LogData extends LogEvent {
  timestamp: string;
  service: string;
  environment: string;
}

// Request ID management
let currentRequestId: string | null = null;

export function setRequestId(id: string): void {
  currentRequestId = id;
}

export function getRequestId(): string | null {
  return currentRequestId;
}

export function generateRequestId(): string {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// User ID management (from auth context)
let currentUserId: string | null = null;

export function setUserId(id: string | null): void {
  currentUserId = id;
}

export function getCurrentUserId(): string | null {
  return currentUserId;
}

// PII Detection and Redaction
const PII_PATTERNS = [
  /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g, // Email
  /\b\d{3}-\d{2}-\d{4}\b/g, // SSN
  /\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b/g, // Credit card
  /\b\d{3}-\d{3}-\d{4}\b/g, // Phone number
];

function redactPII(text: string): string {
  let redacted = text;
  PII_PATTERNS.forEach(pattern => {
    redacted = redacted.replace(pattern, '[REDACTED]');
  });
  return redacted;
}

// Safe metadata processing - removes or redacts sensitive data
function sanitizeMetadata(metadata: Record<string, unknown>): Record<string, unknown> {
  const sanitized: Record<string, unknown> = {};
  
  for (const [key, value] of Object.entries(metadata)) {
    const lowerKey = key.toLowerCase();
    
    // Skip sensitive fields entirely
    if (
      lowerKey.includes('password') ||
      lowerKey.includes('token') ||
      lowerKey.includes('secret') ||
      lowerKey.includes('key') ||
      lowerKey.includes('transcript') ||
      lowerKey.includes('content') ||
      lowerKey.includes('audio') ||
      lowerKey.includes('speech_content')
    ) {
      sanitized[key] = '[REDACTED]';
      continue;
    }
    
    // Redact PII from string values
    if (typeof value === 'string') {
      sanitized[key] = redactPII(value);
    } else if (value !== null && typeof value === 'object') {
      // Recursively sanitize nested objects
      sanitized[key] = sanitizeMetadata(value as Record<string, unknown>);
    } else {
      sanitized[key] = value;
    }
  }
  
  return sanitized;
}

// Check if log level should be processed
function shouldLog(level: LogLevel): boolean {
  const currentLevelValue = LOG_LEVELS[env.NEXT_PUBLIC_LOG_LEVEL];
  const eventLevelValue = LOG_LEVELS[level];
  return eventLevelValue >= currentLevelValue;
}

// Core logging function
export function logEvent(event: LogEvent): void {
  if (!shouldLog(event.level)) {
    return;
  }

  const logData: LogData = {
    timestamp: new Date().toISOString(),
    service: 'frontend',
    environment: env.NODE_ENV,
    request_id: event.request_id || currentRequestId || undefined,
    user_id: event.user_id || currentUserId || undefined,
    ...event,
    message: redactPII(event.message),
    metadata: event.metadata ? sanitizeMetadata(event.metadata) : undefined,
  };

  // Remove undefined values for cleaner logs
  const cleanLogData = Object.fromEntries(
    Object.entries(logData).filter(([_, value]) => value !== undefined)
  );

  // Console output with appropriate level
  const logMethod = event.level === 'debug' ? 'debug' :
                   event.level === 'info' ? 'info' :
                   event.level === 'warn' ? 'warn' : 'error';

  if (isDevelopment) {
    // Development: Pretty-printed logs
    console[logMethod](`[${event.level.toUpperCase()}] ${event.message}`, {
      operation: event.operation,
      duration_ms: event.duration_ms,
      metadata: event.metadata,
    });
  } else {
    // Production: Structured JSON logs
    console[logMethod](JSON.stringify(cleanLogData));
  }

  // Send to external logging service in production
  if (isProduction && event.level !== 'debug') {
    sendToLogService(cleanLogData as LogData);
  }
}

// Convenience logging methods
export const logger = {
  debug: (message: string, metadata?: Record<string, unknown>) => 
    logEvent({ level: 'debug', message, metadata }),
  
  info: (message: string, operation?: string, metadata?: Record<string, unknown>) => 
    logEvent({ level: 'info', message, operation, metadata }),
  
  warn: (message: string, operation?: string, metadata?: Record<string, unknown>) => 
    logEvent({ level: 'warn', message, operation, metadata }),
  
  error: (message: string, operation?: string, metadata?: Record<string, unknown>) => 
    logEvent({ level: 'error', message, operation, metadata }),
};

// Performance logging helper
export function logPerformance<T>(
  operation: string,
  fn: () => Promise<T>,
  metadata?: Record<string, unknown>
): Promise<T> {
  const start = Date.now();
  
  return fn()
    .then(result => {
      const duration = Date.now() - start;
      logEvent({
        level: 'info',
        message: `${operation} completed successfully`,
        operation,
        duration_ms: duration,
        metadata,
      });
      return result;
    })
    .catch(error => {
      const duration = Date.now() - start;
      logEvent({
        level: 'error',
        message: `${operation} failed: ${error.message}`,
        operation,
        duration_ms: duration,
        metadata: {
          ...metadata,
          error_type: error.constructor.name,
          error_message: redactPII(error.message),
        },
      });
      throw error;
    });
}

// API call logging wrapper
export function logAPICall<T>(
  method: string,
  url: string,
  fn: () => Promise<T>,
  requestData?: unknown
): Promise<T> {
  const operation = `api_call_${method.toLowerCase()}`;
  const start = Date.now();
  
  // Log request start
  logEvent({
    level: 'debug',
    message: `API call started: ${method} ${url}`,
    operation,
    metadata: {
      method,
      url: redactPII(url),
      has_request_data: requestData !== undefined,
    },
  });
  
  return fn()
    .then(result => {
      const duration = Date.now() - start;
      logEvent({
        level: 'info',
        message: `API call successful: ${method} ${url}`,
        operation,
        duration_ms: duration,
        metadata: {
          method,
          url: redactPII(url),
          status: 'success',
        },
      });
      return result;
    })
    .catch(error => {
      const duration = Date.now() - start;
      logEvent({
        level: 'error',
        message: `API call failed: ${method} ${url}`,
        operation,
        duration_ms: duration,
        metadata: {
          method,
          url: redactPII(url),
          status: 'error',
          error_type: error.constructor.name,
          error_message: redactPII(error.message),
          status_code: error.status || undefined,
        },
      });
      throw error;
    });
}

// External logging service integration
async function sendToLogService(logData: LogData): Promise<void> {
  // Only send error and warn logs to external service to reduce noise
  if (logData.level !== 'error' && logData.level !== 'warn') {
    return;
  }

  try {
    // Example: Send to Sentry, LogRocket, or custom logging endpoint
    if (env.NEXT_PUBLIC_SENTRY_DSN) {
      // Sentry integration would go here
      // Sentry.addBreadcrumb({
      //   message: logData.message,
      //   level: logData.level,
      //   data: logData.metadata,
      // });
    }
    
    // Example: Send to custom logging endpoint
    // await fetch('/api/logs', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(logData),
    // });
  } catch (error) {
    // Fail silently for logging errors to avoid infinite loops
    console.error('Failed to send log to external service:', error);
  }
}

// Error boundary logging helper
export function logReactError(error: Error, errorInfo: { componentStack: string }): void {
  logEvent({
    level: 'error',
    message: 'React error boundary caught error',
    operation: 'react_error_boundary',
    metadata: {
      error_type: error.constructor.name,
      error_message: redactPII(error.message),
      component_stack: errorInfo.componentStack,
      stack_trace: error.stack ? redactPII(error.stack) : undefined,
    },
  });
}

// User action logging
export function logUserAction(action: string, metadata?: Record<string, unknown>): void {
  logEvent({
    level: 'info',
    message: `User action: ${action}`,
    operation: 'user_action',
    metadata: {
      action,
      ...metadata,
    },
  });
}

// Feature flag usage logging
export function logFeatureUsage(feature: string, enabled: boolean): void {
  logEvent({
    level: 'info',
    message: `Feature flag accessed: ${feature}`,
    operation: 'feature_flag',
    metadata: {
      feature,
      enabled,
    },
  });
}