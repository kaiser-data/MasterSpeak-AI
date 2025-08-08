# MasterSpeak AI

A comprehensive speech analysis platform that helps users improve their public speaking skills through AI-powered feedback, featuring both modern React frontend and REST API backend.

## 🎯 Features

### **Frontend (Next.js 14)**
- **Modern React Interface**: Built with Next.js 14, TypeScript, and Tailwind CSS
- **Authentication**: Secure user login/signup with JWT tokens
- **Speech Analysis Dashboard**: Interactive interface for speech analysis
- **Multi-Modal Analysis**: Text input, audio file upload, and live recording
- **Real-Time Results**: Instant feedback with scores and suggestions
- **Responsive Design**: Mobile-first responsive interface

### **Backend (FastAPI)**
- **REST API**: Comprehensive RESTful API with OpenAPI documentation
- **User Management**: Secure authentication with FastAPIUsers
- **Speech Analysis Engine**: AI-powered analysis using OpenAI GPT models
- **Rate Limiting**: Configurable rate limiting with Redis backend support
- **Database**: SQLModel with async support (SQLite/PostgreSQL)
- **Production Ready**: Health checks, CORS, security middleware

### **Analysis Capabilities**
- **Text Analysis**: Direct text input analysis with multiple prompt types
- **Audio Processing**: File upload support for audio analysis
- **Live Recording**: Browser-based audio recording and analysis
- **Comprehensive Scoring**: Clarity, confidence, pace, and structure analysis
- **Personalized Feedback**: AI-generated improvement suggestions
- **History Tracking**: Track progress over time with historical data

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (Backend)
- **Node.js 18+** (Frontend) 
- **OpenAI API Key** (Required for analysis)
- **Redis** (Optional, for distributed rate limiting)

### 1. Clone & Setup Environment

```bash
# Clone the repository
git clone https://github.com/kaiser-data/MasterSpeak-AI.git
cd MasterSpeak-AI

# Copy and configure environment
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` with your settings:

```bash
# Required Configuration
OPENAI_API_KEY="your_openai_api_key_here"
SECRET_KEY="your_strong_random_secret_key_32_chars_min"
RESET_SECRET="another_strong_secret_for_password_reset"
VERIFICATION_SECRET="yet_another_secret_for_email_verification"

# Optional: Database (defaults to SQLite)
DATABASE_URL="sqlite:///./data/masterspeak.db"

# Optional: Rate Limiting with Redis
RATE_LIMIT_ENABLED=true
REDIS_URL="redis://localhost:6379/0"

# Development
ENV="development"
DEBUG=true
ALLOWED_ORIGINS="http://localhost:3000,http://localhost:8000"
```

### 3. Backend Setup (FastAPI)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m backend.seed_db

# Start backend server
uvicorn backend.main:app --reload --port 8000
```

**Backend will be available at:** http://localhost:8000
**API Documentation:** http://localhost:8000/docs

### 4. Frontend Setup (Next.js)

```bash
# Navigate to frontend
cd frontend-nextjs

# Install dependencies
npm install

# Start development server
npm run dev
```

**Frontend will be available at:** http://localhost:3000

### 5. Access the Application

1. **Open** http://localhost:3000 in your browser
2. **Sign in** with demo account: `demo@masterspeak.ai` / `Demo123!`
3. **Start analyzing** speech through text input, file upload, or recording

## 🐳 Docker Setup (Recommended)

### Development with Docker Compose

```bash
# Start all services (backend, frontend, Redis)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### E2E Testing with Docker

```bash
# Run complete E2E test suite
docker-compose -f docker-compose.e2e.yml up --build

# View test reports
open e2e/playwright-report/index.html
```

## 📱 Usage Guide

### **Authentication**
- **Sign Up**: Create new account with email verification
- **Sign In**: Access with email/password or demo account
- **Demo Account**: `demo@masterspeak.ai` / `Demo123!`

### **Speech Analysis Modes**

#### **1. Text Analysis**
```bash
1. Navigate to Dashboard
2. Click "Text Analysis" 
3. Enter your speech text
4. Select analysis focus (general, clarity, structure)
5. Click "Analyze Speech"
6. Review results and suggestions
```

#### **2. File Upload Analysis**
```bash
1. Go to "Upload Analysis"
2. Drag & drop text/audio files (TXT, PDF, WAV, MP3)
3. Configure analysis parameters
4. Upload and process
5. View detailed feedback
```

#### **3. Live Recording**
```bash
1. Click "Record Speech"
2. Allow microphone permissions
3. Record your speech (up to 5 minutes)
4. Stop recording and analyze
5. Get real-time feedback
```

### **Results & Analytics**
- **Scoring**: Clarity, confidence, pace, and structure metrics (0-100)
- **Feedback**: AI-generated specific improvement suggestions  
- **History**: Track progress over time with historical analysis
- **Export**: Download results as PDF or CSV

## 🏗️ Project Architecture

```
MasterSpeak-AI/
├── backend/                     # FastAPI REST API
│   ├── api/v1/                  # API v1 endpoints  
│   │   ├── endpoints/           # Route handlers
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── analysis.py     # Speech analysis endpoints
│   │   │   └── users.py        # User management endpoints
│   │   └── router.py           # API router configuration
│   ├── database/               # Database layer
│   │   ├── database.py         # Database connection & session
│   │   └── models.py           # SQLModel database models  
│   ├── middleware/             # Custom middleware
│   │   └── rate_limiting.py    # Rate limiting with Redis
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py            # Auth request/response schemas
│   │   ├── analysis.py        # Analysis schemas
│   │   └── user.py            # User schemas
│   ├── routes/                 # Legacy HTML routes (compatibility)
│   ├── config.py              # Environment configuration
│   ├── main.py                # FastAPI application entry point
│   ├── openai_service.py      # OpenAI API integration
│   └── seed_db.py             # Database initialization
├── frontend-nextjs/            # Next.js 14 React Frontend  
│   ├── src/
│   │   ├── app/                # Next.js 14 App Router
│   │   │   ├── auth/           # Authentication pages
│   │   │   ├── dashboard/      # Dashboard pages
│   │   │   └── layout.tsx      # Root layout
│   │   ├── components/         # React components
│   │   │   ├── ui/             # UI components
│   │   │   └── providers/      # Context providers
│   │   ├── lib/                # Utility libraries
│   │   │   ├── api.ts          # API client (Axios)
│   │   │   └── auth-schemas.ts # Form validation (Zod)
│   │   └── types/              # TypeScript type definitions
│   ├── package.json           # Node.js dependencies
│   └── tailwind.config.js     # Tailwind CSS configuration
├── e2e/                       # End-to-end testing (Playwright)
│   ├── tests/                 # Test suites
│   │   ├── auth.spec.ts       # Authentication flow tests  
│   │   ├── speech-analysis.spec.ts # Analysis workflow tests
│   │   └── helpers/           # Test helper classes
│   ├── playwright.config.ts   # Playwright configuration
│   └── docker-compose.e2e.yml # E2E testing environment
├── test/                      # Backend unit tests
│   └── unit/
│       ├── test_rate_limiting.py # Rate limiting tests
│       └── test_analysis.py      # Analysis logic tests  
├── .github/workflows/         # GitHub Actions CI/CD
│   └── e2e-tests.yml         # E2E testing pipeline
├── docs/                      # Documentation
│   ├── PRODUCTION_READINESS.md # Production deployment guide
│   └── API.md                   # API documentation
├── docker-compose.yml         # Development environment
├── docker-compose.e2e.yml     # E2E testing environment
├── .env.example              # Environment configuration template
├── requirements.txt          # Python dependencies
└── README.md                # Project documentation
```

## 🛠️ Development & Testing

### **Local Development**
```bash
# Backend development
cd backend
uvicorn main:app --reload --port 8000

# Frontend development  
cd frontend-nextjs
npm run dev

# Run unit tests
python -m pytest test/

# Run E2E tests
cd e2e && ./scripts/run-local.sh
```

### **Production Deployment**
- **Production Readiness**: See `PRODUCTION_READINESS.md` for deployment checklist
- **Docker**: Multi-stage builds with health checks
- **CI/CD**: GitHub Actions with automated testing
- **Monitoring**: Built-in health endpoints and error tracking

## 🧪 Testing

### **Test Coverage**
- **Unit Tests**: Backend logic and API endpoints  
- **Integration Tests**: Database and external API integration
- **E2E Tests**: Complete user workflows with Playwright
- **Performance Tests**: Load testing and rate limiting validation

### **Running Tests**
```bash
# Unit tests
python -m pytest test/ -v

# E2E tests (local)
cd e2e && npm test

# E2E tests (Docker)
docker-compose -f docker-compose.e2e.yml up --build
```

## 📊 Production Features

### **Performance & Scalability**
- **Rate Limiting**: Configurable limits with Redis backend
- **Caching**: Redis-based caching for improved response times  
- **Database**: Async SQLModel with connection pooling
- **CDN Ready**: Static asset optimization and caching headers

### **Security**
- **Authentication**: JWT-based with secure token management
- **Authorization**: Role-based access control
- **Rate Limiting**: DDoS protection and abuse prevention
- **Input Validation**: Comprehensive request validation
- **CORS**: Configurable cross-origin resource sharing
- **Security Headers**: Production-ready security middleware

### **Monitoring & Observability**
- **Health Checks**: Comprehensive service health monitoring
- **Logging**: Structured logging with configurable levels
- **Error Tracking**: Integration with Sentry for error monitoring
- **Metrics**: Performance metrics and usage analytics

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** your feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'feat: add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### **Development Guidelines**
- Follow the existing code style and conventions
- Write comprehensive tests for new features
- Update documentation for any API changes
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

### **Core Technologies**
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[Next.js](https://nextjs.org/)** - React framework for production
- **[SQLModel](https://sqlmodel.tiangolo.com/)** - SQL databases with Python
- **[OpenAI](https://openai.com/)** - AI-powered speech analysis
- **[Playwright](https://playwright.dev/)** - End-to-end testing framework

### **Development Tools**  
- **[TypeScript](https://www.typescriptlang.org/)** - Type-safe JavaScript
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[Redis](https://redis.io/)** - In-memory data structure store
- **[Docker](https://www.docker.com/)** - Containerization platform

---

**Built with ❤️ for public speaking improvement**