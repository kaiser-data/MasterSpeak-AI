# ADR-0001: MasterSpeak-AI Architecture Decision Record

## Status
Accepted

## Context
MasterSpeak-AI is a speech analysis platform that requires scalable architecture supporting real-time analysis, user management, and data persistence. The system needs to handle speech transcription, AI-powered analysis, and user session management while maintaining security and performance standards.

## Decision
We adopt a modern full-stack architecture with clear separation of concerns:

### Frontend Architecture (Next.js 14 with App Router)
```
src/
├── app/                     # App Router pages & layouts
│   ├── auth/               # Authentication pages
│   ├── dashboard/          # Main application interface
│   └── layout.tsx          # Root layout with providers
├── components/             # Reusable UI components
│   └── ui/                 # Core UI components
├── lib/                    # Core utilities & configuration
│   ├── api.ts             # API client with interceptors
│   ├── env.ts             # Environment configuration (Zod)
│   ├── log.ts             # Frontend logging utility
│   └── http.ts            # HTTP helpers & error mapping
├── domain/                 # Domain types & models
│   └── types.ts           # TypeScript domain types
├── services/               # Business logic services
│   └── analyses.ts        # Analysis service layer
└── types/                  # Application-wide types
```

### Backend Architecture (FastAPI with Layered Design)
```
backend/
├── main.py                 # FastAPI application entry
├── config.py              # Application configuration
├── api/v1/                 # API route definitions
│   ├── endpoints/         # Route handlers
│   └── router.py          # Route registration
├── models/                 # SQLModel domain models
│   ├── speech.py          # Speech entity
│   ├── analysis.py        # Analysis entity
│   └── share_token.py     # Share token entity
├── repositories/           # Data access layer
│   ├── speech_repo.py     # Speech repository
│   └── analysis_repo.py   # Analysis repository
├── services/               # Business logic layer
│   ├── analysis_service.py # Analysis orchestration
│   └── export_service.py  # Export functionality
├── middleware/             # Cross-cutting concerns
│   └── rate_limit.py      # Rate limiting
├── utils/                  # Utility functions
│   └── logging.py         # Structured logging
└── database/               # Database layer
    ├── database.py        # Connection & session management
    └── models.py          # Legacy model definitions
```

## Architectural Principles

### 1. Service Layer Pattern
- **Repositories**: Handle data persistence and queries
- **Services**: Orchestrate business logic and coordinate repositories
- **Controllers**: Handle HTTP concerns and delegate to services

### 2. Domain-Driven Design
- Clear domain models with TypeScript/Pydantic schemas
- Separation between API contracts and internal models
- Consistent error handling across layers

### 3. API-First Design
- RESTful API design under `/api/v1/` namespace
- OpenAPI documentation with Pydantic schemas
- Consistent JSON response formats with proper HTTP status codes

### 4. Security by Design
- JWT-based authentication with secure token management
- Rate limiting on all mutating endpoints
- Input validation at API boundaries
- No PII logging in any layer

### 5. Observability
- Structured logging with correlation IDs
- Request/response logging without sensitive data
- Performance metrics and error tracking
- Feature flag support for controlled rollouts

## Technology Choices

### Frontend Stack
- **Next.js 14**: React framework with App Router for modern routing
- **TypeScript**: Type safety across the application
- **Tailwind CSS**: Utility-first styling framework
- **Zod**: Runtime type validation for environment variables
- **React Query**: Server state management and caching

### Backend Stack
- **FastAPI**: Modern Python web framework with automatic OpenAPI
- **SQLModel**: Type-safe ORM with Pydantic integration
- **PostgreSQL**: Relational database for data persistence
- **Asyncio**: Asynchronous request handling
- **Pydantic**: Data validation and serialization

### Infrastructure
- **Railway**: Deployment platform with PostgreSQL hosting
- **Vercel**: Frontend deployment with serverless functions
- **GitHub Actions**: CI/CD pipeline automation

## Data Flow Architecture

```
User Input → Next.js Frontend → FastAPI Backend → PostgreSQL Database
     ↓              ↓                ↓              ↓
1. User Action   2. API Call     3. Business     4. Data
   Validation       /api/v1/*      Logic           Persistence
```

### API Communication
- Frontend communicates with backend via REST API
- Next.js API routes proxy to FastAPI backend
- Consistent error handling and response formats
- JWT authentication with secure token storage

### Database Design
- Entity relationships: User → Speech (1:many) → SpeechAnalysis (1:1)
- UUID primary keys for security and distribution
- Audit trails with created_at/updated_at timestamps
- Soft deletes for data retention compliance

## Consequences

### Positive
- **Scalability**: Clean separation allows independent scaling
- **Maintainability**: Clear boundaries between concerns
- **Developer Experience**: Type safety and modern tooling
- **Security**: Multiple layers of validation and authentication
- **Observability**: Comprehensive logging and monitoring

### Negative
- **Complexity**: Multiple layers require coordination
- **Learning Curve**: Developers need familiarity with multiple technologies
- **Deployment**: Coordination required between frontend and backend deployments

### Risks & Mitigations
- **API Version Compatibility**: Use semantic versioning and deprecation policies
- **Database Migrations**: Additive-only changes during development
- **Authentication**: Secure token management with proper expiration
- **Rate Limiting**: Prevent abuse with token bucket implementation

## Implementation Guidelines

### Feature Development
1. Design API contracts first with OpenAPI schemas
2. Implement backend services with full test coverage
3. Create frontend services that consume backend APIs
4. Add integration tests for critical user flows
5. Deploy with feature flags for controlled rollouts

### Code Quality
- All changes require type checking and linting
- Unit tests required for services and repositories
- Integration tests for API endpoints
- Pre-commit hooks enforce quality standards

### Monitoring & Observability
- Structured logging with correlation IDs
- Performance metrics for critical operations
- Error tracking with actionable alerts
- User analytics for feature usage insights

## Future Considerations
- Microservices decomposition as system grows
- Event-driven architecture for real-time features
- CDN integration for static asset optimization
- Caching layer for improved performance