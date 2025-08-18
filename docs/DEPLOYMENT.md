# 🚀 MasterSpeak AI - Deployment Guide

## Overview

MasterSpeak AI uses a multi-environment deployment strategy with automatic deployments for different branches.

## 📊 Environment Architecture

| Environment | Branch | Purpose | Frontend | Backend |
|------------|--------|---------|----------|---------|
| **Production** | `main` | Live users | Vercel (auto) | Railway (auto) |
| **Staging** | `release-candidate` | Pre-production testing | Vercel Preview | Railway Staging |
| **Development** | Feature branches | Active development | Vercel Preview | Local/Docker |

## 🔧 Initial Setup

### Prerequisites
- Node.js 18+
- Docker & Docker Compose
- Railway CLI: `npm install -g @railway/cli`
- Vercel CLI: `npm install -g vercel`
- GitHub account with repository access

### Quick Start
```bash
# Clone repository
git clone https://github.com/kaiser-data/MasterSpeak-AI.git
cd MasterSpeak-AI

# Install dependencies
npm install
cd backend && pip install -r requirements.txt
cd ../e2e && npm install

# Set up environment
cp .env.example .env
# Edit .env with your configuration
```

## 🚀 Universal Backend Deployment

### Platform Support
MasterSpeak AI supports deployment to multiple platforms:
- **Railway** (Current primary)
- **Render** (Alternative PaaS)
- **Heroku** (Classic PaaS)
- **Fly.io** (Modern edge platform)
- **Docker** (Containerized local/cloud)
- **Kubernetes** (Enterprise orchestration)

### Quick Deployment (Any Platform)

#### Automated Setup (Recommended)
```bash
# Interactive deployment wizard
./scripts/deploy.sh --interactive

# Or direct deployment
./scripts/deploy.sh [platform] [environment]

# Examples:
./scripts/deploy.sh railway staging
./scripts/deploy.sh render production
./scripts/deploy.sh docker local
```

### Platform-Specific Setup

#### Railway (Current)
```bash
# Railway-specific staging setup
./scripts/setup-staging.sh

# Or use universal script
./scripts/deploy.sh railway staging
```

#### Render.com
```bash
# Deploy to Render
./scripts/deploy.sh render staging

# Creates render.yaml configuration automatically
```

#### Heroku
```bash
# Deploy to Heroku
./scripts/deploy.sh heroku staging

# Handles app creation and buildpack configuration
```

#### Manual Setup
```bash
# 1. Login to Railway
railway login

# 2. Link project
railway link

# 3. Create staging environment
railway environment create staging

# 4. Switch to staging
railway environment staging

# 5. Deploy
railway up

# 6. Get URL
railway domain
```

### Environment Variables
Required for both production and staging:
```bash
ENV=production|staging
DATABASE_URL=your-database-url
OPENAI_API_KEY=your-openai-key
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

## 🎨 Vercel Frontend Deployment

### Automatic Deployments
- **Production**: Automatically deploys from `main` branch
- **Preview**: Every PR and branch gets a unique preview URL

### Environment Configuration
1. Go to Vercel Dashboard → Project Settings → Environment Variables
2. Add variables for different environments:

**Production:**
```bash
NEXT_PUBLIC_API_URL=https://masterspeak-production.railway.app
```

**Preview (Staging):**
```bash
NEXT_PUBLIC_API_URL=https://masterspeak-staging.railway.app
```

## 🧪 Testing Deployments

### Local Testing
```bash
# Start all services locally
docker compose -f docker-compose.e2e.yml up --build

# Run E2E tests
cd e2e
npm test
```

### Staging Testing
```bash
# Test staging backend
curl https://masterspeak-staging.railway.app/health

# Run E2E tests against staging
cd e2e
BACKEND_URL=https://masterspeak-staging.railway.app npm test
```

### Production Smoke Test
```bash
# Check production health
curl https://masterspeak-production.railway.app/health

# Verify frontend
curl -I https://masterspeak.vercel.app
```

## 📋 Deployment Workflow

### Feature Development
1. Create feature branch from `main`
2. Develop locally with Docker
3. Push to GitHub (creates Vercel preview)
4. Create PR to `release-candidate`

### Release Process
1. Merge feature branches to `release-candidate`
2. Staging automatically deploys (Railway + Vercel)
3. Run E2E tests against staging
4. Create PR from `release-candidate` to `main`
5. Review and merge to production

### Rollback Procedure
```bash
# Railway - Rollback to previous deployment
railway rollback

# Vercel - Promote previous deployment
vercel rollback

# Or use git revert
git revert HEAD
git push origin main
```

## 🔍 Monitoring & Debugging

### View Logs
```bash
# Railway logs
railway logs

# Docker logs (local)
docker compose logs -f backend

# Vercel logs
vercel logs
```

### Health Checks
```bash
# Check all environments
for env in production staging; do
  echo "Checking $env..."
  curl https://masterspeak-$env.railway.app/health
done
```

### Database Access
```bash
# Railway database
railway connect

# Local database
docker compose exec backend python -m backend.shell
```

## 🛡️ Security Considerations

### Secrets Management
- Never commit secrets to git
- Use different secrets for each environment
- Rotate secrets regularly
- Use Railway/Vercel secret management

### CORS Configuration
- Production: Specific domain only
- Staging: Preview domains
- Local: localhost:3000

### Database Security
- Production: Managed PostgreSQL
- Staging: Separate database
- Local: SQLite for development

## 📊 CI/CD Pipeline

### GitHub Actions Workflows
- **Backend CI/CD**: Tests, linting, security scans
- **E2E Tests**: Full integration testing
- **Security Scanning**: Dependency and container scanning

### Automatic Checks
All PRs automatically run:
1. Unit tests
2. E2E tests
3. Security scans
4. Code quality checks

## 🆘 Troubleshooting

### Common Issues

#### Railway Deployment Fails
```bash
# Check build logs
railway logs

# Verify environment variables
railway variables

# Restart service
railway restart
```

#### Vercel Build Error
```bash
# Check build logs
vercel logs --output

# Clear cache and redeploy
vercel --force
```

#### Database Connection Issues
```bash
# Test connection
railway run python -c "from backend.database import engine; print('Connected!')"

# Check DATABASE_URL
railway variables get DATABASE_URL
```

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Vercel Documentation](https://vercel.com/docs)
- [Docker Documentation](https://docs.docker.com)
- [GitHub Actions](https://docs.github.com/en/actions)

## 🤝 Support

For deployment issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review logs in Railway/Vercel dashboards
3. Create an issue on GitHub
4. Contact the development team

---

Last Updated: 2025-08-17
Version: 1.0.0