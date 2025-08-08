import { test, expect } from '@playwright/test';
import { AuthHelper } from './helpers/auth-helper';
import { testUsers, selectors } from './fixtures/test-data';

test.describe('Authentication Flow', () => {
  let authHelper: AuthHelper;

  test.beforeEach(async ({ page }) => {
    authHelper = new AuthHelper(page);
    await authHelper.ensureLoggedOut();
  });

  test('should display login page correctly', async ({ page }) => {
    await page.goto('/auth/signin');
    
    await expect(page).toHaveTitle(/Sign In/);
    await expect(page.locator(selectors.auth.emailInput)).toBeVisible();
    await expect(page.locator(selectors.auth.passwordInput)).toBeVisible();
    await expect(page.locator(selectors.auth.loginButton)).toBeVisible();
  });

  test('should login with demo account', async ({ page }) => {
    const user = await authHelper.login('demo');
    
    // Verify successful login
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator(selectors.dashboard.welcomeMessage)).toBeVisible();
    
    // Verify user info is displayed
    await expect(page.getByText(user.email)).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/auth/signin');
    
    await page.fill(selectors.auth.emailInput, 'invalid@example.com');
    await page.fill(selectors.auth.passwordInput, 'wrongpassword');
    await page.click(selectors.auth.loginButton);
    
    // Should stay on login page and show error
    await expect(page).toHaveURL('/auth/signin');
    await expect(page.locator(selectors.auth.errorMessage)).toBeVisible();
  });

  test('should logout successfully', async ({ page }) => {
    // First login
    await authHelper.login('demo');
    await expect(page).toHaveURL('/dashboard');
    
    // Then logout
    await authHelper.logout();
    await expect(page).toHaveURL('/');
  });

  test('should redirect to login when accessing protected route', async ({ page }) => {
    // Try to access dashboard without login
    await page.goto('/dashboard');
    
    // Should redirect to login
    await expect(page).toHaveURL('/auth/signin');
  });

  test('should maintain session across page refreshes', async ({ page }) => {
    await authHelper.login('demo');
    await expect(page).toHaveURL('/dashboard');
    
    // Refresh page
    await page.reload();
    
    // Should still be logged in
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator(selectors.dashboard.welcomeMessage)).toBeVisible();
  });

  test('should navigate between auth pages', async ({ page }) => {
    await page.goto('/auth/signin');
    
    // Go to signup
    await page.click('text=Sign Up');
    await expect(page).toHaveURL('/auth/signup');
    await expect(page).toHaveTitle(/Sign Up/);
    
    // Go back to signin
    await page.click('text=Sign In');
    await expect(page).toHaveURL('/auth/signin');
    await expect(page).toHaveTitle(/Sign In/);
  });
});