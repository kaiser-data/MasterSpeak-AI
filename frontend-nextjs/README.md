# MasterSpeak AI Frontend

A modern Next.js 14 frontend for MasterSpeak AI - Advanced Speech Analysis Platform with real-time AI feedback.

## Features

- 🎯 **Modern Design System** - Built with Tailwind CSS and custom design tokens
- 🔐 **Authentication** - Secure sign-in/sign-up with form validation
- 🎤 **Speech Analysis** - Upload files, paste text, or record audio
- 📊 **Dashboard** - User analytics and progress tracking
- 🌙 **Dark Mode** - Full dark/light theme support
- 📱 **Responsive** - Mobile-first design approach
- ⚡ **Performance** - Optimized with Next.js 14 features
- 🛡️ **Type Safety** - Full TypeScript implementation

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom design system
- **Forms**: React Hook Form with Zod validation
- **Animation**: Framer Motion
- **API**: Axios with interceptors and error handling
- **State**: React Query for server state
- **Auth**: NextAuth.js (ready for integration)

## Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Set up environment**:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Run development server**:
   ```bash
   npm run dev
   ```

4. **Open your browser** and navigate to [http://localhost:3000](http://localhost:3000)

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

### Speech Analysis
- **Multi-Input Support** - Text, file upload, and audio recording
- **Real-time Recording** - Browser-based audio capture
- **File Validation** - Support for text, PDF, and audio files
- **Analysis Types** - Multiple prompt types for different use cases

### Dashboard
- **Analytics Overview** - Key metrics and progress tracking
- **Recent Activity** - Latest speech analyses
- **Quick Actions** - Fast access to common tasks
- **Responsive Design** - Works on all devices

## API Integration

The frontend integrates with the FastAPI backend through:

- **Authentication API** - User management and JWT tokens
- **Speech Analysis API** - Text and file analysis endpoints
- **User Statistics** - Progress tracking and metrics
- **Health Monitoring** - System status checks

## Development

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript compiler
npm run format       # Format code with Prettier
```

### Code Quality

- **ESLint** - Code linting and best practices
- **Prettier** - Code formatting
- **TypeScript** - Type safety and IDE support
- **Tailwind CSS** - Consistent design system

## Deployment

The application is ready for deployment on Vercel, Netlify, or any Node.js hosting platform.

1. **Build the application**:
   ```bash
   npm run build
   ```

2. **Set environment variables** in your hosting platform

3. **Deploy** using your preferred method

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is part of MasterSpeak AI - Advanced Speech Analysis Platform.