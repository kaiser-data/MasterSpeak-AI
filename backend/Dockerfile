FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# Install deps from backend/requirements.txt (must live next to this Dockerfile)
COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy backend code, preserve package structure
COPY . ./backend

# Set Python path
ENV PYTHONPATH=/app

# Healthcheck using Railway's $PORT
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:' + __import__('os').environ.get('PORT', '8000') + '/health')" || exit 1

# Start uvicorn on $PORT
CMD ["sh", "-c", "python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]