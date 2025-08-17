# E2E Testing Dockerfile for MasterSpeak AI
# Using standard Node.js image with proper Playwright installation
FROM node:18-bookworm

WORKDIR /app

# Install system dependencies for Playwright browsers
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy package files first for better layer caching
COPY package.json ./

# Install npm dependencies including Playwright
RUN npm install

# Install Playwright browsers
RUN npx playwright install --with-deps

# Copy test configuration
COPY playwright.config.ts ./

# Copy test files
COPY tests/ ./tests/

# Create directories for reports
RUN mkdir -p test-results playwright-report

# Set environment variables
ENV CI=true

# Default command
CMD ["npx", "playwright", "test", "--reporter=html,json"]