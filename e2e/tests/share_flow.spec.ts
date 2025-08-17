import { test, expect } from '@playwright/test'
import { authHelper } from '../helpers/auth-helper'

test.describe('Share Flow', () => {
  // Skip all tests if export is not enabled
  test.beforeEach(async ({ page }) => {
    const exportEnabled = process.env.NEXT_PUBLIC_EXPORT_ENABLED === "1"
    if (!exportEnabled) {
      test.skip('Export functionality is not enabled')
    }
  })

  test.describe('Authentication Required', () => {
    test.beforeEach(async ({ page }) => {
      await authHelper.signIn(page)
    })

    test('should create share link for analysis', async ({ page }) => {
      // Navigate to an analysis detail page
      // Note: This assumes we have at least one analysis available
      await page.goto('/dashboard/analyses')
      
      // Wait for analyses to load
      await expect(page.locator('[data-testid="analysis-item"]').first()).toBeVisible({ timeout: 10000 })
      
      // Click on the first analysis
      await page.locator('[data-testid="analysis-item"]').first().click()
      
      // Wait for analysis detail page to load
      await expect(page.locator('h1')).toBeVisible()
      
      // Look for the Share button (only visible if export is enabled)
      const shareButton = page.locator('button:has-text("Share")')
      await expect(shareButton).toBeVisible()
      
      // Click the Share button
      await shareButton.click()
      
      // Wait for share link to be created
      await expect(page.locator('[data-testid="share-link-display"]')).toBeVisible({ timeout: 5000 })
      
      // Verify share link is displayed
      const shareUrl = await page.locator('[data-testid="share-url"]').textContent()
      expect(shareUrl).toContain('/share/')
      expect(shareUrl).toMatch(/^https?:\/\//)
      
      // Verify expiration notice
      await expect(page.locator('text=Expires in 7 days')).toBeVisible()
    })

    test('should copy share link to clipboard', async ({ page }) => {
      // Navigate to analysis and create share link (similar to above)
      await page.goto('/dashboard/analyses')
      await expect(page.locator('[data-testid="analysis-item"]').first()).toBeVisible({ timeout: 10000 })
      await page.locator('[data-testid="analysis-item"]').first().click()
      
      const shareButton = page.locator('button:has-text("Share")')
      await shareButton.click()
      await expect(page.locator('[data-testid="share-link-display"]')).toBeVisible({ timeout: 5000 })
      
      // Grant clipboard permissions
      await page.context().grantPermissions(['clipboard-read', 'clipboard-write'])
      
      // Click copy button
      const copyButton = page.locator('button:has-text("Copy")')
      await copyButton.click()
      
      // Verify copy feedback
      await expect(page.locator('button:has-text("Copied!")')).toBeVisible()
      
      // Verify clipboard content
      const clipboardContent = await page.evaluate(() => navigator.clipboard.readText())
      expect(clipboardContent).toContain('/share/')
    })

    test('should export analysis as PDF', async ({ page }) => {
      // Navigate to analysis detail page
      await page.goto('/dashboard/analyses')
      await expect(page.locator('[data-testid="analysis-item"]').first()).toBeVisible({ timeout: 10000 })
      await page.locator('[data-testid="analysis-item"]').first().click()
      
      // Look for Export button
      const exportButton = page.locator('button:has-text("Export")')
      await expect(exportButton).toBeVisible()
      
      // Set up download listener
      const downloadPromise = page.waitForEvent('download')
      
      // Hover over Export to show dropdown
      await exportButton.hover()
      
      // Click on "Export as PDF" option
      await page.locator('button:has-text("Export as PDF")').click()
      
      // Wait for download
      const download = await downloadPromise
      
      // Verify download
      expect(download.suggestedFilename()).toMatch(/.*\.pdf$/)
      
      // Verify file is not empty
      const path = await download.path()
      if (path) {
        const fs = require('fs')
        const stats = fs.statSync(path)
        expect(stats.size).toBeGreaterThan(0)
      }
    })

    test('should export analysis as JSON', async ({ page }) => {
      // Navigate to analysis detail page
      await page.goto('/dashboard/analyses')
      await expect(page.locator('[data-testid="analysis-item"]').first()).toBeVisible({ timeout: 10000 })
      await page.locator('[data-testid="analysis-item"]').first().click()
      
      // Set up download listener
      const downloadPromise = page.waitForEvent('download')
      
      // Hover over Export to show dropdown
      const exportButton = page.locator('button:has-text("Export")')
      await exportButton.hover()
      
      // Click on "Export as JSON" option
      await page.locator('button:has-text("Export as JSON")').click()
      
      // Wait for download
      const download = await downloadPromise
      
      // Verify download
      expect(download.suggestedFilename()).toMatch(/.*\.json$/)
      
      // Verify JSON content
      const path = await download.path()
      if (path) {
        const fs = require('fs')
        const content = fs.readFileSync(path, 'utf8')
        const jsonData = JSON.parse(content)
        
        expect(jsonData).toHaveProperty('analysis_id')
        expect(jsonData).toHaveProperty('feedback')
        expect(jsonData).toHaveProperty('export_metadata')
      }
    })

    test('should handle export loading states', async ({ page }) => {
      await page.goto('/dashboard/analyses')
      await expect(page.locator('[data-testid="analysis-item"]').first()).toBeVisible({ timeout: 10000 })
      await page.locator('[data-testid="analysis-item"]').first().click()
      
      // Mock slow network to test loading state
      await page.route('**/analyses/*/export', async route => {
        await new Promise(resolve => setTimeout(resolve, 2000))
        await route.continue()
      })
      
      const exportButton = page.locator('button:has-text("Export")')
      await exportButton.hover()
      await page.locator('button:has-text("Export as PDF")').click()
      
      // Verify loading state
      await expect(page.locator('button:has-text("Exporting...")')).toBeVisible()
    })

    test('should handle share loading states', async ({ page }) => {
      await page.goto('/dashboard/analyses')
      await expect(page.locator('[data-testid="analysis-item"]').first()).toBeVisible({ timeout: 10000 })
      await page.locator('[data-testid="analysis-item"]').first().click()
      
      // Mock slow network to test loading state
      await page.route('**/share/*', async route => {
        await new Promise(resolve => setTimeout(resolve, 2000))
        await route.continue()
      })
      
      const shareButton = page.locator('button:has-text("Share")')
      await shareButton.click()
      
      // Verify loading state
      await expect(page.locator('button:has-text("Creating...")')).toBeVisible()
    })
  })

  test.describe('Public Share Access', () => {
    test('should access shared analysis without authentication', async ({ page }) => {
      // This test would require a pre-existing share token
      // In a real scenario, you'd create one in a setup step or use a test fixture
      
      // Mock successful share token response
      await page.route('**/share/*', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            analysis_id: 'test-analysis-id',
            speech_id: 'test-speech-id',
            user_id: 'test-user-id',
            feedback: 'This is test feedback for a shared analysis',
            metrics: {
              word_count: 150,
              clarity_score: 8,
              structure_score: 7,
              filler_word_count: 3
            },
            summary: 'Test summary for shared analysis',
            created_at: new Date().toISOString(),
            shared: true,
            transcript_included: false
          })
        })
      })
      
      // Access a mock share URL
      await page.goto('/share/test-token')
      
      // Verify public share page loads
      await expect(page.locator('text=Shared Analysis')).toBeVisible()
      await expect(page.locator('text=This is test feedback')).toBeVisible()
      
      // Verify metrics are displayed
      await expect(page.locator('text=150')).toBeVisible() // word count
      await expect(page.locator('text=8')).toBeVisible() // clarity score
      await expect(page.locator('text=7')).toBeVisible() // structure score
    })

    test('should handle expired share token', async ({ page }) => {
      // Mock expired token response
      await page.route('**/share/*', async route => {
        await route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({
            detail: 'Share link not found or expired'
          })
        })
      })
      
      await page.goto('/share/expired-token')
      
      // Verify error message
      await expect(page.locator('text=Share link not found or expired')).toBeVisible()
    })

    test('should handle invalid share token', async ({ page }) => {
      await page.route('**/share/*', async route => {
        await route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({
            detail: 'Share link not found or expired'
          })
        })
      })
      
      await page.goto('/share/invalid-token')
      
      // Verify error handling
      await expect(page.locator('text=not found')).toBeVisible()
    })

    test('should show transcript when enabled', async ({ page }) => {
      // Mock share response with transcript
      await page.route('**/share/*', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            analysis_id: 'test-analysis-id',
            speech_id: 'test-speech-id',
            user_id: 'test-user-id',
            feedback: 'Test feedback',
            transcript: 'This is the speech transcript that should be visible',
            transcript_included: true,
            metrics: { word_count: 150 },
            created_at: new Date().toISOString(),
            shared: true
          })
        })
      })
      
      await page.goto('/share/test-token-with-transcript')
      
      // Verify transcript is displayed
      await expect(page.locator('text=This is the speech transcript')).toBeVisible()
      await expect(page.locator('text=Transcript')).toBeVisible()
    })

    test('should hide transcript when disabled', async ({ page }) => {
      // Mock share response without transcript
      await page.route('**/share/*', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            analysis_id: 'test-analysis-id',
            speech_id: 'test-speech-id',
            user_id: 'test-user-id',
            feedback: 'Test feedback',
            transcript_included: false,
            metrics: { word_count: 150 },
            created_at: new Date().toISOString(),
            shared: true
          })
        })
      })
      
      await page.goto('/share/test-token-no-transcript')
      
      // Verify transcript section is not displayed
      await expect(page.locator('text=Transcript')).not.toBeVisible()
    })
  })

  test.describe('Error Handling', () => {
    test.beforeEach(async ({ page }) => {
      await authHelper.signIn(page)
    })

    test('should handle export API errors', async ({ page }) => {
      await page.goto('/dashboard/analyses')
      await expect(page.locator('[data-testid="analysis-item"]').first()).toBeVisible({ timeout: 10000 })
      await page.locator('[data-testid="analysis-item"]').first().click()
      
      // Mock API error
      await page.route('**/analyses/*/export', async route => {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Export failed' })
        })
      })
      
      const exportButton = page.locator('button:has-text("Export")')
      await exportButton.hover()
      await page.locator('button:has-text("Export as PDF")').click()
      
      // Verify error message
      await expect(page.locator('text=Failed to export PDF')).toBeVisible()
    })

    test('should handle share API errors', async ({ page }) => {
      await page.goto('/dashboard/analyses')
      await expect(page.locator('[data-testid="analysis-item"]').first()).toBeVisible({ timeout: 10000 })
      await page.locator('[data-testid="analysis-item"]').first().click()
      
      // Mock API error
      await page.route('**/share/*', async route => {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Share creation failed' })
        })
      })
      
      const shareButton = page.locator('button:has-text("Share")')
      await shareButton.click()
      
      // Verify error message
      await expect(page.locator('text=Failed to create share link')).toBeVisible()
    })

    test('should handle rate limiting', async ({ page }) => {
      await page.goto('/dashboard/analyses')
      await expect(page.locator('[data-testid="analysis-item"]').first()).toBeVisible({ timeout: 10000 })
      await page.locator('[data-testid="analysis-item"]').first().click()
      
      // Mock rate limit error
      await page.route('**/share/*', async route => {
        await route.fulfill({
          status: 429,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Rate limit exceeded' })
        })
      })
      
      const shareButton = page.locator('button:has-text("Share")')
      await shareButton.click()
      
      // Verify rate limit message
      await expect(page.locator('text=Rate limit exceeded')).toBeVisible()
    })
  })

  test.describe('Feature Disabled', () => {
    test('should hide export/share buttons when feature is disabled', async ({ page }) => {
      // Override environment variable for this test
      await page.addInitScript(() => {
        Object.defineProperty(window, 'process', {
          value: {
            env: {
              NEXT_PUBLIC_EXPORT_ENABLED: "0"
            }
          }
        })
      })
      
      await authHelper.signIn(page)
      await page.goto('/dashboard/analyses')
      await expect(page.locator('[data-testid="analysis-item"]').first()).toBeVisible({ timeout: 10000 })
      await page.locator('[data-testid="analysis-item"]').first().click()
      
      // Verify buttons are not visible
      await expect(page.locator('button:has-text("Export")')).not.toBeVisible()
      await expect(page.locator('button:has-text("Share")')).not.toBeVisible()
    })
  })
})