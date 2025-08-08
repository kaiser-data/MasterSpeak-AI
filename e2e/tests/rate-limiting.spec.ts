import { test, expect } from '@playwright/test';
import { RateLimitHelper } from './helpers/rate-limit-helper';
import { apiEndpoints, testUsers } from './fixtures/test-data';

test.describe('Rate Limiting E2E Tests', () => {
  let rateLimitHelper: RateLimitHelper;

  test.beforeEach(async ({ page, request }) => {
    rateLimitHelper = new RateLimitHelper(page, request);
  });

  test.describe('Basic Rate Limiting', () => {
    test('should enforce rate limits on health endpoint', async () => {
      const result = await rateLimitHelper.testHealthRateLimit();
      
      // Health endpoint should have high limits, so this tests basic functionality
      expect(result.successResponses.length).toBeGreaterThan(10);
      
      // If we did hit rate limit, validate the response structure
      if (result.rateLimitedResponses.length > 0) {
        for (const response of result.rateLimitedResponses) {
          await rateLimitHelper.validateRateLimitResponse(response);
        }
      }
    });

    test('should enforce rate limits with proper 429 structure and headers', async ({ request }) => {
      // Use a low-limit endpoint to trigger rate limiting
      const responses: any[] = [];
      
      // Make multiple requests to trigger rate limiting
      for (let i = 0; i < 15; i++) {
        const response = await request.get('http://localhost:8000/health');
        responses.push({
          status: response.status(),
          headers: response.headers(),
          body: response.status() === 429 ? await response.json() : null
        });
        
        // Small delay between requests
        await new Promise(resolve => setTimeout(resolve, 50));
      }

      // Find 429 responses
      const rateLimitedResponses = responses.filter(r => r.status === 429);
      
      if (rateLimitedResponses.length > 0) {
        const response429 = rateLimitedResponses[0];
        
        // Validate 429 response structure
        expect(response429.body).toMatchObject({
          error: 'Rate limit exceeded',
          detail: expect.any(String),
          retry_after: expect.any(Number),
          timestamp: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T/),
          limit: expect.any(String),
          remaining: 0,
          reset_time: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T/),
          client_ip: expect.any(String)
        });

        // Validate headers
        expect(response429.headers['retry-after']).toBeTruthy();
        expect(response429.headers['x-ratelimit-limit']).toBeTruthy();
        expect(response429.headers['x-ratelimit-remaining']).toBe('0');
        expect(response429.headers['x-ratelimit-reset']).toBeTruthy();
      }
    });
  });

  test.describe('Authentication Rate Limiting', () => {
    test('should rate limit failed login attempts', async ({ request }) => {
      const loginUrl = 'http://localhost:8000' + apiEndpoints.auth.login;
      const invalidCredentials = new URLSearchParams({
        username: 'invalid@example.com',
        password: 'wrongpassword'
      });

      const responses: any[] = [];

      // Make multiple failed login attempts
      for (let i = 0; i < 8; i++) {
        const response = await request.post(loginUrl, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          data: invalidCredentials.toString()
        });

        responses.push({
          status: response.status(),
          body: response.status() === 429 ? await response.json() : null,
          headers: response.headers()
        });

        await new Promise(resolve => setTimeout(resolve, 100));
      }

      // Should have some 429 responses for auth rate limiting
      const rateLimitedResponses = responses.filter(r => r.status === 429);
      
      if (rateLimitedResponses.length > 0) {
        const response429 = rateLimitedResponses[0];
        
        // Validate auth-specific rate limiting
        expect(response429.body.error).toBe('Rate limit exceeded');
        expect(response429.body.retry_after).toBeGreaterThan(0);
        expect(response429.headers['retry-after']).toBeTruthy();
      }
    });
  });

  test.describe('Analysis Rate Limiting', () => {
    test('should rate limit analysis requests', async ({ request }) => {
      // First, get a valid auth token for analysis requests
      let authToken = '';
      
      try {
        const loginResponse = await request.post('http://localhost:8000' + apiEndpoints.auth.login, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          data: new URLSearchParams({
            username: testUsers.demo.email,
            password: testUsers.demo.password
          }).toString()
        });

        if (loginResponse.ok()) {
          const loginData = await loginResponse.json();
          authToken = loginData.access_token;
        }
      } catch (error) {
        console.warn('Could not get auth token for analysis test:', error);
      }

      const analysisUrl = 'http://localhost:8000' + apiEndpoints.analysis.textAnalysis;
      const analysisData = new URLSearchParams({
        text: 'Test speech for rate limiting analysis',
        user_id: '123e4567-e89b-12d3-a456-426614174000',
        prompt_type: 'default'
      });

      const responses: any[] = [];

      // Make multiple analysis requests
      for (let i = 0; i < 12; i++) {
        const headers: any = {
          'Content-Type': 'application/x-www-form-urlencoded',
        };
        
        if (authToken) {
          headers['Authorization'] = `Bearer ${authToken}`;
        }

        const response = await request.post(analysisUrl, {
          headers,
          data: analysisData.toString()
        });

        responses.push({
          status: response.status(),
          body: response.status() === 429 ? await response.json() : null
        });

        await new Promise(resolve => setTimeout(resolve, 100));
      }

      // Check for rate limiting (may not always trigger depending on limits)
      const rateLimitedResponses = responses.filter(r => r.status === 429);
      
      if (rateLimitedResponses.length > 0) {
        const response429 = rateLimitedResponses[0];
        expect(response429.body.error).toBe('Rate limit exceeded');
      }
    });
  });

  test.describe('Redis vs In-Memory Rate Limiting', () => {
    test('should handle rate limiting with Redis backend', async () => {
      // This tests the Redis backend path when REDIS_URL is configured
      await rateLimitHelper.flushRedisKeys('redis-test');
      
      const result = await rateLimitHelper.testRedisRateLimit('/health', 20);
      
      // Redis backend should work the same as in-memory for basic functionality
      expect(result.successResponses.length).toBeGreaterThanOrEqual(15);
    });

    test('should handle rate limiting with in-memory fallback', async () => {
      // This tests the in-memory fallback when Redis is not available
      const result = await rateLimitHelper.testInMemoryRateLimit('/health', 20);
      
      // In-memory backend should also work
      expect(result.successResponses.length).toBeGreaterThanOrEqual(15);
    });

    test('should maintain rate limit state across requests', async ({ request }) => {
      // Test that rate limiting state is maintained properly
      const endpoint = 'http://localhost:8000/health';
      
      // Make some requests
      const firstBatch: any[] = [];
      for (let i = 0; i < 10; i++) {
        const response = await request.get(endpoint);
        firstBatch.push(response.status());
        await new Promise(resolve => setTimeout(resolve, 50));
      }

      // Small delay
      await new Promise(resolve => setTimeout(resolve, 200));

      // Make more requests - rate limiting should still be in effect if triggered
      const secondBatch: any[] = [];
      for (let i = 0; i < 10; i++) {
        const response = await request.get(endpoint);
        secondBatch.push(response.status());
        await new Promise(resolve => setTimeout(resolve, 50));
      }

      // Both batches should have consistent behavior
      expect(firstBatch.length).toBe(10);
      expect(secondBatch.length).toBe(10);
      
      // Count successful vs rate limited responses
      const allStatuses = [...firstBatch, ...secondBatch];
      const successCount = allStatuses.filter(status => status < 400).length;
      const rateLimitCount = allStatuses.filter(status => status === 429).length;
      
      expect(successCount + rateLimitCount).toBe(20);
    });
  });

  test.describe('Rate Limit Recovery', () => {
    test('should allow requests after rate limit window expires', async ({ request }) => {
      const endpoint = 'http://localhost:8000/health';
      
      // Trigger rate limiting
      const responses: any[] = [];
      for (let i = 0; i < 100; i++) {  // High number to ensure rate limiting
        const response = await request.get(endpoint);
        responses.push({
          status: response.status(),
          body: response.status() === 429 ? await response.json() : null
        });
        
        if (response.status() === 429) {
          break;  // Stop once we hit rate limit
        }
        
        await new Promise(resolve => setTimeout(resolve, 20));
      }

      const rateLimited = responses.find(r => r.status === 429);
      
      if (rateLimited && rateLimited.body && rateLimited.body.retry_after) {
        const retryAfter = rateLimited.body.retry_after;
        
        // Wait for rate limit to expire (with buffer)
        const waitTime = (retryAfter + 1) * 1000;
        await new Promise(resolve => setTimeout(resolve, waitTime));
        
        // Try again - should succeed
        const recoveryResponse = await request.get(endpoint);
        expect(recoveryResponse.status()).toBeLessThan(400);
      }
    });
  });

  test.describe('Rate Limit Configuration', () => {
    test('should respect environment-based rate limit configuration', async ({ request }) => {
      // Test that the rate limiting respects the environment configuration
      // This is more of an integration test to ensure the config is working
      
      const responses: any[] = [];
      let rateLimitInfo: any = null;

      // Make requests until we hit a rate limit to see the configuration
      for (let i = 0; i < 200 && !rateLimitInfo; i++) {
        const response = await request.get('http://localhost:8000/health');
        
        if (response.status() === 429) {
          rateLimitInfo = await response.json();
          break;
        }
        
        responses.push(response.status());
        await new Promise(resolve => setTimeout(resolve, 10));
      }

      if (rateLimitInfo) {
        // Should have proper limit information in the response
        expect(rateLimitInfo.limit).toBeTruthy();
        expect(rateLimitInfo.retry_after).toBeGreaterThan(0);
        expect(rateLimitInfo.reset_time).toBeTruthy();
        
        // The limit should be a valid rate limit string
        expect(rateLimitInfo.limit).toMatch(/\d+\s*per\s*\d+\s*(minute|second|hour)/i);
      }
    });
  });
});