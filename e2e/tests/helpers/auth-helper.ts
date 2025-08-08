import { Page, expect } from '@playwright/test';
import { testUsers, selectors } from '../fixtures/test-data';

export class AuthHelper {
  constructor(private page: Page) {}

  async login(userType: keyof typeof testUsers = 'demo') {
    const user = testUsers[userType];
    
    await this.page.goto('/auth/signin');
    await expect(this.page).toHaveTitle(/Sign In/);
    
    // Fill login form
    await this.page.fill(selectors.auth.emailInput, user.email);
    await this.page.fill(selectors.auth.passwordInput, user.password);
    
    // Submit form and wait for navigation
    await Promise.all([
      this.page.waitForURL('/dashboard'),
      this.page.click(selectors.auth.loginButton)
    ]);
    
    // Verify successful login
    await expect(this.page.locator(selectors.dashboard.welcomeMessage)).toBeVisible();
    
    return user;
  }

  async logout() {
    // Check if logout button is visible (user is logged in)
    const logoutButton = this.page.locator(selectors.navigation.logoutButton);
    if (await logoutButton.isVisible()) {
      await logoutButton.click();
      await this.page.waitForURL('/');
    }
  }

  async register(userData: { email: string; password: string; fullName: string }) {
    await this.page.goto('/auth/signup');
    await expect(this.page).toHaveTitle(/Sign Up/);
    
    // Fill registration form
    await this.page.fill('[name="fullName"]', userData.fullName);
    await this.page.fill(selectors.auth.emailInput, userData.email);
    await this.page.fill(selectors.auth.passwordInput, userData.password);
    await this.page.fill('[name="confirmPassword"]', userData.password);
    
    // Submit form
    await this.page.click(selectors.auth.signupButton);
    
    // Wait for success or error
    await this.page.waitForTimeout(2000);
  }

  async ensureLoggedOut() {
    await this.logout();
    
    // Verify we're on home page or auth page
    const currentUrl = this.page.url();
    if (!currentUrl.includes('/auth') && !currentUrl.endsWith('/')) {
      await this.page.goto('/');
    }
  }

  async ensureLoggedIn(userType: keyof typeof testUsers = 'demo') {
    // Check if already logged in by looking for dashboard elements
    try {
      await this.page.goto('/dashboard', { timeout: 5000 });
      await expect(this.page.locator(selectors.dashboard.welcomeMessage)).toBeVisible({ timeout: 3000 });
      return testUsers[userType]; // Already logged in
    } catch {
      // Not logged in, perform login
      return await this.login(userType);
    }
  }
}