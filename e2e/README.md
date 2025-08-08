# MasterSpeak AI - E2E Testing

Comprehensive end-to-end testing suite using Playwright for the MasterSpeak AI application.

## 🧪 Test Coverage

### Authentication Flow Tests
- ✅ Login with demo account
- ✅ Invalid credentials handling
- ✅ Logout functionality
- ✅ Session persistence
- ✅ Protected route access

### Speech Analysis Tests
- ✅ Text speech analysis
- ✅ Audio file upload and analysis
- ✅ Audio recording and analysis
- ✅ Error handling (invalid files, API errors)
- ✅ Complete user workflows

### Dashboard Tests
- ✅ Dashboard display and navigation
- ✅ Analysis options availability
- ✅ Mobile responsiveness
- ✅ User information display

### API Integration Tests
- ✅ Health endpoint verification
- ✅ Authentication API testing
- ✅ Speech analysis API testing
- ✅ Rate limiting validation
- ✅ CORS configuration testing

## 🚀 Running Tests

### Local Development
```bash
cd e2e
npm install
npx playwright install
npm test
```

### With Docker Compose
```bash
docker-compose -f docker-compose.e2e.yml up --build
```

### CI/CD Pipeline
Tests run automatically on push/PR via GitHub Actions with HTML report generation.

## 📊 Test Reports

### HTML Report
After test execution, view the interactive HTML report:
```bash
npx playwright show-report
```

### JSON Results
Test results are also available in JSON format for CI integration:
- `test-results.json` - Detailed test results
- `test-results.xml` - JUnit format for CI systems

## 🏗️ Test Architecture

### Helper Classes
- **AuthHelper**: Authentication flow management
- **SpeechHelper**: Speech analysis workflow automation

### Test Fixtures
- **test-data.ts**: Test users, audio samples, API endpoints
- **audio/**: Test audio files for upload testing

### Page Object Model
Tests use a Page Object Model pattern with:
- Centralized selectors in `test-data.ts`
- Reusable helper methods
- Clear separation of test logic and page interaction

## 🔧 Configuration

### Playwright Config
- **Multi-browser testing**: Chrome, Firefox, Safari, Mobile Chrome
- **Parallel execution**: Tests run in parallel for speed
- **Retry logic**: Automatic retries on failure (CI: 2 retries)
- **Screenshots/Videos**: Captured on failure for debugging

### Docker Setup
- **Backend**: FastAPI with test database
- **Frontend**: Next.js in development mode
- **Redis**: For rate limiting and caching tests
- **E2E Runner**: Playwright in headless mode

## 📝 Test Scenarios

### Complete User Journeys
1. **Login → Upload → Analyze → Results**
2. **Login → Text Input → Analyze → Results**  
3. **Login → Record → Analyze → Results**

### Error Handling
- Network timeouts
- API failures
- Invalid file formats
- Microphone permission denial
- Rate limiting responses

### Performance Testing
- Response time validation
- Large file upload handling
- Concurrent user simulation

## 🔍 Debugging Tests

### Local Debugging
```bash
# Run tests in headed mode
npm run test:headed

# Debug specific test
npx playwright test --debug auth.spec.ts

# Interactive UI mode
npm run test:ui
```

### CI Debugging
- Check uploaded artifacts in GitHub Actions
- Review service logs for backend/frontend issues
- Examine screenshots and videos from failed tests

## 🛡️ Test Data Management

### Security
- Uses demo accounts with known credentials
- Test data is isolated from production
- Secrets are managed via environment variables

### Data Cleanup
- Each test runs in isolation
- Database resets between test suites
- Temporary files are cleaned up automatically

## 📈 Metrics & Reporting

### Success Metrics
- Test pass rate: Target 95%+
- Test execution time: <10 minutes
- Browser compatibility: Chrome, Firefox, Safari, Mobile

### Failure Analysis
- Automatic retry on transient failures
- Detailed error reporting with context
- Screenshot and video capture for investigation

## 🔄 Continuous Integration

### GitHub Actions Integration
- Runs on every push and PR
- Multi-browser parallel execution
- Artifact collection (reports, logs, screenshots)
- Slack/email notifications on failure

### Performance Optimization
- Docker layer caching
- Parallel test execution
- Service health checks
- Smart retry logic