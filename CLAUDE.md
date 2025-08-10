# CLAUDE.md
# 🚀 Mission Update

Please help me repair, modernize, and redesign this project.

## What I Want:
- ✅ Fix any broken or inconsistent Python/Streamlit code
- ✅ Refactor backend for modularity and clarity
- ✅ Replace the Streamlit frontend with a modern, React-based UI
  - Preferred libraries: ShadCN, Tailwind, or Material UI
- ✅ Structure the app with proper backend/frontend separation
- ✅ Use SuperClaude tools like `/sc:implement`, `/sc:spawn`, Context7, and `/sc:design` to plan and execute
- ✅ Deliver clean, production-ready code with smart UX decisions

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Start the FastAPI server with hot reload
python -m uvicorn backend.main:app --reload

# Alternative: Start on specific host/port
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Database Management
```bash
# Initialize database (creates tables and seeds initial data)
python -m backend.seed_db

# Alternative database initialization
python -m backend.init_db
```

### Testing
```bash
# Run all unit tests
pytest test/unit/

# Run specific test file
pytest test/unit/test_analysis_service.py -v

# Run tests with coverage
pytest test/unit/ --cov=backend --cov-report=html
```

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env
# Then edit .env with your actual API keys
```

## Architecture Overview

### Core Application Structure
- **FastAPI Backend**: Main application server with async/await support
- **SQLModel ORM**: Database models and operations using SQLAlchemy core
- **Jinja2 Templates**: Server-side rendered HTML frontend
- **OpenAI Integration**: GPT-4 powered speech analysis service

### Key Components

#### Database Layer (`backend/database/`)
- **models.py**: SQLModel definitions for User, Speech, SpeechAnalysis entities
- **database.py**: Database connection, session management, and initialization
- Uses UUID primary keys across all entities
- Relationships: User → Speech (1:many), Speech → SpeechAnalysis (1:1)

#### API Routes (`backend/routes/`)
- **analyze_routes.py**: Speech analysis endpoints with file upload support
- **user_routes.py**: User management and speech history
- **auth_routes.py**: Authentication (JWT-based)
- **database_routes.py**: Database management utilities
- **general_routes.py**: Static pages and navigation

#### Services Layer
- **analysis_service.py**: Core business logic for speech processing and analysis
- **openai_service.py**: OpenAI API integration with rate limiting, caching, and retry logic
- **prompts.py**: Analysis prompt templates for different analysis types

#### Configuration
- **config.py**: Centralized settings using pydantic-settings
- Environment variables: DATABASE_URL, OPENAI_API_KEY, SECRET_KEY
- Automatic .env file loading and validation

### Analysis Architecture
The application supports multiple analysis types:
- **General Analysis**: Overall speech evaluation
- **Clarity Focus**: Emphasis on speech clarity and articulation
- **Structure Focus**: Logical flow and organization
- **Engagement Focus**: Audience engagement and impact

#### OpenAI Integration Features
- **Rate Limiting**: Token bucket algorithm (40 tokens/minute)
- **Caching**: MD5-based response caching to reduce API calls
- **Retry Logic**: Exponential backoff for rate limit errors
- **Structured Responses**: JSON-only responses with Pydantic validation

### Frontend Architecture
- **Server-Side Rendering**: Jinja2 templates with Bootstrap styling
- **Static Assets**: CSS, JS, and images served from `/frontend/static/`
- **Template Structure**: Base template with component inheritance
- **File Upload**: Supports TXT and PDF file analysis

### Database Schema
```
User (id, email, hashed_password, full_name, is_active, is_superuser)
  ↓ 1:many
Speech (id, user_id, title, source_type, content, feedback, created_at)
  ↓ 1:1
SpeechAnalysis (id, speech_id, word_count, clarity_score, structure_score, 
                filler_word_count, prompt, feedback, created_at)
```

### Key Design Patterns
- **Service Layer Pattern**: Business logic separated from route handlers
- **Repository Pattern**: Database operations abstracted through SQLModel
- **Dependency Injection**: FastAPI dependency system for database sessions
- **Error Handling**: Centralized HTTPException handling with detailed logging

### API Testing
Use `test_main.http` for manual API testing with endpoints for:
- User registration/login
- Speech upload and analysis
- Results retrieval

## Important Implementation Notes

### OpenAI Service
- Uses async/await pattern with proper resource cleanup
- Implements sophisticated caching to minimize API costs
- Rate limiter prevents API quota exhaustion
- All responses validated against Pydantic schemas

### Database Operations
- All operations use proper transaction handling
- Speech and analysis creation is atomic
- Database initialization includes automatic seeding
- UUID primary keys ensure global uniqueness

### Security Considerations
- JWT-based authentication system
- Password hashing with bcrypt
- Environment variable configuration for secrets
- CORS middleware configured (currently permissive for development)

### File Upload Handling
- Supports both direct text input and file uploads
- PDF and TXT file processing
- Content validation before analysis
- Proper error handling for file processing failures
- 404
This page could not be found.