FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# Cache busting argument
ARG CACHE_BUST=2
ENV CACHE_BUST=$CACHE_BUST

COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

# Force rebuild - copy backend code
COPY . ./backend
ENV PYTHONPATH=/app

# Simple healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import os,sys,urllib.request; url=f'http://127.0.0.1:{os.environ.get('PORT','8000')}/health'; \
                 sys.exit(0) if urllib.request.urlopen(url, timeout=3).getcode()==200 else sys.exit(1)"

# Start uvicorn with proxy headers for Railway
CMD ["sh","-c","python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]