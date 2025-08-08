# Railway-optimized Dockerfile for MasterSpeak AI Backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal for Railway memory limits)
RUN apt-get update && apt-get install -y \
    curl \
    --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies (memory optimized)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

# Copy entire backend directory
COPY backend/ .

# Create necessary directories
RUN mkdir -p data

# Copy Railway-specific environment defaults
COPY .env.railway .env

# Set Python path for proper module imports
ENV PYTHONPATH=/app

# Railway uses PORT environment variable
ENV PORT=8000

# Ensure startup script is executable
RUN chmod +x railway-start.py

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:$PORT/health || exit 1

# Start application with Railway initialization
CMD ["python", "railway-start.py"]