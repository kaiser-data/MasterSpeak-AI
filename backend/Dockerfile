FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

# Copy backend code directly to /app
COPY . .
ENV PYTHONPATH=/app

# HEALTHCHECK without curl/apt
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import os,sys,urllib.request; \
    url=f'http://127.0.0.1:{os.environ.get(\"PORT\",\"8000\")}/health'; \
    sys.exit(0) if urllib.request.urlopen(url, timeout=3).getcode()==200 else sys.exit(1)"

CMD ["sh","-c","python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]