# MasterSpeak AI

A comprehensive AI-powered speech analysis platform with real-time feedback, transcription, and performance tracking.

## ✨ Features

- 🎯 **Modern Design System** - Built with Tailwind CSS and custom design tokens
- 🔐 **Authentication** - Secure sign-in/sign-up with form validation and JWT tokens
- 🎤 **Speech Analysis** - Upload files, paste text, or record audio for AI analysis
- 🎙️ **Audio Transcription** - OpenAI Whisper integration for accurate speech-to-text
- 📊 **Dashboard** - User analytics and progress tracking
- 🌙 **Dark Mode** - Full dark/light theme support
- 📱 **Responsive** - Mobile-first design approach
- ⚡ **Performance** - Optimized with Next.js 14 features
- 🛡️ **Type Safety** - Full TypeScript implementation
- 🚀 **Production Ready** - Deployed on Railway (backend) and Vercel (frontend)

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom design system
- **Forms**: React Hook Form with Zod validation
- **Animation**: Framer Motion
- **API Client**: Axios with interceptors and error handling
- **File Upload**: React Dropzone
- **UI Components**: Custom component library with dark mode

### Backend
- **Framework**: FastAPI with async/await support
- **Database**: PostgreSQL with SQLModel ORM
- **Authentication**: FastAPI Users with JWT tokens
- **AI Services**: OpenAI GPT-4 (analysis) + Whisper (transcription)
- **Rate Limiting**: SlowAPI with token bucket algorithm
- **Caching**: In-memory caching for API responses
- **Deployment**: Railway with Docker containers

### AI & Transcription
- **Speech Analysis**: OpenAI GPT-4 with custom prompts
- **Transcription**: OpenAI Whisper API with multi-format support
- **Supported Audio**: MP3, WAV, M4A, WebM, OGG (max 10MB)
- **Rate Limiting**: Intelligent retry with exponential backoff

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- PostgreSQL database
- OpenAI API key

### Frontend Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Set up environment**:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Configure API endpoint**:
   ```bash
   # .env.local
   NEXT_PUBLIC_API_BASE=http://localhost:8000
   ```

4. **Run development server**:
   ```bash
   npm run dev
   ```

5. **Open your browser** and navigate to [http://localhost:3000](http://localhost:3000)

### Backend Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Configure environment**:
   ```bash
   # .env
   DATABASE_URL=postgresql://user:password@localhost:5432/masterspeak
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=your_secret_key_here
   ```

4. **Initialize database**:
   ```bash
   python -m backend.seed_db
   ```

5. **Start the backend server**:
   ```bash
   python -m uvicorn backend.main:app --reload
   ```

### Live Demo

- **Frontend**: https://master-speak-ai.vercel.app
- **Backend API**: https://masterspeak-ai-production.up.railway.app
- **API Docs**: https://masterspeak-ai-production.up.railway.app/docs

## Project Structure

```
src/
├── app/                 # Next.js 14 App Router
│   ├── auth/           # Authentication pages
│   ├── dashboard/      # User dashboard
│   ├── layout.tsx      # Root layout
│   └── page.tsx        # Landing page
├── components/         # Reusable UI components
│   ├── providers/      # Context providers
│   └── ui/             # UI components
├── lib/                # Utilities and configurations
│   ├── api.ts         # API client and functions
│   └── auth-schemas.ts # Form validation schemas
└── types/              # TypeScript type definitions
    ├── auth.ts
    └── speech.ts
```

## Key Components

### Authentication System
- **Sign In/Up Pages** - Modern forms with validation
- **Password Strength** - Real-time password validation
- **Error Handling** - Comprehensive error states
- **Demo Account** - Quick testing credentials

### Speech Analysis & Transcription
- **Multi-Input Support** - Text input, file upload, and real-time audio recording
- **Audio Transcription** - Automatic speech-to-text with OpenAI Whisper
- **File Support** - Text (TXT), PDF, and audio files (MP3, WAV, M4A, WebM, OGG)
- **Analysis Types** - Multiple AI prompt types (General, Presentation, Conversation, Detailed, Brief)
- **Real-time Feedback** - Instant AI analysis with clarity, structure, and filler word detection
- **Progress Tracking** - Historical analysis and improvement metrics

### Dashboard
- **Analytics Overview** - Key metrics and progress tracking
- **Recent Activity** - Latest speech analyses
- **Quick Actions** - Fast access to common tasks
- **Responsive Design** - Works on all devices

## 🔌 API Integration

The frontend integrates with the FastAPI backend through:

- **Authentication API** - User registration, login, and JWT token management
- **Speech Analysis API** - Text and file analysis with AI feedback
- **Transcription API** - Audio file transcription with OpenAI Whisper
- **User Management** - Profile management and user statistics
- **Speech History** - CRUD operations for speech records
- **Health Monitoring** - System status and performance checks

### API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/jwt/login` - User login
- `GET /api/v1/auth/me` - Get current user

#### Speech Analysis
- `POST /api/v1/analysis/text` - Analyze text content
- `POST /api/v1/analysis/upload` - Upload and analyze files (text/audio)
- `GET /api/v1/analysis/results/{speech_id}` - Get analysis results

#### Transcription
- `POST /api/v1/transcription/transcribe` - Transcribe audio files
- `POST /api/v1/transcription/transcribe-and-save` - Transcribe and save as speech
- `GET /api/v1/transcription/supported-formats` - Get supported audio formats

#### Speech Management
- `GET /api/v1/speeches/` - List user speeches
- `GET /api/v1/speeches/{speech_id}` - Get specific speech
- `DELETE /api/v1/speeches/{speech_id}` - Delete speech

## 💻 Development

### Frontend Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript compiler
npm run format       # Format code with Prettier
```

### Backend Scripts

```bash
# Development
python -m uvicorn backend.main:app --reload

# Database
python -m backend.seed_db         # Initialize and seed database
python -m backend.cleanup_db      # Clean up database

# Testing
pytest test/unit/                 # Run unit tests
python test_auth_registration.py  # Test auth endpoints
python test_transcription.py      # Test transcription feature
```

### Code Quality

- **ESLint & Prettier** - Frontend code formatting and linting
- **TypeScript** - Type safety across frontend and backend APIs
- **Pydantic** - Backend data validation and serialization
- **SQLModel** - Type-safe database operations
- **Rate Limiting** - API protection with token bucket algorithm
- **Error Handling** - Comprehensive error handling with request IDs

## 🚀 Deployment

### Current Deployment

- **Frontend**: Vercel (https://master-speak-ai.vercel.app)
- **Backend**: Railway (https://masterspeak-ai-production.up.railway.app)
- **Database**: PostgreSQL on Railway

### Deploy Your Own

#### Frontend (Vercel)
1. **Connect to GitHub**:
   - Link your GitHub repository to Vercel
   - Enable automatic deployments

2. **Set environment variables**:
   ```bash
   NEXT_PUBLIC_API_BASE=https://your-backend-url.com
   ```

3. **Deploy**: Automatic on Git push

#### Backend (Railway)
1. **Connect to GitHub**:
   - Link repository to Railway
   - Enable automatic deployments

2. **Set environment variables**:
   ```bash
   DATABASE_URL=postgresql://user:password@host:port/dbname
   OPENAI_API_KEY=your_openai_api_key
   SECRET_KEY=your_secret_key
   ENV=production
   ```

3. **Deploy**: Automatic on Git push

### Manual Deployment

#### Frontend
```bash
npm run build
npm run start
```

#### Backend
```bash
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 Recent Updates

- ✅ **Audio Transcription** - Added OpenAI Whisper integration for speech-to-text
- ✅ **Enhanced Audio Support** - WAV, MP3, M4A, WebM, OGG file support
- ✅ **Authentication Fixes** - Resolved signup/login 404 issues
- ✅ **API Improvements** - Comprehensive error handling and rate limiting
- ✅ **Production Deployment** - Live on Railway and Vercel

## 📄 License

This project is part of MasterSpeak AI - Advanced Speech Analysis Platform.

---

**Built with ❤️ using Next.js, FastAPI, and OpenAI**