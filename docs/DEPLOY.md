# 🚀 Deployment Guide - MasterSpeak AI

Comprehensive deployment guide for MasterSpeak AI across different platforms with rate limiting configuration.

## 📋 Pre-Deployment Checklist

### **Environment Variables Required**

#### **Core Configuration**
```bash
ENV="production"
DEBUG=false
DATABASE_URL="postgresql://user:pass@host:5432/masterspeak_prod"
OPENAI_API_KEY="your_openai_api_key"
```

#### **Security Configuration**
```bash
SECRET_KEY="your_strong_random_secret_key_32_chars_min"
RESET_SECRET="another_strong_secret_for_password_reset"
VERIFICATION_SECRET="yet_another_secret_for_email_verification"
ALLOWED_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"
JWT_LIFETIME_SECONDS=3600
```

#### **Rate Limiting Configuration**
```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT="60/minute"
RATE_LIMIT_AUTH="5/minute"
RATE_LIMIT_ANALYSIS="10/minute" 
RATE_LIMIT_UPLOAD="5/minute"
RATE_LIMIT_HEALTH="100/minute"
REDIS_URL="redis://your-redis-host:6379/0"  # Optional but recommended
```

#### **Optional: Observability**
```bash
SENTRY_DSN="https://your-sentry-dsn"
LOG_LEVEL="WARNING"
```

---

## 🛤️ Railway Deployment

Railway uses Docker from `/backend` directory. Frontend is deployed on Vercel.

### **1. Setup Railway Project**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and create project
railway login
railway init
```

### **2. Configure Environment Variables**
```bash
# Set production variables
railway variables set ENV=production
railway variables set DEBUG=false
railway variables set RATE_LIMIT_ENABLED=true
railway variables set RATE_LIMIT_DEFAULT="60/minute"
railway variables set REDIS_URL="\${{Redis.REDIS_URL}}"  # Railway Redis service

# Set secrets (replace with actual values)
railway variables set OPENAI_API_KEY="your_key"
railway variables set SECRET_KEY="your_secret"
railway variables set DATABASE_URL="\${{DATABASE_URL}}"  # Railway PostgreSQL
```

### **3. Add Redis Service**
```bash
railway add redis
```

### **4. Deploy**
```bash
railway deploy
```

### **5. Custom Domain (Optional)**
```bash
railway domain add yourdomain.com
```

---

## ✈️ Fly.io Deployment

### **1. Install Fly CLI**
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh
```

### **2. Initialize App**
```bash
# Launch app (uses existing fly.toml)
fly launch --no-deploy

# Add PostgreSQL database
fly postgres create --name masterspeak-db

# Attach database
fly postgres attach --app masterspeak-ai masterspeak-db
```

### **3. Add Redis**
```bash
# Add Redis via Upstash
fly redis create
```

### **4. Set Environment Variables**
```bash
# Set secrets
fly secrets set OPENAI_API_KEY="your_key"
fly secrets set SECRET_KEY="your_secret" 
fly secrets set RESET_SECRET="your_reset_secret"
fly secrets set VERIFICATION_SECRET="your_verification_secret"
fly secrets set REDIS_URL="redis://your-redis-connection-string"

# Set production origins
fly secrets set ALLOWED_ORIGINS="https://yourapp.fly.dev"
```

### **5. Deploy**
```bash
fly deploy
```

### **6. Scale & Monitor**
```bash
# Scale app
fly scale count 2

# View logs
fly logs

# Open app
fly open
```

---

## ☁️ Vercel Frontend Deployment

### **1. Connect Repository**
- Connect your GitHub repository to Vercel
- Select `frontend-nextjs` as root directory

### **2. Environment Variables**
```bash
# Set in Vercel dashboard
NEXT_PUBLIC_API_URL="https://your-backend-domain.com"
NODE_ENV="production"
```

### **3. Build Configuration**
```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "outputDirectory": ".next"
}
```

---

## 🐳 Docker Production Deployment

### **1. Multi-Stage Production Build**

**Backend Production Dockerfile:**
```dockerfile
FROM python:3.11-slim AS production

# Production optimizations
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install production dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ ./backend/
COPY generate_secrets.py .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### **2. Production Docker Compose**

**docker-compose.prod.yml:**
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile.prod
    restart: unless-stopped
    environment:
      - ENV=production
      - RATE_LIMIT_ENABLED=true
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    networks:
      - app-network

  frontend:
    build:
      context: ./frontend-nextjs
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    depends_on:
      - backend
    networks:
      - app-network

  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: masterspeak_prod
      POSTGRES_USER: masterspeak
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

---

## 🎛️ Environment-Specific Rate Limiting

### **Production Settings**
```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT="60/minute"    # Conservative for production
RATE_LIMIT_AUTH="5/minute"        # Prevent brute force
RATE_LIMIT_ANALYSIS="10/minute"   # Protect expensive AI calls
REDIS_URL="redis://prod-redis:6379/0"  # Required for production
```

### **Staging Settings (Relaxed)**
```bash
RATE_LIMIT_ENABLED=false          # Disable for easier testing
# OR with higher limits:
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT="500/minute"   # Much higher for testing
RATE_LIMIT_AUTH="50/minute"
```

### **Development Settings**
```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT="200/minute"   # Higher limits for development
REDIS_URL=""                      # Optional - uses in-memory
```

---

## 🔍 Health Checks & Monitoring

### **Backend Health Endpoints**
- `GET /health` - Basic service health
- `GET /api/status` - Detailed service status with database connectivity
- `GET /_internal/rate-limit-status` - Rate limiting configuration (internal only)

### **Expected Health Response**
```json
{
  "status": "healthy",
  "service": "MasterSpeak AI",
  "version": "1.0.0", 
  "timestamp": "2025-08-08T10:30:00.000Z",
  "environment": "production",
  "checks": {
    "database": "healthy",
    "redis": "healthy",
    "rate_limiting": "enabled"
  }
}
```

### **Monitoring Setup**
```bash
# Add monitoring environment variables
SENTRY_DSN="https://your-sentry-dsn"
LOG_LEVEL="WARNING"  # INFO for staging, WARNING/ERROR for production

# Custom metrics endpoint (if implemented)
METRICS_ENABLED=true
METRICS_PORT=9090
```

---

## 🔒 Security Hardening

### **Production Security Checklist**

#### **Environment Variables**
- [ ] All secrets use strong random values (32+ characters)
- [ ] `DEBUG=false` in production
- [ ] `ALLOWED_ORIGINS` set to exact production domains
- [ ] Database uses encrypted connections
- [ ] Redis uses AUTH if exposed

#### **Rate Limiting**
- [ ] `RATE_LIMIT_ENABLED=true` in production
- [ ] Conservative rate limits set (not too high)
- [ ] Redis backend configured for distributed rate limiting
- [ ] Rate limiting tested and validated

#### **Infrastructure**
- [ ] Use HTTPS/TLS for all connections
- [ ] Database not publicly accessible
- [ ] Redis not publicly accessible  
- [ ] Regular security updates applied

---

## 🚨 Troubleshooting

### **Common Deployment Issues**

#### **Rate Limiting Not Working**
```bash
# Check configuration
curl http://your-app/api/status

# Check logs for rate limiting messages
# Look for: "Rate limiting enabled with Redis backend" or "in-memory backend"

# Test rate limiting
for i in {1..100}; do curl http://your-app/health; done
```

#### **Redis Connection Issues**
```bash
# Check Redis connectivity
redis-cli -u $REDIS_URL ping

# Application logs should show:
# "Redis connected for rate limiting" (success)
# "Redis unavailable, using in-memory rate limiting" (fallback)
```

#### **Environment Variable Issues**
```bash
# Verify all required variables are set
env | grep -E "(RATE_LIMIT|REDIS|OPENAI)"

# Check application startup logs for missing variables
```

### **Performance Optimization**

#### **Database Connection Pooling**
```bash
# Add to production environment
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
```

#### **Rate Limiting Optimization**
```bash
# Use Redis for distributed rate limiting
REDIS_URL="redis://your-redis-cluster:6379/0"

# Tune limits based on capacity
RATE_LIMIT_DEFAULT="100/minute"  # Increase if infrastructure can handle
```

---

## 📊 Production Monitoring

### **Key Metrics to Monitor**
- **Response Times**: < 500ms for API calls
- **Error Rates**: < 1% for critical endpoints
- **Rate Limiting**: 429 response rates and patterns
- **Database**: Connection pool usage and query times
- **Redis**: Memory usage and hit rates

### **Alerting Rules**
```bash
# High error rate
error_rate > 5% for 5 minutes

# Rate limiting triggered frequently
rate_limit_429_responses > 100/minute for 10 minutes

# Database connectivity issues
database_connection_failures > 0 for 1 minute

# Redis connectivity issues  
redis_connection_failures > 0 for 5 minutes
```

---

## 🔄 Alembic Database Migrations

### **Production Migration Setup**
```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Generate migration
alembic revision --autogenerate -m "Initial production schema"

# Run migrations in production
alembic upgrade head
```

### **Railway/Fly.io Integration**
Both platforms support `release_command` for running migrations:

**Railway:**
```json
{
  "build": {
    "builder": "dockerfile" 
  },
  "deploy": {
    "releaseCommand": "alembic upgrade head"
  }
}
```

**Fly.io:**
```toml
[deploy]
  release_command = "alembic upgrade head"
```

---

**🎯 Deployment Complete!** Your MasterSpeak AI application should now be running in production with comprehensive rate limiting, monitoring, and security measures.