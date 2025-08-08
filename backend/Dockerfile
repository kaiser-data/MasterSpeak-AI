FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
# Keep backend as a package path under /app/backend
COPY . ./backend
ENV PYTHONPATH=/app
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -fsSL http://127.0.0.1:${PORT:-8000}/health || exit 1
CMD ["sh","-c","python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]