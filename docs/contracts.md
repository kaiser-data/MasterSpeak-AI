# API Contracts & Integration Specifications

## Overview
This document defines the exact API contracts, data schemas, and integration patterns for MasterSpeak-AI sprint goals. All APIs follow RESTful conventions under the `/api/v1/` namespace with comprehensive request/response schemas.

## Sprint Goals & API Coverage
1. **Analysis Persistence (Agent A)**: POST /api/v1/analysis/complete, GET /api/v1/analyses
2. **History & Navigation (Agent C)**: GET /api/v1/analyses/{id}, pagination support
3. **Transcript UI (Agent B)**: POST /api/v1/transcription/transcribe (flag: TRANSCRIPTION_UI)
4. **Export & Share (Agent D)**: GET /api/v1/analyses/{id}/export, POST /api/v1/share/{id}, GET /share/{token} (flag: EXPORT_ENABLED)
5. **Progress & Metrics (Agent E)**: GET /api/v1/analyses/metrics (flag: PROGRESS_UI)

## Current Repository Structure

### Frontend (Next.js 14 App Router)
```
src/
├── app/                    # App Router pages & layouts
│   ├── auth/              # Authentication flows
│   ├── dashboard/         # Main application interface
│   │   ├── analyses/      # Analysis list & detail pages
│   │   └── page.tsx       # Dashboard home
│   └── layout.tsx         # Root layout
├── components/            # Reusable UI components
│   └── ui/               # Core UI components
├── lib/                   # Core utilities
│   └── api.ts            # API client configuration
├── services/              # Business logic services
│   └── analyses.ts       # Analysis service layer
└── types/                 # TypeScript type definitions
```

### Backend (FastAPI + SQLModel)
```
backend/
├── main.py                 # FastAPI application entry
├── api/v1/                # API route definitions
│   ├── endpoints/         # Current route handlers
│   └── routes/            # New modular route structure
│       ├── analyses.py    # Analysis CRUD endpoints (Agent A,C)
│       ├── transcription.py # Transcription service (Agent B)
│       ├── export.py      # Export functionality (Agent D)
│       ├── share.py       # Share token management (Agent D)
│       └── metrics.py     # Progress metrics (Agent E)
├── models/                # SQLModel domain entities
│   ├── speech.py          # Speech entity
│   ├── analysis.py        # Analysis entity (unique constraint)
│   ├── share_token.py     # Share token entity (Agent D)
│   └── progress_goal.py   # Progress goals (Agent E)
├── repositories/          # Data access layer
│   ├── speech_repo.py     # Speech repository
│   ├── analysis_repo.py   # Analysis repository (idempotent)
│   └── share_token_repo.py # Share token repository
├── services/              # Business logic layer
│   ├── analysis_service.py  # Analysis orchestration (Agent A)
│   ├── transcription_service.py # Transcription logic (Agent B)
│   ├── export_service.py    # PDF export (Agent D)
│   └── progress_service.py  # Progress calculations (Agent E)
└── database/              # Database connection & models
    ├── database.py        # Session management
    └── models.py          # Legacy model definitions
```

## Core Domain Entities

### User Entity
```typescript
// Frontend (TypeScript/Zod)
interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}
```

```python
# Backend (Pydantic/SQLModel)
class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    full_name: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Speech Entity
```typescript
// Frontend
interface Speech {
  id: string;
  user_id: string;
  title: string;
  content: string;
  source_type: 'text' | 'audio';
  transcription?: string;
  created_at: string;
}
```

```python
# Backend
class Speech(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    title: str
    content: str
    source_type: SourceType
    transcription: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Analysis Entity (Agent A - Idempotent Constraint)
```typescript
// Frontend
interface Analysis {
  id: string;
  speech_id: string;
  user_id: string;
  transcript?: string;        // Optional transcript content
  metrics?: {                 // Optional structured metrics
    word_count: number;
    clarity_score: number;
    structure_score: number;
    filler_word_count: number;
  };
  summary?: string;           // Optional AI-generated summary
  feedback: string;           // Always present
  created_at: string;
  updated_at: string;
}
```

```python
# Backend - Idempotent Analysis with unique constraint
class Analysis(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    speech_id: UUID = Field(foreign_key="speech.id")
    user_id: UUID = Field(foreign_key="user.id")
    transcript: Optional[str] = None    # Never logged
    metrics: Optional[dict] = None      # JSON field for structured data
    summary: Optional[str] = None       # AI-generated summary
    feedback: str                       # Always required
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint("user_id", "speech_id"),)  # Idempotency
```

### Share Token Entity (Agent D)
```typescript
// Frontend
interface ShareToken {
  id: string;
  analysis_id: string;
  token: string;
  expires_at: string;
  created_at: string;
}
```

```python
# Backend
class ShareToken(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    analysis_id: UUID = Field(foreign_key="analysis.id")
    hashed_token: str = Field(index=True)  # Never store plain token
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## API Routes & Contracts

## Sprint Goal API Endpoints

### Agent A: Analysis Persistence

#### POST /api/v1/analysis/complete
**Purpose**: Idempotent analysis completion with unique(user_id, speech_id)

**Request:**
```json
{
  "user_id": "uuid",
  "speech_id": "uuid", 
  "transcript": "optional_transcript_content",
  "metrics": {
    "word_count": 150,
    "clarity_score": 8.5,
    "structure_score": 7.2,
    "filler_word_count": 3
  },
  "summary": "optional_ai_generated_summary",
  "feedback": "required_feedback_content"
}
```

**Response (201 - Created):**
```json
{
  "analysis_id": "uuid",
  "speech_id": "uuid",
  "user_id": "uuid",
  "created_at": "2024-01-01T12:00:00Z",
  "is_duplicate": false,
  "summary": "optional_summary",
  "metrics": {
    "word_count": 150,
    "clarity_score": 8.5,
    "structure_score": 7.2,
    "filler_word_count": 3
  }
}
```

**Response (200 - Existing):**
```json
{
  "analysis_id": "uuid",
  "speech_id": "uuid", 
  "user_id": "uuid",
  "created_at": "2024-01-01T12:00:00Z",
  "is_duplicate": true,
  "summary": "existing_summary",
  "metrics": {...}
}
```

**Error Codes:**
- 400: Invalid request data
- 403: Speech not owned by user
- 404: Speech not found
- 422: Validation error

#### GET /api/v1/analyses
**Purpose**: Paginated list of user's analyses

**Query Parameters:**
```
limit: 20 (default, max 100)
page: 1 (default)
user_id: uuid (auto from auth context)
```

**Response (200):**
```json
{
  "items": [
    {
      "analysis_id": "uuid",
      "speech_id": "uuid",
      "speech_title": "Speech Title",
      "summary": "optional_summary",
      "metrics": {
        "word_count": 150,
        "clarity_score": 8.5,
        "structure_score": 7.2,
        "filler_word_count": 3
      },
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

### Agent C: History & Navigation

#### GET /api/v1/analyses/{id}
**Purpose**: Get single analysis details (owner auth required)

**Response (200):**
```json
{
  "analysis_id": "uuid",
  "speech_id": "uuid",
  "user_id": "uuid",
  "speech_title": "Speech Title",
  "speech_content": "redacted_for_privacy",
  "transcript": "optional_transcript_if_flag_enabled",
  "summary": "optional_summary",
  "metrics": {
    "word_count": 150,
    "clarity_score": 8.5,
    "structure_score": 7.2,
    "filler_word_count": 3
  },
  "feedback": "detailed_feedback_content",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Error Codes:**
- 403: Not analysis owner
- 404: Analysis not found

### Agent B: Transcription UI (Flag: TRANSCRIPTION_UI=1)

#### POST /api/v1/transcription/transcribe
**Purpose**: Transcribe audio file to text

**Request (Multipart Form):**
```
file: [audio file - mp3, wav, m4a]
language: "en" (optional, default)
model: "whisper-1" (optional, default)
```

**Response (200):**
```json
{
  "transcript": "transcribed_text_content",
  "language": "en",
  "duration_seconds": 125.5,
  "word_count": 187,
  "confidence_score": 0.95,
  "processing_time_ms": 2500
}
```

**Error Codes:**
- 400: Invalid audio file
- 413: File too large (>10MB)
- 429: Rate limit exceeded
- 503: Transcription service unavailable

### Agent D: Export & Share (Flag: EXPORT_ENABLED=1)

#### GET /api/v1/analyses/{id}/export
**Purpose**: Export analysis as PDF (owner auth required)

**Query Parameters:**
```
format: "pdf" (default)
include_transcript: true/false (default: false unless ALLOW_TRANSCRIPT_EXPORT=1)
```

**Response (200):**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="analysis-{id}.pdf"
[PDF binary data]
```

**Headers:**
```
X-Export-Type: pdf
X-Analysis-ID: uuid
X-Generated-At: 2024-01-01T12:00:00Z
```

#### POST /api/v1/share/{id}
**Purpose**: Create shareable link for analysis

**Request:**
```json
{
  "expires_in_hours": 72,
  "include_transcript": false,
  "password_protected": false
}
```

**Response (201):**
```json
{
  "share_url": "https://app.masterspeak.ai/share/abc123def456",
  "token": "abc123def456",
  "expires_at": "2024-01-04T12:00:00Z",
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### GET /share/{token}
**Purpose**: Access shared analysis (public, no auth)

**Response (200):**
```json
{
  "analysis_id": "uuid",
  "speech_title": "Speech Title",
  "summary": "redacted_summary",
  "metrics": {
    "word_count": 150,
    "clarity_score": 8.5,
    "structure_score": 7.2,
    "filler_word_count": 3
  },
  "feedback": "public_feedback_content",
  "transcript": "only_if_ALLOW_TRANSCRIPT_SHARE=1",
  "created_at": "2024-01-01T12:00:00Z",
  "shared_at": "2024-01-01T12:00:00Z",
  "expires_at": "2024-01-04T12:00:00Z"
}
```

**Error Codes:**
- 404: Token not found or expired
- 410: Share link expired

### Agent E: Progress & Metrics (Flag: PROGRESS_UI=1)

#### GET /api/v1/analyses/metrics
**Purpose**: Aggregated progress metrics for user

**Query Parameters:**
```
from: "2024-01-01T00:00:00Z" (optional)
to: "2024-01-31T23:59:59Z" (optional)
granularity: "day|week|month" (default: week)
```

**Response (200):**
```json
{
  "user_id": "uuid",
  "date_range": {
    "from": "2024-01-01T00:00:00Z",
    "to": "2024-01-31T23:59:59Z"
  },
  "totals": {
    "analyses_count": 45,
    "total_words": 12750,
    "avg_clarity_score": 8.2,
    "avg_structure_score": 7.8,
    "improvement_trend": 0.15
  },
  "time_series": [
    {
      "date": "2024-01-01",
      "analyses_count": 3,
      "avg_clarity_score": 7.5,
      "avg_structure_score": 7.2,
      "total_words": 450
    }
  ],
  "goals": [
    {
      "goal_id": "uuid",
      "type": "clarity_improvement",
      "target_value": 8.5,
      "current_value": 8.2,
      "progress_percent": 85,
      "deadline": "2024-02-01T00:00:00Z"
    }
  ]
}
```

## Error Response Format

All API errors follow a consistent structure:

```json
{
  "detail": "Human readable error message",
  "error_code": "VALIDATION_ERROR|NOT_FOUND|FORBIDDEN|RATE_LIMITED",
  "request_id": "req_uuid",
  "timestamp": "2024-01-01T12:00:00Z",
  "field_errors": {
    "field_name": ["Specific field error message"]
  }
}
```

## Feature Flag Enforcement

### TRANSCRIPTION_UI=1
- Enables: POST /api/v1/transcription/transcribe
- UI: Shows transcription upload in analysis detail
- Backend: Activates Whisper API integration

### EXPORT_ENABLED=1  
- Enables: GET /api/v1/analyses/{id}/export, POST /api/v1/share/{id}
- UI: Shows Export PDF and Share buttons
- Backend: Activates PDF generation and share token creation

### PROGRESS_UI=1
- Enables: GET /api/v1/analyses/metrics, progress goal endpoints
- UI: Shows /dashboard/progress page
- Backend: Activates metrics aggregation and goal tracking

## Dependency Graph & Merge Order

```
A (Analysis Persistence) → C (History/Nav) → B (Transcription UI) → D (Export/Share) → E (Progress)
```

### Agent A: Analysis Persistence (Priority 1)
**Dependencies**: None (foundation)
**Provides**: Analysis CRUD operations, idempotent save
**Critical Path**: Required by all other agents

**Deliverables:**
- `backend/models/analysis.py` - Analysis entity with unique(user_id, speech_id)
- `backend/repositories/analysis_repo.py` - Idempotent data access
- `backend/services/analysis_service.py` - Business logic orchestration
- `backend/api/v1/routes/analyses.py` - REST endpoints
- Database migration for Analysis table

**Handoff Contract to C:**
```json
POST /api/v1/analysis/complete → {analysis_id, is_duplicate}
GET /api/v1/analyses → {items[], total, page, page_size}
```

### Agent C: History & Navigation (Priority 2)
**Dependencies**: Agent A (analysis persistence)
**Provides**: Analysis listing, detail views, navigation
**Blocks**: Agents B, D, E (need navigation framework)

**Deliverables:**
- `src/app/dashboard/analyses/page.tsx` - Paginated analysis list
- `src/app/dashboard/analyses/[id]/page.tsx` - Analysis detail view  
- `src/services/analyses.ts` - Frontend analysis service
- Navigation updates in dashboard

**Handoff Contract to B:**
```json
GET /api/v1/analyses/{id} → {analysis with transcript field}
Analysis detail page framework for transcript UI injection
```

### Agent B: Transcription UI (Priority 3)
**Dependencies**: Agent C (navigation framework)
**Provides**: Audio transcription, transcript display
**Feature Flag**: TRANSCRIPTION_UI=1

**Deliverables:**
- `backend/api/v1/routes/transcription.py` - Transcription endpoint
- `backend/services/transcription_service.py` - Whisper integration
- `src/components/ui/TranscriptionUpload.tsx` - File upload UI
- Analysis detail page transcript section

**Handoff Contract to D:**
```json
POST /api/v1/transcription/transcribe → {transcript, metadata}
Enhanced analysis detail page for export/share integration
```

### Agent D: Export & Share (Priority 4)
**Dependencies**: Agent B (enhanced detail page)
**Provides**: PDF export, shareable links
**Feature Flag**: EXPORT_ENABLED=1

**Deliverables:**
- `backend/models/share_token.py` - Share token entity
- `backend/services/export_service.py` - PDF generation
- `backend/api/v1/routes/export.py` + `share.py` - Export/share endpoints
- Export/share UI components in analysis detail

**Handoff Contract to E:**
```json
GET /api/v1/analyses/{id}/export → PDF export
POST /api/v1/share/{id} → {share_url, expires_at}
Analysis data structure for progress calculations
```

### Agent E: Progress & Metrics (Priority 5)
**Dependencies**: Agent D (complete analysis data)
**Provides**: Progress dashboard, metrics aggregation
**Feature Flag**: PROGRESS_UI=1

**Deliverables:**
- `backend/api/v1/routes/metrics.py` - Metrics endpoints
- `backend/services/progress_service.py` - Progress calculations
- `src/app/dashboard/progress/page.tsx` - Progress dashboard
- `src/selectors/progress.ts` - Data transformation

**Final Integration:**
```json
GET /api/v1/analyses/metrics → {totals, time_series, goals}
Complete progress tracking with historical analysis data
```

## Daily Integration Schedule

### Week 1: Foundation (Agent A)
- **Day 1-2**: Analysis models, repositories, database migration
- **Day 3**: Analysis service with idempotency logic  
- **Day 4**: REST API endpoints with error handling
- **Day 5**: Integration testing, handoff to Agent C

### Week 2: Navigation (Agent C)  
- **Day 1-2**: Analysis list page with pagination
- **Day 3**: Analysis detail page framework
- **Day 4**: Frontend service integration, dashboard links
- **Day 5**: E2E testing, handoff to Agent B

### Week 3: Transcription (Agent B)
- **Day 1-2**: Transcription service and endpoints
- **Day 3**: UI components with file upload
- **Day 4**: Detail page transcript integration
- **Day 5**: Feature flag testing, handoff to Agent D

### Week 4: Export/Share (Agent D)
- **Day 1-2**: Share token model, PDF service
- **Day 3**: Export/share endpoints
- **Day 4**: UI integration in detail page
- **Day 5**: Security testing, handoff to Agent E

### Week 5: Progress (Agent E)
- **Day 1-2**: Metrics service and endpoints
- **Day 3**: Progress dashboard UI
- **Day 4**: Chart integration, goal tracking
- **Day 5**: Final integration testing

## Risk Management & Rollback

### High-Risk Integration Points
1. **A→C Handoff**: Analysis API contract changes
   - **Mitigation**: Strict API versioning, backward compatibility
   - **Rollback**: Feature flag disable, revert to existing analysis flow

2. **Database Schema Changes**: Analysis table creation
   - **Mitigation**: Additive-only migrations, rollback scripts
   - **Rollback**: Drop new tables, restore previous schema

3. **Feature Flag Dependencies**: UI components dependent on backend flags
   - **Mitigation**: Backend flags control API availability
   - **Rollback**: Set all flags to 0, disable new features

### Per-Agent Rollback Plans
- **Agent A**: Drop analysis table, revert to existing analysis flow
- **Agent C**: Remove new pages, restore existing dashboard
- **Agent B**: Disable TRANSCRIPTION_UI flag, hide transcription components
- **Agent D**: Disable EXPORT_ENABLED flag, remove export/share features
- **Agent E**: Disable PROGRESS_UI flag, hide progress dashboard

### Authentication Routes

#### POST /api/v1/auth/register
**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST /api/v1/auth/jwt/login
**Request (Form Data):**
```
username: user@example.com
password: secure_password
```

**Response (200):**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

### Analysis Routes

#### POST /api/v1/analysis/text
**Request:**
```json
{
  "text": "Speech content here...",
  "prompt": "default",
  "title": "My Speech Analysis"
}
```

**Response (200):**
```json
{
  "success": true,
  "speech_id": "uuid",
  "analysis": {
    "clarity_score": 8.5,
    "structure_score": 7.2,
    "filler_word_count": 5,
    "feedback": "Your speech demonstrates..."
  }
}
```

#### POST /api/v1/analysis/upload
**Request (Multipart Form):**
```
file: [audio/text file]
prompt_type: "default"
title: "Analysis Title"
```

**Response (200):**
```json
{
  "success": true,
  "speech_id": "uuid",
  "transcription": "Transcribed text...",
  "source_type": "audio",
  "analysis": {
    "clarity_score": 8.5,
    "structure_score": 7.2,
    "filler_word_count": 5,
    "feedback": "Your speech demonstrates..."
  }
}
```

#### GET /api/v1/analysis/user/{user_id}
**Query Parameters:**
```
skip: 0 (default)
limit: 100 (default)
```

**Response (200):**
```json
[
  {
    "speech_id": "uuid",
    "analysis_id": "uuid",
    "word_count": 150,
    "clarity_score": 8.5,
    "structure_score": 7.2,
    "filler_words_rating": 5,
    "feedback": "Analysis feedback...",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Speech Routes

#### GET /api/v1/speeches/
**Query Parameters:**
```
skip: 0 (default)
limit: 100 (default)
user_id: uuid (optional)
```

**Response (200):**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "title": "Speech Title",
    "content": "Speech content...",
    "source_type": "text",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### GET /api/v1/speeches/{speech_id}/analysis
**Response (200):**
```json
{
  "speech_id": "uuid",
  "analysis_id": "uuid",
  "word_count": 150,
  "clarity_score": 8.5,
  "structure_score": 7.2,
  "filler_word_count": 5,
  "feedback": "Analysis feedback...",
  "prompt": "default",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /api/v1/speeches/{speech_id}
**Response (200):**
```json
{
  "message": "Speech deleted successfully",
  "speech_id": "uuid"
}
```

## Error Response Format

All API errors follow a consistent structure:

```json
{
  "detail": "Error message",
  "error_code": "VALIDATION_ERROR",
  "request_id": "req_uuid",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | Success | Successful GET/PUT/DELETE operations |
| 201 | Created | Successful POST operations |
| 400 | Bad Request | Invalid request data or parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Valid auth but insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Resource already exists or constraint violation |
| 422 | Unprocessable Entity | Valid JSON but invalid data structure |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |

## Feature Development Dependencies

### Dependency Graph & Merge Order
```
A (Persistence) → C (History/Nav) → B (Transcription UI) → D (Export/Share) → E (Progress)
```

### A: Analysis Persistence (Priority 1)
**Components:**
- `backend/models/analysis.py` - Analysis entity with unique constraints
- `backend/repositories/analysis_repo.py` - Data access layer
- `backend/services/analysis_service.py` - Business logic with idempotency
- `backend/api/v1/routes/analyses.py` - REST endpoints

**Handoff Contract:**
```json
POST /api/v1/analysis/complete
{
  "user_id": "uuid",
  "speech_id": "uuid", 
  "transcript": "optional",
  "metrics": {"clarity": 8.5},
  "summary": "optional"
}
→ {analysis_id, created_at, is_duplicate: bool}
```

### B: Transcription UI (Priority 3)
**Dependencies:** A (Persistence)
**Components:**
- `src/components/ui/TranscriptionUpload.tsx` - File upload with progress
- `src/services/transcription.ts` - Transcription service calls
- Feature flag: `TRANSCRIPTION_UI`

### C: History/Navigation (Priority 2)
**Dependencies:** A (Persistence)
**Components:**
- `src/app/dashboard/analyses/page.tsx` - Paginated analysis list
- `src/app/dashboard/analyses/[id]/page.tsx` - Analysis detail view
- `src/services/analyses.ts` - Frontend analysis service

**Handoff Contract:**
```json
GET /api/v1/analyses?page=1&limit=20
→ {items: Analysis[], total, page, page_size}
```

### D: Export/Share (Priority 4)
**Dependencies:** A (Persistence), C (Navigation)
**Components:**
- `backend/models/share_token.py` - Share token entity
- `backend/services/export_service.py` - Export logic
- `src/components/ui/ExportDialog.tsx` - Export UI
- Feature flag: `EXPORT_ENABLED`

### E: Progress Tracking (Priority 5)
**Dependencies:** A (Persistence), C (Navigation)
**Components:**
- `src/app/dashboard/progress/page.tsx` - Progress dashboard
- `backend/services/progress_service.py` - Progress calculations
- Feature flag: `PROGRESS_UI`

## Daily Integration Plan

### Week 1: Foundation (Agent A)
- **Day 1-2:** Analysis persistence models and repositories
- **Day 3:** Analysis service with idempotency logic
- **Day 4:** REST API endpoints with proper error handling
- **Day 5:** Integration testing and documentation

### Week 2: Navigation (Agent C)
- **Day 1-2:** Analysis list page with pagination
- **Day 3:** Analysis detail page with navigation
- **Day 4:** Dashboard integration and "View All" links
- **Day 5:** E2E testing and polish

### Week 3: Transcription (Agent B)
- **Day 1-2:** Transcription upload component
- **Day 3:** Service integration with progress tracking
- **Day 4:** Error handling and retry logic
- **Day 5:** Testing and feature flag integration

### Week 4: Export (Agent D)
- **Day 1-2:** Share token model and service
- **Day 3:** Export service with multiple formats
- **Day 4:** Export UI components
- **Day 5:** Integration testing and security review

### Week 5: Progress (Agent E)
- **Day 1-2:** Progress calculation service
- **Day 3:** Progress dashboard components
- **Day 4:** Chart integration and visualization
- **Day 5:** Performance optimization and testing

## Risk Register & Rollback Plan

### High Risk Items
1. **Database Schema Changes**
   - Risk: Breaking changes to existing data
   - Mitigation: Additive-only migrations, backward compatibility
   - Rollback: Database migration reversal scripts

2. **API Breaking Changes**
   - Risk: Frontend-backend incompatibility
   - Mitigation: API versioning, contracts-first development
   - Rollback: Feature flags to disable new endpoints

3. **Authentication Integration**
   - Risk: User lockout or security vulnerabilities
   - Mitigation: Thorough testing, gradual rollout
   - Rollback: Revert to previous auth implementation

### Medium Risk Items
1. **Rate Limiting Changes**
   - Risk: Legitimate users blocked
   - Mitigation: Conservative limits, monitoring
   - Rollback: Disable rate limiting middleware

2. **File Upload Changes**
   - Risk: Upload failures or security issues
   - Mitigation: File validation, size limits
   - Rollback: Revert to previous upload handler

### Rollback Procedures
1. **Application Rollback:** Deploy previous Docker image
2. **Database Rollback:** Run migration reversal scripts
3. **Feature Rollback:** Disable feature flags
4. **Cache Rollback:** Clear application caches

## Orchestrator Approval Process

### Breaking Changes Requiring Approval
- Database schema modifications
- API contract changes (request/response structure)
- Authentication/authorization changes
- File upload/processing changes

### Approval Criteria
- All tests pass (unit, integration, E2E)
- PR size < 300 LOC
- Backward compatibility maintained
- Documentation updated
- Security review completed

### Change Management
1. **Proposal:** RFC document with technical design
2. **Review:** Orchestrator and senior engineers review
3. **Approval:** Explicit approval before implementation
4. **Implementation:** Follow approved design exactly
5. **Validation:** Testing and monitoring in staging
6. **Deployment:** Gradual rollout with feature flags