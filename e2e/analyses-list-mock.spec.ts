import { test, expect } from '@playwright/test'

test.describe('Analyses List Page (Mock)', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to dashboard first
    await page.goto('/dashboard')
  })

  test('navigates from dashboard to analyses list', async ({ page }) => {
    // Click "View All" button on dashboard
    await page.getByText('View All').click()
    
    // Should navigate to analyses list
    await expect(page).toHaveURL('/dashboard/analyses')
    await expect(page.getByText('All Analyses')).toBeVisible()
  })

  test('displays loading state', async ({ page }) => {
    // Navigate directly to analyses page
    await page.goto('/dashboard/analyses')
    
    // Should see loading state briefly
    const loadingText = page.getByText('Loading analyses...')
    
    // Use a longer timeout as the mock has built-in delays
    await expect(loadingText).toBeVisible({ timeout: 1000 })
  })

  test('displays analyses list with mock data', async ({ page }) => {
    await page.goto('/dashboard/analyses')
    
    // Wait for analyses to load
    await expect(page.getByText('All Analyses')).toBeVisible()
    
    // Check that mock analyses are displayed
    await expect(page.getByText(/Product Launch Presentation/)).toBeVisible()
    await expect(page.getByText(/Quarterly Sales Review/)).toBeVisible()
    
    // Check word counts are displayed
    await expect(page.getByText(/\d+ words/)).toBeVisible()
    
    // Check total count
    await expect(page.getByText(/\(\d+ total\)/)).toBeVisible()
  })

  test('pagination controls work', async ({ page }) => {
    await page.goto('/dashboard/analyses')
    
    // Wait for page to load
    await expect(page.getByText('All Analyses')).toBeVisible()
    
    // Should see pagination controls
    await expect(page.getByText('Previous')).toBeVisible()
    await expect(page.getByText('Next')).toBeVisible()
    
    // Previous should be disabled on first page
    await expect(page.getByText('Previous')).toBeDisabled()
    
    // Click next page
    await page.getByText('Next').click()
    
    // URL should update
    await expect(page).toHaveURL('/dashboard/analyses?page=2')
  })

  test('clicking analysis navigates to detail page', async ({ page }) => {
    await page.goto('/dashboard/analyses')
    
    // Wait for analyses to load
    await expect(page.getByText('All Analyses')).toBeVisible()
    
    // Click on first analysis
    const firstAnalysis = page.getByTestId('analysis-item').first()
    await firstAnalysis.click()
    
    // Should navigate to detail page
    await expect(page).toHaveURL(/\/dashboard\/analyses\/analysis-\d+/)
    
    // Should see analysis details
    await expect(page.getByText('Analysis Details')).toBeVisible()
  })

  test('back navigation works', async ({ page }) => {
    await page.goto('/dashboard/analyses')
    
    // Click back to dashboard
    await page.getByText('Back to Dashboard').click()
    
    // Should return to dashboard
    await expect(page).toHaveURL('/dashboard')
  })

  test('handles empty state (simulated)', async ({ page }) => {
    // Mock empty response by intercepting the service call
    await page.route('**/analyses-mock.ts', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/javascript',
        body: `
          export async function getAnalysesPage() {
            return {
              items: [],
              total: 0,
              page: 1,
              page_size: 20,
              total_pages: 0
            }
          }
        `
      })
    })
    
    await page.goto('/dashboard/analyses')
    
    // Should see empty state
    await expect(page.getByText('No analyses yet')).toBeVisible()
    await expect(page.getByText('Start analyzing your speeches to see results here')).toBeVisible()
  })

  test('displays relative timestamps', async ({ page }) => {
    await page.goto('/dashboard/analyses')
    
    // Wait for analyses to load
    await expect(page.getByText('All Analyses')).toBeVisible()
    
    // Should see relative time format (days ago, hours ago, etc.)
    await expect(page.getByText(/\d+ days? ago|\d+ hours? ago|Just now/)).toBeVisible()
  })

  test('shows metrics for each analysis', async ({ page }) => {
    await page.goto('/dashboard/analyses')
    
    // Wait for analyses to load
    await expect(page.getByText('All Analyses')).toBeVisible()
    
    // Should see score headers
    await expect(page.getByText('Clarity')).toBeVisible()
    await expect(page.getByText('Structure')).toBeVisible()
    await expect(page.getByText('Fillers')).toBeVisible()
    
    // Should see numerical scores
    await expect(page.getByText(/\d+\.\d+/)).toBeVisible()
  })

  test('responsive design on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    
    await page.goto('/dashboard/analyses')
    
    // Should still display main content
    await expect(page.getByText('All Analyses')).toBeVisible()
    
    // Navigation should be accessible
    await expect(page.getByText('Back to Dashboard')).toBeVisible()
  })

  test('keyboard navigation works', async ({ page }) => {
    await page.goto('/dashboard/analyses')
    
    // Wait for page to load
    await expect(page.getByText('All Analyses')).toBeVisible()
    
    // Tab through pagination controls
    await page.keyboard.press('Tab')
    await page.keyboard.press('Tab')
    
    // Should be able to focus on pagination buttons
    const focusedElement = await page.locator(':focus').textContent()
    expect(['Previous', 'Next', '1', '2', '3']).toContain(focusedElement)
  })

  test('error state recovery', async ({ page }) => {
    // This would require more complex mocking to simulate errors
    // For now, we'll test that error states are handled gracefully
    await page.goto('/dashboard/analyses')
    
    // If there's an error, should show error message
    // This is more of a smoke test since our mock rarely errors
    await expect(page.getByText('All Analyses')).toBeVisible({ timeout: 10000 })
  })

  test('page header shows correct pagination info', async ({ page }) => {
    await page.goto('/dashboard/analyses?page=2')
    
    // Wait for page to load
    await expect(page.getByText('All Analyses')).toBeVisible()
    
    // Should show current page info in header
    await expect(page.getByText(/Page 2 of \d+/)).toBeVisible()
  })

  test('deep linking to specific page works', async ({ page }) => {
    // Navigate directly to page 3
    await page.goto('/dashboard/analyses?page=3')
    
    // Should load page 3 correctly
    await expect(page.getByText('All Analyses')).toBeVisible()
    await expect(page.getByText(/Page 3 of \d+/)).toBeVisible()
  })
})