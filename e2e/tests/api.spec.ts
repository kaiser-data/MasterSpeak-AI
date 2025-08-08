import { test, expect } from '@playwright/test';
import { apiEndpoints, testUsers } from './fixtures/test-data';

test.describe('API Integration Tests', () => {
  let authToken: string;

  test.beforeAll(async ({ request }) => {
    // Login to get auth token
    const loginResponse = await request.post(`http://localhost:8000${apiEndpoints.auth.login}`, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      form: {
        username: testUsers.demo.email,
        password: testUsers.demo.password,
      },
    });

    expect(loginResponse.ok()).toBeTruthy();
    const loginData = await loginResponse.json();
    authToken = loginData.access_token;
    expect(authToken).toBeDefined();
  });

  test('should check API health', async ({ request }) => {
    const response = await request.get('http://localhost:8000/health');
    
    expect(response.ok()).toBeTruthy();
    
    const healthData = await response.json();
    expect(healthData.status).toBe('healthy');
    expect(healthData.service).toBe('MasterSpeak AI');
  });

  test('should authenticate user via API', async ({ request }) => {
    const response = await request.get(`http://localhost:8000${apiEndpoints.auth.me}`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    expect(response.ok()).toBeTruthy();
    
    const userData = await response.json();
    expect(userData.email).toBe(testUsers.demo.email);
    expect(userData.is_active).toBe(true);
  });

  test('should handle text analysis via API', async ({ request }) => {
    const analysisResponse = await request.post(`http://localhost:8000${apiEndpoints.analysis.textAnalysis}`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      data: {
        text: 'This is a test speech for analysis. I am speaking clearly and slowly.',
        language: 'en',
      },
    });

    expect(analysisResponse.ok()).toBeTruthy();
    
    const analysisData = await analysisResponse.json();
    expect(analysisData).toHaveProperty('clarity_score');
    expect(analysisData).toHaveProperty('confidence_score');
    expect(analysisData).toHaveProperty('suggestions');
  });

  test('should handle rate limiting correctly', async ({ request }) => {
    // Make multiple rapid requests to test rate limiting
    const requests = [];
    
    for (let i = 0; i < 10; i++) {
      requests.push(
        request.get('http://localhost:8000/health')
      );
    }

    const responses = await Promise.all(requests);
    
    // All requests should succeed (health endpoint has high limits)
    responses.forEach(response => {
      expect(response.status()).toBeLessThan(500);
    });
  });

  test('should return 401 for unauthorized requests', async ({ request }) => {
    const response = await request.get(`http://localhost:8000${apiEndpoints.auth.me}`);
    
    expect(response.status()).toBe(401);
  });

  test('should validate request data', async ({ request }) => {
    // Send invalid data to text analysis endpoint
    const response = await request.post(`http://localhost:8000${apiEndpoints.analysis.textAnalysis}`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      data: {
        // Missing required 'text' field
        language: 'en',
      },
    });

    expect(response.status()).toBe(422); // Validation error
    
    const errorData = await response.json();
    expect(errorData).toHaveProperty('detail');
  });

  test('should handle CORS correctly', async ({ request }) => {
    const response = await request.options('http://localhost:8000/health', {
      headers: {
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'GET',
      },
    });

    expect(response.ok()).toBeTruthy();
    expect(response.headers()['access-control-allow-origin']).toBeTruthy();
  });
});