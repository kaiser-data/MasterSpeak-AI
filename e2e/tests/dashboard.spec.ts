import { test, expect } from '@playwright/test';
import { AuthHelper } from './helpers/auth-helper';
import { selectors } from './fixtures/test-data';

test.describe('Dashboard Functionality', () => {
  let authHelper: AuthHelper;

  test.beforeEach(async ({ page }) => {
    authHelper = new AuthHelper(page);
    await authHelper.ensureLoggedIn('demo');
  });

  test('should display dashboard correctly after login', async ({ page }) => {
    await expect(page).toHaveURL('/dashboard');
    await expect(page).toHaveTitle(/Dashboard/);
    
    // Check for main dashboard elements
    await expect(page.locator(selectors.dashboard.welcomeMessage)).toBeVisible();
    await expect(page.locator(selectors.dashboard.analysisCard)).toBeVisible();
  });

  test('should have working navigation links', async ({ page }) => {
    // Test navigation to different sections
    await page.click(selectors.navigation.profileLink);
    await expect(page).toHaveURL(/profile/);
    
    // Navigate back to dashboard
    await page.click(selectors.navigation.dashboardLink);
    await expect(page).toHaveURL('/dashboard');
  });

  test('should show analysis options', async ({ page }) => {
    // Check for analysis options
    await expect(page.locator(selectors.dashboard.textAnalysisButton)).toBeVisible();
    await expect(page.locator(selectors.dashboard.uploadButton)).toBeVisible();
    await expect(page.locator(selectors.dashboard.recordButton)).toBeVisible();
  });

  test('should navigate to speech analysis from dashboard', async ({ page }) => {
    await page.click(selectors.dashboard.textAnalysisButton);
    
    // Should navigate to speech analysis page
    await expect(page).toHaveURL(/speech-analysis/);
    await expect(page.locator(selectors.speechAnalysis.textInput)).toBeVisible();
  });

  test('should show user information', async ({ page }) => {
    // Check for user-specific information
    await expect(page.getByText('demo@masterspeak.ai')).toBeVisible();
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Test mobile responsiveness
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Dashboard should still be accessible
    await expect(page.locator(selectors.dashboard.welcomeMessage)).toBeVisible();
    await expect(page.locator(selectors.dashboard.analysisCard)).toBeVisible();
  });
});