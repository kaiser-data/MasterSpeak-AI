# E2E Testing Dockerfile for MasterSpeak AI
FROM mcr.microsoft.com/playwright:v1.40.0-focal

WORKDIR /app

# Copy package files
COPY package.json ./
RUN npm install

# Install Playwright browsers
RUN npx playwright install

# Copy test files
COPY . .

# Create directories for reports
RUN mkdir -p test-results playwright-report

# Set environment
ENV CI=true
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Default command
CMD ["npx", "playwright", "test"]