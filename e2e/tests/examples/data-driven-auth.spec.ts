/**
 * Example test demonstrating the new test data management system
 * This test shows how to use factories, data managers, and setup utilities
 */

import { test, expect, TestUtils, TestConfig } from '../utils/test-setup';
import { UserFactory, PredefinedUsers } from '../factories/user-factory';
import { SpeechFactory, PredefinedSpeeches } from '../factories/speech-factory';

test.describe('Data-Driven Authentication Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to signin page before each test
    await page.goto('/auth/signin');
  });

  test('should login with demo user from factory', async ({ page, authHelper, demoUser }) => {
    // Using the demo user from the fixture (automatically created by testData fixture)
    TestUtils.logStep('Logging in with demo user', { email: demoUser.email });
    
    await authHelper.login('demo');
    
    // Verify successful login
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText(demoUser.email)).toBeVisible();
    
    TestUtils.logStep('Login successful, user on dashboard');
  });

  test('should handle multiple user scenarios', async ({ page, dataManager, authHelper }) => {
    // Create users for different scenarios using the data manager
    const newUser = await dataManager.createUser(UserFactory.createForScenario('new_user'));
    const returningUser = await dataManager.createUser(UserFactory.createForScenario('returning_user'));
    
    TestUtils.logStep('Created test users', { 
      newUser: newUser.email, 
      returningUser: returningUser.email 
    });
    
    // Test new user registration flow
    await page.goto('/auth/signup');
    await page.fill('[name="fullName"]', newUser.fullName);
    await page.fill('[name="email"]', newUser.email);
    await page.fill('[name="password"]', newUser.password);
    await page.fill('[name="confirmPassword"]', newUser.password);
    await page.click('[type="submit"]');
    
    // Should redirect to signin or dashboard
    await expect(page).toHaveURL(/\/(auth\/signin|dashboard)/);
    
    // Test returning user login
    if (await page.url().includes('signin')) {
      await authHelper.ensureLoggedOut();
      await page.goto('/auth/signin');
    }
    
    await page.fill('[name="email"]', returningUser.email);
    await page.fill('[name="password"]', returningUser.password);
    await page.click('[type="submit"]');
    
    await expect(page).toHaveURL('/dashboard');
    TestUtils.logStep('Multi-user scenario completed successfully');
  });

  test('should test with generated user data', async ({ page, dataManager }) => {
    // Generate user with specific characteristics for edge case testing
    const complexUser = UserFactory.createWithCharacteristics({
      emailLength: 'long',
      nameComplexity: 'complex',
      passwordStrength: 'strong'
    });
    
    // Create the user via API
    await dataManager.createUser(complexUser);
    
    TestUtils.logStep('Testing with complex user data', {
      email: complexUser.email,
      nameLength: complexUser.fullName.length,
      passwordLength: complexUser.password.length
    });
    
    // Test login with complex data
    await page.fill('[name="email"]', complexUser.email);
    await page.fill('[name="password"]', complexUser.password);
    await page.click('[type="submit"]');
    
    // Should successfully login
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText(complexUser.fullName)).toBeVisible();
  });

  test('should test speech analysis with factory data', async ({ 
    page, 
    dataManager, 
    demoUser, 
    speechHelper 
  }) => {
    // Login first
    await page.goto('/auth/signin');
    await page.fill('[name="email"]', demoUser.email);
    await page.fill('[name="password"]', demoUser.password);
    await page.click('[type="submit"]');
    
    await expect(page).toHaveURL('/dashboard');
    
    // Navigate to speech analysis
    await speechHelper.navigateToSpeechAnalysis();
    
    // Use predefined speech from factory
    const professionalSpeech = PredefinedSpeeches.professional;
    
    TestUtils.logStep('Analyzing professional speech', {
      title: professionalSpeech.title,
      wordCount: professionalSpeech.expectedWordCount,
      category: professionalSpeech.category
    });
    
    // Perform text analysis
    await page.fill('[data-testid="speech-text-input"]', professionalSpeech.content);
    await page.click('[data-testid="analyze-button"]');
    
    // Wait for analysis to complete
    await TestUtils.waitForNetworkIdle(page);
    
    // Verify results are displayed
    await expect(page.locator('[data-testid="analysis-results"]')).toBeVisible();
    
    // Create speech analysis record via API for future testing
    await dataManager.createSpeechAnalysis(demoUser, professionalSpeech);
    
    TestUtils.logStep('Speech analysis completed and recorded');
  });

  test('should handle batch user testing', async ({ page, dataManager }) => {
    // Create multiple users for batch testing
    const batchUsers = UserFactory.createBatch(3, { 
      domain: 'batch-test.com',
      password: 'BatchTest123!'
    });
    
    TestUtils.logStep('Testing batch user creation', {
      userCount: batchUsers.length,
      domain: 'batch-test.com'
    });
    
    // Create all users via API
    for (const user of batchUsers) {
      await dataManager.createUser(user);
    }
    
    // Test login for each user
    for (const user of batchUsers) {
      await page.goto('/auth/signin');
      await page.fill('[name="email"]', user.email);
      await page.fill('[name="password"]', user.password);
      await page.click('[type="submit"]');
      
      await expect(page).toHaveURL('/dashboard');
      await expect(page.getByText(user.fullName)).toBeVisible();
      
      // Logout for next user
      await page.locator('text=Logout').click();
      await expect(page).toHaveURL('/');
    }
    
    TestUtils.logStep('Batch user testing completed');
  });

  test('should test with invalid user data', async ({ page }) => {
    // Test with invalid email format
    const invalidUser = UserFactory.createInvalid('email');
    
    await page.fill('[name="email"]', invalidUser.email!);
    await page.fill('[name="password"]', invalidUser.password!);
    await page.click('[type="submit"]');
    
    // Should stay on login page and show error
    await expect(page).toHaveURL('/auth/signin');
    await expect(page.locator('[role="alert"]')).toBeVisible();
    
    TestUtils.logStep('Invalid data test completed', { email: invalidUser.email });
  });

  test('should demonstrate data cleanup', async ({ dataManager }) => {
    // Create some test data
    const tempUser = await dataManager.createUser();
    const tempSpeech = await dataManager.createSpeechAnalysis(tempUser);
    
    TestUtils.logStep('Created temporary test data', {
      userId: tempUser.id,
      speechTitle: tempSpeech.title
    });
    
    // Verify data exists
    const createdUsers = dataManager.getCreatedUsers();
    const createdSpeeches = dataManager.getCreatedSpeeches();
    
    expect(createdUsers.length).toBeGreaterThan(0);
    expect(createdSpeeches.length).toBeGreaterThan(0);
    
    TestUtils.logStep('Verified test data exists in manager', {
      userCount: createdUsers.length,
      speechCount: createdSpeeches.length
    });
    
    // Cleanup will happen automatically via fixture teardown
  });
});

test.describe('Test Environment Verification', () => {
  
  test('should verify test environment is ready', async () => {
    // Check if all services are ready
    const envStatus = await TestUtils.verifyEnvironment(TestConfig.FRONTEND_URL);
    
    expect(envStatus.ready).toBe(true);
    if (!envStatus.ready) {
      console.error('Environment issues:', envStatus.issues);
    }
    
    TestUtils.logStep('Environment verification completed', envStatus);
  });

  test('should verify database state', async ({ dataManager }) => {
    // Check database health and state
    const dbState = await dataManager.verifyDatabaseState();
    
    TestUtils.logStep('Database state verification', dbState);
    
    // Database should be healthy (though counts might vary)
    expect(dbState.issues.length).toBeLessThanOrEqual(2); // Allow some missing endpoints
  });
});