/**
 * Test Setup Utilities for E2E Tests
 * Provides setup, teardown, and common utilities for Playwright tests
 */

import { test as base, Page, BrowserContext } from '@playwright/test';
import { TestDataManager, TestDataSnapshot } from './test-data-manager';
import { AuthHelper } from '../helpers/auth-helper';
import { SpeechHelper } from '../helpers/speech-helper';
import { TestUser } from '../factories/user-factory';

// Extend Playwright test with our custom fixtures
type TestFixtures = {
  dataManager: TestDataManager;
  authHelper: AuthHelper;
  speechHelper: SpeechHelper;
  testData: TestDataSnapshot;
  authenticatedPage: Page;
  demoUser: TestUser;
  testUser: TestUser;
};

/**
 * Custom test with data management fixtures
 */
export const test = base.extend<TestFixtures>({
  // Test Data Manager fixture
  dataManager: async ({ page }, use) => {
    const manager = new TestDataManager();
    await manager.initialize();
    await use(manager);
    await manager.cleanup();
    await manager.dispose();
  },

  // Auth Helper fixture
  authHelper: async ({ page }, use) => {
    const helper = new AuthHelper(page);
    await use(helper);
  },

  // Speech Helper fixture
  speechHelper: async ({ page }, use) => {
    const helper = new SpeechHelper(page);
    await use(helper);
  },

  // Test data fixture - seeds database with basic test data
  testData: async ({ dataManager }, use) => {
    const data = await dataManager.seedDatabase();
    await use(data);
    // Cleanup is handled by dataManager fixture
  },

  // Pre-authenticated page fixture for tests that need a logged-in user
  authenticatedPage: async ({ page, authHelper, testData }, use) => {
    await authHelper.login('demo');
    await use(page);
  },

  // Demo user fixture
  demoUser: async ({ testData }, use) => {
    const demoUser = testData.users.find(u => u.email === 'demo@masterspeak.ai');
    if (!demoUser) {
      throw new Error('Demo user not found in test data');
    }
    await use(demoUser);
  },

  // Test user fixture
  testUser: async ({ testData }, use) => {
    const testUser = testData.users.find(u => u.email === 'test@playwright.com');
    if (!testUser) {
      throw new Error('Test user not found in test data');
    }
    await use(testUser);
  }
});

export { expect } from '@playwright/test';

/**
 * Test suite setup utilities
 */
export class TestSuite {
  
  /**
   * Setup for test suite that needs clean database
   */
  static async setupClean(dataManager: TestDataManager): Promise<void> {
    await dataManager.resetDatabase();
    const state = await dataManager.verifyDatabaseState();
    if (!state.healthy) {
      console.warn('Database health issues detected:', state.issues);
    }
  }
  
  /**
   * Setup for test suite that needs seeded database
   */
  static async setupSeeded(dataManager: TestDataManager): Promise<TestDataSnapshot> {
    await dataManager.resetDatabase();
    return await dataManager.seedDatabase();
  }
  
  /**
   * Setup for performance/stress testing
   */
  static async setupStress(dataManager: TestDataManager): Promise<TestDataSnapshot> {
    await dataManager.resetDatabase();
    return await dataManager.createScenarioData('stress');
  }
  
  /**
   * Verify test environment is ready
   */
  static async verifyEnvironment(baseURL: string = 'http://localhost:3000'): Promise<{
    ready: boolean;
    issues: string[];
  }> {
    const issues: string[] = [];
    
    try {
      // Check frontend
      const frontendResponse = await fetch(baseURL);
      if (!frontendResponse.ok) {
        issues.push(`Frontend not responding: ${frontendResponse.status}`);
      }
    } catch (error) {
      issues.push(`Frontend connection failed: ${error}`);
    }
    
    try {
      // Check backend
      const backendResponse = await fetch(baseURL.replace('3000', '8000') + '/health');
      if (!backendResponse.ok) {
        issues.push(`Backend health check failed: ${backendResponse.status}`);
      } else {
        const health = await backendResponse.json();
        if (health.status !== 'ok') {
          issues.push(`Backend status: ${health.status}`);
        }
      }
    } catch (error) {
      issues.push(`Backend connection failed: ${error}`);
    }
    
    return {
      ready: issues.length === 0,
      issues
    };
  }
  
  /**
   * Wait for services to be ready
   */
  static async waitForServices(
    maxWaitTime: number = 60000,
    baseURL: string = 'http://localhost:3000'
  ): Promise<boolean> {
    const startTime = Date.now();
    
    while (Date.now() - startTime < maxWaitTime) {
      const status = await this.verifyEnvironment(baseURL);
      if (status.ready) {
        return true;
      }
      
      console.log('Waiting for services...', status.issues);
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    return false;
  }
}

/**
 * Common test utilities
 */
export class TestUtils {
  
  /**
   * Take a screenshot with timestamp
   */
  static async takeTimestampedScreenshot(
    page: Page, 
    name: string
  ): Promise<string> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${name}-${timestamp}.png`;
    await page.screenshot({ path: `test-results/${filename}`, fullPage: true });
    return filename;
  }
  
  /**
   * Wait for network to be idle
   */
  static async waitForNetworkIdle(page: Page, timeout: number = 5000): Promise<void> {
    await page.waitForLoadState('networkidle', { timeout });
  }
  
  /**
   * Clear browser storage
   */
  static async clearStorage(context: BrowserContext): Promise<void> {
    await context.clearCookies();
    await context.clearPermissions();
    
    // Clear localStorage and sessionStorage for all pages
    const pages = context.pages();
    for (const page of pages) {
      await page.evaluate(() => {
        localStorage.clear();
        sessionStorage.clear();
      });
    }
  }
  
  /**
   * Mock API response
   */
  static async mockApiResponse(
    page: Page,
    endpoint: string,
    response: any,
    status: number = 200
  ): Promise<void> {
    await page.route(`**${endpoint}`, route => {
      route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify(response)
      });
    });
  }
  
  /**
   * Wait for element with retry
   */
  static async waitForElementWithRetry(
    page: Page,
    selector: string,
    maxRetries: number = 3,
    timeout: number = 5000
  ): Promise<boolean> {
    for (let i = 0; i < maxRetries; i++) {
      try {
        await page.waitForSelector(selector, { timeout });
        return true;
      } catch (error) {
        if (i === maxRetries - 1) {
          console.error(`Element ${selector} not found after ${maxRetries} retries`);
          return false;
        }
        await page.waitForTimeout(1000);
      }
    }
    return false;
  }
  
  /**
   * Generate unique test ID
   */
  static generateTestId(prefix: string = 'test'): string {
    return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
  
  /**
   * Log test step for debugging
   */
  static logStep(step: string, data?: any): void {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${step}`, data ? JSON.stringify(data, null, 2) : '');
  }
}

/**
 * Environment configuration
 */
export const TestConfig = {
  // Timeouts
  DEFAULT_TIMEOUT: 30000,
  NETWORK_TIMEOUT: 60000,
  NAVIGATION_TIMEOUT: 30000,
  
  // URLs
  FRONTEND_URL: process.env.FRONTEND_URL || 'http://localhost:3000',
  BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:8000',
  
  // Test data
  TEST_DATA_PATH: process.env.TEST_DATA_PATH || './test_data',
  
  // Feature flags
  ENABLE_SCREENSHOTS: process.env.ENABLE_SCREENSHOTS !== 'false',
  ENABLE_VIDEO: process.env.ENABLE_VIDEO !== 'false',
  ENABLE_TRACE: process.env.ENABLE_TRACE !== 'false',
  
  // Performance
  MAX_CONCURRENT_TESTS: parseInt(process.env.MAX_CONCURRENT_TESTS || '3'),
  
  // Debugging
  DEBUG_MODE: process.env.DEBUG === 'true',
  SLOW_MO: parseInt(process.env.SLOW_MO || '0')
} as const;