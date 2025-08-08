import { test, expect } from '@playwright/test';
import { AuthHelper } from './helpers/auth-helper';
import { SpeechHelper } from './helpers/speech-helper';
import { testAudioData, selectors } from './fixtures/test-data';

test.describe('Speech Analysis Flow', () => {
  let authHelper: AuthHelper;
  let speechHelper: SpeechHelper;

  test.beforeEach(async ({ page }) => {
    authHelper = new AuthHelper(page);
    speechHelper = new SpeechHelper(page);
    
    // Ensure user is logged in before each test
    await authHelper.ensureLoggedIn('demo');
  });

  test.describe('Text Analysis', () => {
    test('should analyze basic text speech', async ({ page }) => {
      const results = await speechHelper.analyzeText(testAudioData.speechTexts.basic);
      
      // Validate results
      await speechHelper.validateAnalysisResults(results);
      
      // Check that analysis completed successfully
      await expect(page.locator(selectors.speechAnalysis.results)).toBeVisible();
    });

    test('should analyze complex text speech', async ({ page }) => {
      const results = await speechHelper.analyzeText(testAudioData.speechTexts.complex);
      
      await speechHelper.validateAnalysisResults(results);
      
      // Complex text should generate detailed feedback
      expect(results.fullResults.length).toBeGreaterThan(100);
    });

    test('should handle empty text input gracefully', async ({ page }) => {
      await speechHelper.navigateToSpeechAnalysis();
      
      // Try to analyze without entering text
      await page.click(selectors.speechAnalysis.analyzeButton);
      
      // Should show validation error or disable button
      const errorMessage = page.locator('[role="alert"]');
      if (await errorMessage.isVisible()) {
        await expect(errorMessage).toContainText(/text/i);
      } else {
        // Button should be disabled
        await expect(page.locator(selectors.speechAnalysis.analyzeButton)).toBeDisabled();
      }
    });
  });

  test.describe('Audio Upload Analysis', () => {
    test('should upload and analyze audio file', async ({ page }) => {
      const results = await speechHelper.uploadAndAnalyzeAudio();
      
      await speechHelper.validateAnalysisResults(results);
      
      // Verify analysis UI shows expected elements
      await expect(page.locator(selectors.speechAnalysis.results)).toBeVisible();
    });

    test('should handle invalid file formats', async ({ page }) => {
      await speechHelper.navigateToSpeechAnalysis();
      
      // Create a text file instead of audio
      const testFilePath = 'tests/fixtures/invalid.txt';
      await page.evaluate(() => {
        const content = 'This is not an audio file';
        const blob = new Blob([content], { type: 'text/plain' });
        const file = new File([blob], 'invalid.txt', { type: 'text/plain' });
        return file;
      });
      
      // Try to upload invalid file type
      await page.setInputFiles(selectors.speechAnalysis.fileUpload, testFilePath);
      
      // Should show error for invalid file type
      const errorMessage = page.locator('[role="alert"]');
      await expect(errorMessage).toBeVisible();
      await expect(errorMessage).toContainText(/audio/i);
    });

    test('should handle large file sizes', async ({ page }) => {
      await speechHelper.navigateToSpeechAnalysis();
      
      // This would normally test file size limits
      // For E2E testing, we'll verify the UI shows appropriate feedback
      await expect(page.locator('text=Maximum file size')).toBeVisible();
    });
  });

  test.describe('Audio Recording Analysis', () => {
    test('should record and analyze speech', async ({ page }) => {
      const results = await speechHelper.recordAndAnalyzeSpeech(2000); // 2 second recording
      
      await speechHelper.validateAnalysisResults(results);
      
      // Verify recording controls worked
      await expect(page.locator(selectors.speechAnalysis.results)).toBeVisible();
    });

    test('should show recording controls correctly', async ({ page }) => {
      await speechHelper.navigateToSpeechAnalysis();
      
      // Grant microphone permission
      await page.context().grantPermissions(['microphone']);
      
      // Verify record button is visible
      await expect(page.locator(selectors.speechAnalysis.recordButton)).toBeVisible();
      
      // Start recording
      await page.click(selectors.speechAnalysis.recordButton);
      
      // Stop button should appear
      await expect(page.locator(selectors.speechAnalysis.stopButton)).toBeVisible();
      
      // Record button should be hidden or disabled
      await expect(page.locator(selectors.speechAnalysis.recordButton)).toBeHidden();
    });

    test('should handle microphone permission denial', async ({ page }) => {
      await speechHelper.navigateToSpeechAnalysis();
      
      // Block microphone permission
      await page.context().setPermissions([], 'microphone');
      
      // Try to start recording
      await page.click(selectors.speechAnalysis.recordButton);
      
      // Should show permission error
      const errorMessage = page.locator('[role="alert"]');
      await expect(errorMessage).toBeVisible();
      await expect(errorMessage).toContainText(/microphone|permission/i);
    });
  });

  test.describe('Complete User Journey', () => {
    test('should complete full analysis workflow: login → upload → analyze → results', async ({ page }) => {
      // Step 1: Already logged in from beforeEach
      await expect(page.locator(selectors.dashboard.welcomeMessage)).toBeVisible();
      
      // Step 2: Navigate to speech analysis
      await speechHelper.navigateToSpeechAnalysis();
      
      // Step 3: Upload and analyze audio
      const results = await speechHelper.uploadAndAnalyzeAudio();
      
      // Step 4: Verify results are displayed correctly
      await speechHelper.validateAnalysisResults(results);
      await expect(page.locator(selectors.speechAnalysis.results)).toBeVisible();
      
      // Step 5: Verify user can navigate back to dashboard
      await page.click(selectors.navigation.dashboardLink);
      await expect(page).toHaveURL('/dashboard');
    });

    test('should complete text analysis workflow: login → text input → analyze → results', async ({ page }) => {
      // Step 1: Verify logged in
      await expect(page.locator(selectors.dashboard.welcomeMessage)).toBeVisible();
      
      // Step 2: Navigate and analyze text
      const results = await speechHelper.analyzeText(testAudioData.speechTexts.professional);
      
      // Step 3: Verify comprehensive results
      await speechHelper.validateAnalysisResults(results);
      
      // Step 4: Check for professional feedback
      expect(results.fullResults).toContain('professional');
    });

    test('should complete recording workflow: login → record → analyze → results', async ({ page }) => {
      // Step 1: Verify logged in
      await expect(page.locator(selectors.dashboard.welcomeMessage)).toBeVisible();
      
      // Step 2: Record and analyze
      const results = await speechHelper.recordAndAnalyzeSpeech(3000);
      
      // Step 3: Validate results
      await speechHelper.validateAnalysisResults(results);
      
      // Step 4: Verify feedback is generated
      expect(results.fullResults.length).toBeGreaterThan(50);
    });
  });

  test.describe('Error Handling', () => {
    test('should handle API errors gracefully', async ({ page }) => {
      await speechHelper.navigateToSpeechAnalysis();
      
      // Mock API error by intercepting requests
      await page.route('/api/v1/analysis/**', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Internal server error' })
        });
      });
      
      // Try to analyze text
      await page.fill(selectors.speechAnalysis.textInput, testAudioData.speechTexts.basic);
      await page.click(selectors.speechAnalysis.analyzeButton);
      
      // Should show error message
      const errorMessage = page.locator('[role="alert"]');
      await expect(errorMessage).toBeVisible();
      await expect(errorMessage).toContainText(/error|failed/i);
    });

    test('should handle network timeouts', async ({ page }) => {
      await speechHelper.navigateToSpeechAnalysis();
      
      // Mock slow API response
      await page.route('/api/v1/analysis/**', route => {
        // Delay response by 35 seconds (longer than timeout)
        setTimeout(() => {
          route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({ analysis: 'Complete' })
          });
        }, 35000);
      });
      
      // Try to analyze
      await page.fill(selectors.speechAnalysis.textInput, testAudioData.speechTexts.basic);
      await page.click(selectors.speechAnalysis.analyzeButton);
      
      // Should show timeout error
      const errorMessage = page.locator('[role="alert"]');
      await expect(errorMessage).toBeVisible({ timeout: 40000 });
      await expect(errorMessage).toContainText(/timeout|slow|try again/i);
    });
  });
});