import { Page, expect, APIRequestContext, APIResponse } from '@playwright/test';
import { apiEndpoints } from '../fixtures/test-data';

export class RateLimitHelper {
  constructor(private page: Page, private request?: APIRequestContext) {}

  /**
   * Test rate limiting behavior for a specific endpoint
   * @param endpoint - API endpoint to test
   * @param method - HTTP method (GET, POST, etc.)
   * @param limit - Expected rate limit (number of requests)
   * @param timeWindow - Time window (e.g., 'minute', 'hour')
   * @param requestData - Data to send with request
   */
  async testRateLimit(
    endpoint: string, 
    method: 'GET' | 'POST' = 'GET',
    limit: number = 5,
    timeWindow: string = 'minute',
    requestData?: any
  ) {
    const responses: APIResponse[] = [];
    const baseUrl = 'http://localhost:8000';
    
    // Make requests up to the limit - should all return 200
    for (let i = 0; i < limit; i++) {
      const response = await this.makeRequest(baseUrl + endpoint, method, requestData);
      responses.push(response);
      
      // Small delay between requests to avoid overwhelming
      await this.page.waitForTimeout(100);
    }

    // Verify all requests within limit succeeded
    for (let i = 0; i < limit; i++) {
      expect(responses[i].status()).toBeLessThan(400);
    }

    // Make additional requests that should trigger rate limiting
    const exceededResponses: APIResponse[] = [];
    
    for (let i = 0; i < 3; i++) {
      const response = await this.makeRequest(baseUrl + endpoint, method, requestData);
      exceededResponses.push(response);
      await this.page.waitForTimeout(50);
    }

    // At least one request should return 429
    const rateLimitedResponses = exceededResponses.filter(r => r.status() === 429);
    expect(rateLimitedResponses.length).toBeGreaterThan(0);

    // Validate the structure of 429 responses
    for (const response of rateLimitedResponses) {
      await this.validateRateLimitResponse(response);
    }

    return { 
      successResponses: responses,
      rateLimitedResponses: rateLimitedResponses
    };
  }

  /**
   * Test rate limiting with Redis backend (when REDIS_URL is configured)
   */
  async testRedisRateLimit(endpoint: string, limit: number = 3) {
    // Flush any existing rate limit data
    await this.flushRedisKeys('test-redis');
    
    return await this.testRateLimit(endpoint, 'GET', limit, 'minute');
  }

  /**
   * Test rate limiting with in-memory backend (when Redis is not available)
   */
  async testInMemoryRateLimit(endpoint: string, limit: number = 3) {
    // For in-memory testing, we can't easily flush keys
    // So we use a different endpoint or wait for reset
    await this.page.waitForTimeout(1000);
    
    return await this.testRateLimit(endpoint, 'GET', limit, 'minute');
  }

  /**
   * Validate 429 response structure and headers
   */
  async validateRateLimitResponse(response: APIResponse) {
    expect(response.status()).toBe(429);
    
    // Check response body structure
    const body = await response.json();
    
    // Required fields in 429 response
    expect(body).toHaveProperty('error', 'Rate limit exceeded');
    expect(body).toHaveProperty('detail');
    expect(body).toHaveProperty('retry_after');
    expect(body).toHaveProperty('timestamp');
    expect(body).toHaveProperty('limit');
    expect(body).toHaveProperty('remaining', 0);
    expect(body).toHaveProperty('reset_time');
    expect(body).toHaveProperty('client_ip');

    // Check response headers
    const headers = response.headers();
    expect(headers).toHaveProperty('retry-after');
    expect(headers).toHaveProperty('x-ratelimit-limit');
    expect(headers).toHaveProperty('x-ratelimit-remaining', '0');
    expect(headers).toHaveProperty('x-ratelimit-reset');

    // Validate data types and formats
    expect(typeof body.retry_after).toBe('number');
    expect(body.retry_after).toBeGreaterThan(0);
    expect(body.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z$/);
    expect(body.reset_time).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z$/);
    
    return body;
  }

  /**
   * Helper to flush Redis keys for testing isolation
   */
  async flushRedisKeys(namespace: string = 'test'): Promise<void> {
    try {
      // Connect to Redis and flush test keys
      if (this.request) {
        // Use a custom endpoint that flushes Redis keys for testing
        // This would need to be implemented on the backend for testing
        await this.request.post('http://localhost:8000/_test/flush-rate-limits', {
          data: { namespace }
        });
      }
    } catch (error) {
      console.warn('Could not flush Redis keys:', error);
      // Continue with test - Redis may not be available
    }
  }

  /**
   * Wait for rate limit to reset
   */
  async waitForRateLimitReset(retryAfterSeconds: number): Promise<void> {
    // Add small buffer to ensure reset
    const waitTime = (retryAfterSeconds + 2) * 1000;
    await this.page.waitForTimeout(waitTime);
  }

  /**
   * Get rate limit status from API
   */
  async getRateLimitStatus(): Promise<any> {
    if (!this.request) return null;
    
    try {
      const response = await this.request.get('http://localhost:8000/_test/rate-limit-status');
      if (response.ok()) {
        return await response.json();
      }
    } catch (error) {
      console.warn('Could not get rate limit status:', error);
    }
    
    return null;
  }

  /**
   * Make HTTP request with proper error handling
   */
  private async makeRequest(
    url: string, 
    method: 'GET' | 'POST', 
    data?: any
  ): Promise<APIResponse> {
    if (!this.request) {
      throw new Error('APIRequestContext not provided');
    }

    try {
      switch (method) {
        case 'GET':
          return await this.request.get(url);
        case 'POST':
          return await this.request.post(url, { 
            data: data || {},
            headers: { 'Content-Type': 'application/json' }
          });
        default:
          throw new Error(`Unsupported HTTP method: ${method}`);
      }
    } catch (error) {
      console.error(`Request failed for ${method} ${url}:`, error);
      throw error;
    }
  }

  /**
   * Test authentication endpoint rate limiting
   */
  async testAuthRateLimit() {
    const loginData = {
      username: 'invalid@example.com',
      password: 'wrongpassword'
    };

    return await this.testRateLimit(
      apiEndpoints.auth.login,
      'POST',
      3, // AUTH rate limit
      'minute',
      loginData
    );
  }

  /**
   * Test analysis endpoint rate limiting
   */
  async testAnalysisRateLimit() {
    const analysisData = {
      text: 'Test speech for rate limiting',
      user_id: '123e4567-e89b-12d3-a456-426614174000',
      prompt_type: 'default'
    };

    return await this.testRateLimit(
      apiEndpoints.analysis.textAnalysis,
      'POST',
      5, // Analysis rate limit  
      'minute',
      analysisData
    );
  }

  /**
   * Test health endpoint (should have higher limits)
   */
  async testHealthRateLimit() {
    return await this.testRateLimit(
      apiEndpoints.health,
      'GET',
      50, // Health endpoint should have high limits
      'minute'
    );
  }
}