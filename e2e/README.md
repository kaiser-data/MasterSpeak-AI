# 🧪 MasterSpeak AI - E2E Testing Documentation

## Overview

This directory contains the comprehensive end-to-end (E2E) testing suite for MasterSpeak AI. The testing infrastructure has been enhanced with advanced data management, security integration, and CI/CD automation.

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Test environment configured

### Running Tests

```bash
# Start all services and run E2E tests
docker compose -f docker-compose.e2e.yml up --build --abort-on-container-exit

# Run tests locally (services must be running)
cd e2e
npm install
npx playwright test

# Run specific test file
npx playwright test tests/auth.spec.ts

# Run tests with UI mode
npx playwright test --ui

# Generate and open HTML report
npx playwright show-report
```

## Architecture Overview

### 🏗️ Infrastructure Components

- **Docker Environment**: Multi-service orchestration with health checks
- **Playwright Framework**: Cross-browser testing with TypeScript
- **Test Data Management**: Advanced factories and data lifecycle management
- **CI/CD Integration**: GitHub Actions with security scanning
- **Health Monitoring**: Enhanced endpoints with DB/Redis connectivity

### 📁 Directory Structure

```
e2e/
├── tests/
│   ├── auth.spec.ts           # Authentication tests
│   ├── speech-analysis.spec.ts # Core functionality tests
│   ├── examples/              # Example test patterns
│   │   └── data-driven-auth.spec.ts
│   ├── factories/             # Test data generation
│   │   ├── user-factory.ts
│   │   └── speech-factory.ts
│   ├── helpers/               # Reusable test helpers
│   │   ├── auth-helper.ts
│   │   └── speech-helper.ts
│   └── utils/                 # Testing utilities
│       ├── test-setup.ts
│       ├── test-data-manager.ts
│       └── selectors.ts
├── playwright.config.ts       # Playwright configuration
├── Dockerfile                 # E2E test container
└── package.json              # Dependencies and scripts
```

## 🧪 Test Coverage

### Authentication Flow Tests
- ✅ Login with demo account
- ✅ Invalid credentials handling
- ✅ Logout functionality
- ✅ Session persistence
- ✅ Protected route access
- ✅ **NEW**: Advanced user factory testing
- ✅ **NEW**: Batch user scenarios
- ✅ **NEW**: Data-driven authentication patterns

### Speech Analysis Tests
- ✅ Text speech analysis
- ✅ Audio file upload and analysis
- ✅ Audio recording and analysis
- ✅ Error handling (invalid files, API errors)
- ✅ Complete user workflows
- ✅ **NEW**: Predefined speech content testing
- ✅ **NEW**: Performance scenario validation

### API Integration Tests
- ✅ Health endpoint verification
- ✅ Authentication API testing
- ✅ Speech analysis API testing
- ✅ Rate limiting validation
- ✅ CORS configuration testing
- ✅ **NEW**: Enhanced health checks (DB/Redis connectivity)
- ✅ **NEW**: Security endpoint validation

### Security Testing
- ✅ **NEW**: Input sanitization validation
- ✅ **NEW**: Authentication bypass protection
- ✅ **NEW**: Rate limiting enforcement
- ✅ **NEW**: CORS security validation

## 🎯 Test Data Management

### Advanced Factory System

Our factory system provides realistic, consistent test data for various scenarios:

```typescript
// Basic user creation
const user = UserFactory.createBasic();

// User with specific characteristics
const complexUser = UserFactory.createWithCharacteristics({
  emailLength: 'long',
  nameComplexity: 'international',
  passwordStrength: 'strong'
});

// Batch user creation
const users = UserFactory.createBatch(5, { domain: 'company.com' });

// Scenario-specific users
const newUser = UserFactory.createForScenario('new_user');
```

### Data Manager Integration

The `TestDataManager` handles complete test data lifecycle:

```typescript
// Initialize and seed database
const dataManager = new TestDataManager();
await dataManager.initialize();
const testData = await dataManager.seedDatabase();

// Create users and speeches via API
const user = await dataManager.createUser();
const speech = await dataManager.createSpeechAnalysis(user);

// Automatic cleanup
await dataManager.cleanup(); // Called automatically in fixtures
```

### Predefined Test Data

Ready-to-use speech content for different testing scenarios:

- **Professional Speeches**: Business presentations, formal addresses
- **Educational Content**: Training materials, academic speeches  
- **Performance Testing**: Large content samples
- **Edge Cases**: Unusual formatting, special characters

## 🔧 Writing Tests

### Test Setup and Fixtures

Our enhanced test setup provides powerful fixtures:

```typescript
import { test, expect } from '../utils/test-setup';

test('your test name', async ({ 
  page,           // Standard Playwright page
  dataManager,    // Test data management
  authHelper,     // Authentication utilities
  speechHelper,   // Speech analysis utilities
  testData,       // Pre-seeded test data
  demoUser,       // Demo user from test data
  authenticatedPage // Pre-authenticated page
}) => {
  // Your test logic here
});
```

### Example Test Patterns

#### Basic Authentication Test
```typescript
test('should login successfully', async ({ page, authHelper, demoUser }) => {
  await page.goto('/auth/signin');
  await authHelper.login('demo');
  await expect(page).toHaveURL('/dashboard');
});
```

#### Data-Driven Test
```typescript
test('should handle multiple user types', async ({ page, dataManager }) => {
  const users = UserFactory.createBatch(3);
  
  for (const user of users) {
    await dataManager.createUser(user);
    // Test logic for each user
  }
});
```

#### API + UI Integration
```typescript
test('should analyze speech end-to-end', async ({ 
  page, 
  dataManager, 
  speechHelper,
  demoUser 
}) => {
  // Create test data via API
  await dataManager.createUser(demoUser);
  
  // Test UI workflow
  await speechHelper.navigateToSpeechAnalysis();
  await speechHelper.analyzeSpeech(PredefinedSpeeches.professional);
  
  // Verify results
  await expect(page.locator('[data-testid="analysis-results"]')).toBeVisible();
});
```

### Test Helpers

#### AuthHelper
- `login(userType)` - Login with predefined users
- `logout()` - Logout current user
- `ensureLoggedOut()` - Ensure clean state

#### SpeechHelper
- `navigateToSpeechAnalysis()` - Navigate to analysis page
- `analyzeSpeech(content)` - Perform speech analysis
- `uploadFile(path)` - Upload speech file

## 🛡️ Security & Quality Integration

### Security Scanning Pipeline

Comprehensive security scanning integrated into CI/CD:

- **Dependency Scanning**: Safety (Python), npm audit (Node.js)
- **Container Security**: Trivy vulnerability scanning
- **Code Analysis**: CodeQL, Semgrep, Bandit
- **Secrets Detection**: TruffleHog, GitLeaks
- **Infrastructure**: Checkov, Hadolint

### Security Tests

```typescript
test('should reject malicious input', async ({ page }) => {
  const maliciousInput = '<script>alert("xss")</script>';
  await page.fill('[data-testid="speech-input"]', maliciousInput);
  
  // Should sanitize or reject
  await expect(page.locator('script')).toHaveCount(0);
});
```

### Quality Gates

- ✅ Syntax validation (language parsers)
- ✅ Type checking (TypeScript/Python)
- ✅ Linting (ESLint, Pylint)
- ✅ Security scanning (multiple tools)
- ✅ Test coverage (≥80% unit, ≥70% integration)
- ✅ Performance benchmarks
- ✅ Documentation completeness
- ✅ Integration testing

## 🚀 CI/CD Integration

### GitHub Actions Workflows

#### E2E Test Pipeline (`.github/workflows/e2e-tests.yml`)
- Multi-service Docker orchestration
- Health check validation
- Security pre-checks
- Test execution with retries
- Artifact collection (reports, logs, screenshots)

#### Security Scanning (`.github/workflows/security-scan.yml`)
- Weekly automated scans
- Dependency vulnerability assessment
- Container image security
- Code quality analysis
- Compliance checking

### Environment Configuration

```bash
# E2E Testing Environment (.env.e2e)
ENV=testing
DATABASE_URL=sqlite:////app/test_data/masterspeak_test.db
SECRET_KEY=test-secret-key-for-e2e-testing-only
HEALTHCHECK_DB=true
HEALTHCHECK_REDIS=true
RATE_LIMIT_ENABLED=true
```

## 📊 Test Reporting

### Playwright Reports

- **HTML Report**: Interactive test results with screenshots
- **JUnit XML**: CI/CD integration format
- **JSON**: Programmatic access to results

### Artifacts

- Test execution videos
- Failure screenshots
- Network logs
- Performance metrics
- Security scan reports

## 🔍 Debugging & Troubleshooting

### Common Issues

#### Playwright Installation
```bash
# Fix: Use Node.js base image, install dependencies
FROM node:18-bookworm
RUN npx playwright install --with-deps
```

#### Service Health Checks
```bash
# Check services are ready
curl http://localhost:8000/health
curl http://localhost:3000

# View service logs
docker compose -f docker-compose.e2e.yml logs backend
```

#### Test Data Issues
```bash
# Reset test database
docker compose -f docker-compose.e2e.yml exec backend python -m backend.seed_db

# Verify database state
npm run test:debug
```

### Debug Mode

```bash
# Run tests with debug output
DEBUG=true npx playwright test

# Run single test with UI
npx playwright test tests/auth.spec.ts --ui --debug

# Generate trace for failed tests
npx playwright test --trace on
```

### Performance Monitoring

```typescript
test('should load within performance budget', async ({ page }) => {
  const startTime = Date.now();
  await page.goto('/dashboard');
  const loadTime = Date.now() - startTime;
  
  expect(loadTime).toBeLessThan(3000); // 3 second budget
});
```

## 🏆 Best Practices

### Test Organization
- ✅ Group related tests in describe blocks
- ✅ Use descriptive test names
- ✅ Keep tests independent and atomic
- ✅ Use fixtures for common setup

### Data Management
- ✅ Use factories for test data generation
- ✅ Clean up test data after each test
- ✅ Use realistic data scenarios
- ✅ Avoid hardcoded test data

### Reliability
- ✅ Use explicit waits (`waitFor` methods)
- ✅ Handle async operations properly
- ✅ Implement retry logic for flaky operations
- ✅ Use data-testid attributes for stable selectors

### Performance
- ✅ Run tests in parallel when possible
- ✅ Use beforeEach/afterEach efficiently
- ✅ Minimize test data setup time
- ✅ Cache common resources

## 📈 Metrics & Monitoring

### Test Metrics
- Test execution time
- Pass/fail rates
- Coverage percentages
- Flakiness scores

### Performance Metrics
- Page load times
- API response times
- Memory usage
- Database query performance

### Security Metrics
- Vulnerability counts by severity
- Security scan compliance
- Dependency health scores
- Infrastructure security ratings

## 🔄 Maintenance

### Regular Tasks
- Update Playwright and dependencies monthly
- Review and update test data scenarios
- Monitor test execution performance
- Update security scanning configurations

### Scaling
- Add more test scenarios as features grow
- Implement parallel test execution optimization
- Consider test sharding for large suites
- Monitor resource usage and optimize

## 📚 Additional Resources

- [Playwright Documentation](https://playwright.dev/docs/intro)
- [Testing Best Practices](https://playwright.dev/docs/best-practices)
- [Docker Compose Guide](https://docs.docker.com/compose/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

## 🎯 Quick Reference

### Test Commands
```bash
# Full E2E test suite
docker compose -f docker-compose.e2e.yml up --build --abort-on-container-exit

# Development testing
npx playwright test --ui

# Specific browser
npx playwright test --project=chromium

# Generate report
npx playwright show-report

# Update snapshots
npx playwright test --update-snapshots
```

### Environment Variables
```bash
# Debug mode
DEBUG=true

# Headless mode
HEADLESS=false

# Slow motion
SLOW_MO=1000

# Video recording
ENABLE_VIDEO=true

# Screenshots
ENABLE_SCREENSHOTS=true
```

This comprehensive E2E testing suite provides robust, maintainable, and scalable test coverage for MasterSpeak AI with advanced data management, security integration, and CI/CD automation.