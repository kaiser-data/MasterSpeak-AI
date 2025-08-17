# Code Conventions & Standards

## Overview
This document establishes coding conventions, naming standards, logging practices, error handling patterns, and feature flag usage for MasterSpeak-AI.

## Naming Conventions

### File & Directory Naming

#### Frontend (TypeScript/React)
```
kebab-case for files:     user-profile.tsx, analysis-detail.tsx
PascalCase for components: UserProfile.tsx, AnalysisDetail.tsx
camelCase for utilities:   apiClient.ts, authHelpers.ts
lowercase for pages:       page.tsx, layout.tsx, loading.tsx
```

#### Backend (Python)
```
snake_case for files:      analysis_service.py, user_repository.py
snake_case for modules:    analysis_routes.py, auth_middleware.py
snake_case for functions:  get_user_analyses, create_analysis
PascalCase for classes:    AnalysisService, UserRepository
```

### Variable & Function Naming

#### TypeScript Conventions
```typescript
// Constants: SCREAMING_SNAKE_CASE
const API_BASE_URL = 'https://api.example.com';
const MAX_FILE_SIZE = 10 * 1024 * 1024;

// Variables: camelCase
const analysisResult = await getAnalysis(speechId);
const isLoading = true;

// Functions: camelCase with descriptive verbs
function createAnalysis(data: AnalysisData): Promise<Analysis>
function validateSpeechContent(content: string): boolean
function formatAnalysisDate(date: Date): string

// Components: PascalCase
function AnalysisDetail({ analysisId }: Props)
function SpeechUploadForm({ onSubmit }: Props)

// Types/Interfaces: PascalCase
interface AnalysisResponse {
  id: string;
  clarity_score: number;
}

type SpeechSource = 'text' | 'audio' | 'video';
```

#### Python Conventions
```python
# Constants: SCREAMING_SNAKE_CASE
API_VERSION = "v1"
DEFAULT_PAGE_SIZE = 20
MAX_ANALYSIS_LENGTH = 10000

# Variables: snake_case
analysis_result = await get_analysis(speech_id)
is_authenticated = True

# Functions: snake_case with descriptive verbs
async def create_analysis(data: AnalysisCreate) -> Analysis:
def validate_speech_content(content: str) -> bool:
def format_analysis_response(analysis: Analysis) -> dict:

# Classes: PascalCase
class AnalysisService:
class SpeechRepository:
class AuthenticationMiddleware:

# Methods: snake_case
def get_user_analyses(self, user_id: UUID) -> List[Analysis]:
async def save_analysis(self, analysis_data: AnalysisData) -> Analysis:
```

### Database Naming
```sql
-- Tables: snake_case, plural
users, speeches, speech_analyses, share_tokens

-- Columns: snake_case
user_id, created_at, clarity_score, is_active

-- Indexes: descriptive with prefix
idx_speeches_user_id, idx_analyses_created_at, uq_share_tokens_token

-- Foreign Keys: descriptive
fk_speeches_user_id, fk_analyses_speech_id
```

## Code Organization Patterns

### Frontend Structure
```typescript
// Service Layer Pattern
// src/services/analyses.ts
export class AnalysisService {
  async getRecentAnalyses(limit = 5): Promise<Analysis[]> {
    // Implementation using API client
  }
  
  async createAnalysis(data: CreateAnalysisRequest): Promise<Analysis> {
    // Implementation with error handling
  }
}

// Hook Pattern for Data Fetching
// src/hooks/useAnalyses.ts
export function useAnalyses(userId: string) {
  return useQuery({
    queryKey: ['analyses', userId],
    queryFn: () => analysisService.getRecentAnalyses(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Component Composition Pattern
// src/components/analysis/AnalysisCard.tsx
interface AnalysisCardProps {
  analysis: Analysis;
  onSelect?: (analysis: Analysis) => void;
}

export function AnalysisCard({ analysis, onSelect }: AnalysisCardProps) {
  // Component implementation
}
```

### Backend Structure
```python
# Repository Pattern
# backend/repositories/analysis_repo.py
class AnalysisRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_user_speech(
        self, user_id: UUID, speech_id: UUID
    ) -> Optional[Analysis]:
        # Implementation
    
    async def create(self, analysis_data: AnalysisCreate) -> Analysis:
        # Implementation

# Service Layer Pattern
# backend/services/analysis_service.py
class AnalysisService:
    def __init__(self, repo: AnalysisRepository):
        self.repo = repo
    
    async def save_analysis(
        self, user_id: UUID, speech_id: UUID, **kwargs
    ) -> Analysis:
        # Idempotent save with business logic
```

## Logging Standards

### Structured Logging Format
All logs must use structured format with consistent fields:

```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "level": "INFO",
  "request_id": "req_123456",
  "user_id": "user_789",
  "service": "analysis_service",
  "operation": "create_analysis",
  "duration_ms": 1250,
  "status": "success",
  "metadata": {
    "speech_id": "speech_456",
    "analysis_type": "default"
  }
}
```

### Privacy & Security
**NEVER LOG:**
- Speech transcripts or content
- Audio data or files
- User passwords or tokens
- Personal identifiable information (PII)
- API keys or secrets

**SAFE TO LOG:**
- User IDs (UUIDs)
- Speech IDs (UUIDs)
- Analysis metrics (scores, counts)
- Request/response metadata
- Performance metrics
- Error codes and types

### Frontend Logging
```typescript
// src/lib/log.ts
interface LogEvent {
  level: 'debug' | 'info' | 'warn' | 'error';
  message: string;
  operation?: string;
  duration_ms?: number;
  metadata?: Record<string, unknown>;
}

export function logEvent(event: LogEvent) {
  const logData = {
    timestamp: new Date().toISOString(),
    request_id: getRequestId(),
    user_id: getCurrentUserId(),
    ...event,
  };
  
  // Send to logging service (exclude in development)
  if (process.env.NODE_ENV === 'production') {
    sendToLogService(logData);
  }
  
  console.log(JSON.stringify(logData));
}

// Usage Examples
logEvent({
  level: 'info',
  message: 'Analysis created successfully',
  operation: 'create_analysis',
  metadata: { speech_id: 'uuid', analysis_type: 'default' }
});

logEvent({
  level: 'error',
  message: 'Analysis creation failed',
  operation: 'create_analysis',
  metadata: { error_code: 'VALIDATION_ERROR', speech_id: 'uuid' }
});
```

### Backend Logging
```python
# backend/utils/logging.py
import logging
import json
from typing import Dict, Any, Optional
from uuid import UUID

class StructuredLogger:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
    
    def log_event(
        self,
        level: str,
        message: str,
        operation: Optional[str] = None,
        user_id: Optional[UUID] = None,
        request_id: Optional[str] = None,
        duration_ms: Optional[int] = None,
        **metadata
    ):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level.upper(),
            "service": self.service_name,
            "message": message,
            "operation": operation,
            "user_id": str(user_id) if user_id else None,
            "request_id": request_id,
            "duration_ms": duration_ms,
            "metadata": metadata
        }
        
        # Remove None values
        log_data = {k: v for k, v in log_data.items() if v is not None}
        
        getattr(self.logger, level.lower())(json.dumps(log_data))

# Usage Examples
logger = StructuredLogger("analysis_service")

logger.log_event(
    level="info",
    message="Analysis persisted successfully",
    operation="save_analysis",
    user_id=user_id,
    speech_id=str(speech_id),
    analysis_id=str(analysis.id)
)

logger.log_event(
    level="error",
    message="Analysis persist failed",
    operation="save_analysis",
    user_id=user_id,
    speech_id=str(speech_id),
    error="Database constraint violation",
    is_retryable=False
)
```

## Error Handling Patterns

### Frontend Error Handling
```typescript
// src/lib/errors.ts
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public code: string,
    public requestId?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// Error boundary for React components
export class ErrorBoundary extends Component<Props, State> {
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    logEvent({
      level: 'error',
      message: 'React error boundary caught error',
      operation: 'error_boundary',
      metadata: {
        error_message: error.message,
        component_stack: errorInfo.componentStack
      }
    });
  }
}

// Service error handling
async function createAnalysis(data: CreateAnalysisRequest): Promise<Analysis> {
  try {
    const response = await api.post('/analysis/text', data);
    return response.data;
  } catch (error) {
    if (error instanceof APIError) {
      logEvent({
        level: 'error',
        message: 'Analysis creation failed',
        operation: 'create_analysis',
        metadata: {
          status: error.status,
          error_code: error.code,
          request_id: error.requestId
        }
      });
    }
    throw error;
  }
}
```

### Backend Error Handling
```python
# backend/exceptions.py
class MasterSpeakException(Exception):
    """Base exception for MasterSpeak-AI"""
    def __init__(self, message: str, error_code: str = "INTERNAL_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class ValidationError(MasterSpeakException):
    def __init__(self, message: str, field: str = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field

class NotFoundError(MasterSpeakException):
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} not found: {identifier}"
        super().__init__(message, "NOT_FOUND")

# Global exception handler
@app.exception_handler(MasterSpeakException)
async def masterspeak_exception_handler(request: Request, exc: MasterSpeakException):
    logger.log_event(
        level="error",
        message=exc.message,
        operation=request.url.path,
        error_code=exc.error_code,
        request_id=getattr(request.state, "request_id", None)
    )
    
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "request_id": getattr(request.state, "request_id", None)
        }
    )
```

## Feature Flags

### Supported Feature Flags
```typescript
// Feature flag definitions
export const FEATURE_FLAGS = {
  TRANSCRIPTION_UI: 'TRANSCRIPTION_UI',
  EXPORT_ENABLED: 'EXPORT_ENABLED', 
  PROGRESS_UI: 'PROGRESS_UI',
  SHARE_LINKS: 'SHARE_LINKS',
  ADVANCED_ANALYTICS: 'ADVANCED_ANALYTICS'
} as const;

// Environment-based feature flags
export function isFeatureEnabled(flag: keyof typeof FEATURE_FLAGS): boolean {
  const envVar = `NEXT_PUBLIC_${flag}`;
  return process.env[envVar] === '1' || process.env[envVar] === 'true';
}
```

### Frontend Feature Flag Usage
```typescript
// Component with feature flag
export function AnalysisDetailPage({ analysisId }: Props) {
  const showTranscription = isFeatureEnabled('TRANSCRIPTION_UI');
  const allowExport = isFeatureEnabled('EXPORT_ENABLED');
  
  return (
    <div>
      <AnalysisMetrics analysisId={analysisId} />
      
      {showTranscription && (
        <TranscriptionSection analysisId={analysisId} />
      )}
      
      {allowExport && (
        <ExportButtons analysisId={analysisId} />
      )}
    </div>
  );
}

// Service with feature flag
export class AnalysisService {
  async exportToPDF(analysisId: string): Promise<Blob> {
    if (!isFeatureEnabled('EXPORT_ENABLED')) {
      throw new Error('Export feature is not enabled');
    }
    
    // Implementation
  }
}
```

### Backend Feature Flag Usage
```python
# backend/config.py
class Settings(BaseSettings):
    # Feature flags
    transcription_ui: bool = Field(default=False, env="TRANSCRIPTION_UI")
    export_enabled: bool = Field(default=False, env="EXPORT_ENABLED")
    progress_ui: bool = Field(default=False, env="PROGRESS_UI")
    share_links: bool = Field(default=False, env="SHARE_LINKS")

# Usage in services
class ExportService:
    def __init__(self, settings: Settings):
        self.settings = settings
    
    async def export_analysis(self, analysis_id: UUID) -> bytes:
        if not self.settings.export_enabled:
            raise FeatureDisabledError("Export functionality is disabled")
        
        # Implementation
```

## Testing Conventions

### Test File Organization
```
Frontend:
- test/unit/components/     # Component unit tests
- test/unit/services/       # Service layer tests
- test/unit/hooks/          # Custom hook tests
- test/integration/         # Integration tests
- test/e2e/                 # End-to-end tests

Backend:
- test/unit/services/       # Service layer tests
- test/unit/repositories/   # Repository tests
- test/unit/routes/         # Route handler tests
- test/integration/         # Database integration tests
- test/e2e/                 # End-to-end API tests
```

### Test Naming
```typescript
// Frontend test naming
describe('AnalysisService', () => {
  describe('getRecentAnalyses', () => {
    it('should return recent analyses for user', async () => {
      // Test implementation
    });
    
    it('should handle API errors gracefully', async () => {
      // Error case test
    });
  });
});

// Backend test naming
class TestAnalysisService:
    async def test_save_analysis_creates_new_record(self):
        # Test implementation
        pass
    
    async def test_save_analysis_returns_existing_record_when_duplicate(self):
        # Idempotency test
        pass
```

## Performance Guidelines

### Frontend Performance
- Use React.memo for expensive components
- Implement proper loading states with skeletons
- Use pagination for large data sets (limit: 20 items)
- Optimize bundle size with dynamic imports
- Cache API responses with React Query (5-minute stale time)

### Backend Performance
- Use database indexes on query columns
- Implement proper pagination (default: 20, max: 100)
- Use connection pooling for database connections
- Add caching for expensive operations
- Set appropriate request timeouts (30 seconds)

### Database Performance
```sql
-- Required indexes
CREATE INDEX idx_speeches_user_id ON speeches(user_id);
CREATE INDEX idx_speeches_created_at ON speeches(created_at DESC);
CREATE INDEX idx_analyses_speech_id ON speech_analyses(speech_id);
CREATE INDEX idx_analyses_user_created ON speech_analyses(user_id, created_at DESC);
```

## Security Guidelines

### Input Validation
- Validate all inputs at API boundaries
- Use Pydantic for backend validation
- Use Zod for frontend validation
- Sanitize user inputs before database storage
- Implement file type and size validation

### Authentication & Authorization
- Use JWT tokens with proper expiration
- Implement RBAC for resource access
- Validate user ownership of resources
- Use HTTPS for all API communications
- Implement proper CORS policies

### Data Protection
- Never log sensitive data (transcripts, audio, PII)
- Use UUID for all entity identifiers
- Implement proper error messages (no data leaks)
- Use parameterized queries to prevent SQL injection
- Validate file uploads with strict type checking