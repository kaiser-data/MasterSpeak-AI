# 📊 Observability Guide - MasterSpeak AI

Comprehensive observability setup for monitoring rate limiting, performance, and security events.

## 🔍 Structured Logging

### **Log Format**
All logs use structured JSON format in production:

```json
{
  "timestamp": "2025-08-08T10:30:00.000Z",
  "level": "WARNING",
  "logger": "masterspeak.rate_limit",
  "message": "Rate limit exceeded for 127.0.0.1 on /api/v1/analysis/text",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "module": "rate_limiting",
  "event_type": "rate_limit_exceeded",
  "client_ip": "127.0.0.1",
  "endpoint": "/api/v1/analysis/text",
  "limit": "10/minute",
  "retry_after": 45
}
```

### **Request Tracing**
Every request gets a unique `request_id` that flows through:
- Request/response logs
- Rate limiting events
- Error messages
- Response headers (`X-Request-ID`)

## 🚨 Rate Limiting Observability

### **429 Event Monitoring**
Rate limit exceeded events are logged with full context:

```json
{
  "event_type": "rate_limit_exceeded",
  "client_ip": "192.168.1.100", 
  "endpoint": "/api/v1/auth/jwt/login",
  "method": "POST",
  "limit": "5/minute",
  "retry_after": 60,
  "user_agent": "Mozilla/5.0...",
  "request_id": "uuid-here"
}
```

### **Sentry Integration**
When `SENTRY_DSN` is configured, 429 events include:
- **Tags**: `event_type=rate_limit_exceeded`, `client_ip`, `endpoint`
- **Context**: Full rate limiting details
- **Breadcrumbs**: Rate limiting timeline

### **Log Queries**
Find rate limiting patterns:

```bash
# High-volume rate limiting (possible DDoS)
grep "rate_limit_exceeded" logs.json | jq 'select(.client_ip == "X.X.X.X")' | wc -l

# Most rate-limited endpoints
grep "rate_limit_exceeded" logs.json | jq -r '.endpoint' | sort | uniq -c | sort -nr

# Rate limiting by time window
grep "rate_limit_exceeded" logs.json | jq -r '.timestamp[0:13]' | sort | uniq -c
```

## ⚡ Performance Monitoring

### **Slow Request Tracking**
Requests > 500ms are automatically logged:

```json
{
  "event_type": "performance_metric",
  "endpoint": "/api/v1/analysis/text",
  "method": "POST", 
  "response_time_ms": 1250.5,
  "status_code": 200,
  "severity": "warning"
}
```

### **Key Metrics**
Monitor these performance indicators:

| Metric | Threshold | Action |
|--------|-----------|--------|
| Response Time | > 1000ms | Investigate slow endpoints |
| Rate Limit 429s | > 100/min | Check for DDoS or scaling needs |
| Error Rate | > 5% | Review application errors |
| Database Queries | > 100ms | Optimize slow queries |

## 🔒 Security Event Logging

### **Security Events**
Authentication failures, suspicious patterns:

```json
{
  "event_type": "security_failed_auth",
  "client_ip": "192.168.1.100",
  "severity": "warning",
  "endpoint": "/api/v1/auth/jwt/login",
  "failure_count": 5,
  "time_window": "5 minutes"
}
```

### **Sensitive Data Protection**
Automatic redaction of sensitive information:
- Passwords, API keys, tokens
- Long strings (likely secrets) > 50 characters
- Environment variables with sensitive keywords

## 📈 Monitoring Setup

### **Environment Variables**
```bash
# Observability configuration
SENTRY_DSN="https://your-sentry-dsn"
LOG_LEVEL="WARNING"  # DEBUG|INFO|WARNING|ERROR

# Development vs Production
ENV="production"  # Affects log format and level
```

### **Log Levels by Environment**
- **Development**: DEBUG (detailed logs, simple format)
- **Testing**: WARNING (reduce noise during tests)  
- **Production**: WARNING (structured JSON, performance focus)

### **Sentry Configuration**
```python
# Automatic setup when SENTRY_DSN is present
import sentry_sdk
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=1.0,
    environment=settings.ENV
)
```

## 🔧 Inspecting 429 Events

### **Real-time Monitoring**
```bash
# Follow rate limiting events
tail -f app.log | grep "rate_limit_exceeded"

# Parse structured logs  
tail -f app.log | jq 'select(.event_type == "rate_limit_exceeded")'
```

### **Analysis Queries**
```bash
# Top rate-limited IPs
cat logs.json | jq -r 'select(.event_type == "rate_limit_exceeded") | .client_ip' | sort | uniq -c | sort -nr | head -10

# Rate limiting patterns by endpoint
cat logs.json | jq -r 'select(.event_type == "rate_limit_exceeded") | "\(.endpoint) \(.limit)"' | sort | uniq -c

# Rate limiting timeline
cat logs.json | jq -r 'select(.event_type == "rate_limit_exceeded") | "\(.timestamp[0:16]) \(.client_ip) \(.endpoint)"' | sort
```

### **Dashboard Metrics**
Key metrics to display on monitoring dashboards:

```sql
-- Rate limiting events per minute
SELECT 
  date_trunc('minute', timestamp) as time_bucket,
  count(*) as rate_limit_events
FROM logs 
WHERE event_type = 'rate_limit_exceeded'
GROUP BY time_bucket
ORDER BY time_bucket;

-- Top rate-limited endpoints
SELECT 
  endpoint,
  count(*) as total_429s,
  count(distinct client_ip) as unique_ips
FROM logs
WHERE event_type = 'rate_limit_exceeded'
GROUP BY endpoint
ORDER BY total_429s DESC;
```

## 🚀 Production Monitoring

### **Alerting Rules**
```yaml
# High rate limiting volume
- alert: HighRateLimitVolume
  expr: rate_limit_events_per_minute > 100
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High volume of rate limiting events"

# Repeated rate limiting from same IP
- alert: PossibleDDoS  
  expr: rate_limit_events_per_ip > 1000
  for: 10m
  labels:
    severity: critical
  annotations:
    summary: "Possible DDoS attack detected"
```

### **Health Check Integration**
Rate limiting status in health endpoint:

```json
GET /api/status
{
  "api": "online",
  "database": "connected", 
  "rate_limiting": {
    "enabled": true,
    "backend": "redis",
    "default_limit": "60/minute"
  }
}
```

---

**📊 Complete observability setup for production-ready monitoring!**