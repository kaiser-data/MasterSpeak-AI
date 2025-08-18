import { test, expect } from '@playwright/test'

test.describe('Analyses List Page', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.route('**/api/v1/auth/me', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'test-user-id',
          email: 'test@example.com',
          full_name: 'Test User',
          is_active: true
        })
      })
    })

    // Mock analyses API
    await page.route('**/api/v1/analyses*', async route => {
      const url = new URL(route.request().url())
      const page_num = url.searchParams.get('page') || '1'
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              analysis_id: 'analysis-1',
              speech_id: 'speech-1',
              speech_title: 'Sample Speech Analysis',
              summary: 'This is a test summary of the speech analysis.',
              metrics: {
                word_count: 250,
                clarity_score: 8.5,
                structure_score: 7.8,
                filler_word_count: 5
              },
              created_at: '2024-01-15T10:30:00Z'
            },
            {
              analysis_id: 'analysis-2', 
              speech_id: 'speech-2',
              speech_title: 'Another Speech Test',
              summary: null,
              metrics: {
                word_count: 180,
                clarity_score: 9.2,
                structure_score: 8.1,
                filler_word_count: 2
              },
              created_at: '2024-01-14T15:45:00Z'
            }
          ],
          total: 25,
          page: parseInt(page_num),
          page_size: 20,
          total_pages: 2
        })
      })
    })

    // Navigate to analyses page
    await page.goto('/dashboard/analyses')
  })

  test('displays analyses list with correct data', async ({ page }) => {
    // Wait for page to load
    await expect(page.getByText('All Analyses')).toBeVisible()
    
    // Check that analyses are displayed
    await expect(page.getByText('Sample Speech Analysis')).toBeVisible()
    await expect(page.getByText('Another Speech Test')).toBeVisible()
    
    // Check metrics are displayed
    await expect(page.getByText('250 words')).toBeVisible()
    await expect(page.getByText('180 words')).toBeVisible()
    
    // Check scores are displayed
    await expect(page.getByText('8.5')).toBeVisible()
    await expect(page.getByText('9.2')).toBeVisible()
  })

  test('shows total count in header', async ({ page }) => {
    await expect(page.getByText('(25 total)')).toBeVisible()
  })

  test('displays pagination controls', async ({ page }) => {
    await expect(page.getByText('Previous')).toBeVisible()
    await expect(page.getByText('Next')).toBeVisible()
    await expect(page.getByText('1')).toBeVisible()
    await expect(page.getByText('2')).toBeVisible()
  })

  test('pagination navigation works', async ({ page }) => {
    // Click on page 2
    await page.getByText('2').click()
    
    // Check URL updated
    await expect(page).toHaveURL('/dashboard/analyses?page=2')
  })

  test('next/previous buttons work', async ({ page }) => {
    // Initially on page 1, Previous should be disabled
    await expect(page.getByText('Previous')).toBeDisabled()
    
    // Click Next
    await page.getByText('Next').click()
    await expect(page).toHaveURL('/dashboard/analyses?page=2')
  })

  test('clicking analysis navigates to detail page', async ({ page }) => {
    // Mock the analysis detail API
    await page.route('**/api/v1/analyses/analysis-1', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          analysis_id: 'analysis-1',
          speech_id: 'speech-1',
          user_id: 'test-user-id',
          speech_title: 'Sample Speech Analysis',
          speech_content: 'redacted_for_privacy',
          transcript: null,
          summary: 'This is a test summary',
          metrics: {
            word_count: 250,
            clarity_score: 8.5,
            structure_score: 7.8,
            filler_word_count: 5
          },
          feedback: 'Detailed feedback here',
          created_at: '2024-01-15T10:30:00Z',
          updated_at: '2024-01-15T10:30:00Z'
        })
      })
    })
    
    // Click on the first analysis
    await page.getByText('Sample Speech Analysis').click()
    
    // Should navigate to detail page
    await expect(page).toHaveURL('/dashboard/analyses/analysis-1')
  })

  test('back to dashboard link works', async ({ page }) => {
    await page.getByText('Back to Dashboard').click()
    await expect(page).toHaveURL('/dashboard')
  })

  test('handles empty state', async ({ page }) => {
    // Mock empty response
    await page.route('**/api/v1/analyses*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0,
          page: 1,
          page_size: 20,
          total_pages: 0
        })
      })
    })

    await page.reload()
    
    await expect(page.getByText('No analyses yet')).toBeVisible()
    await expect(page.getByText('Start analyzing your speeches to see results here')).toBeVisible()
  })

  test('handles loading state', async ({ page }) => {
    // Delay the API response to test loading state
    await page.route('**/api/v1/analyses*', async route => {
      await new Promise(resolve => setTimeout(resolve, 100))
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0,
          page: 1,
          page_size: 20,
          total_pages: 0
        })
      })
    })

    await page.reload()
    
    // Should see loading state briefly
    await expect(page.getByText('Loading analyses...')).toBeVisible()
  })

  test('handles error state', async ({ page }) => {
    // Mock error response
    await page.route('**/api/v1/analyses*', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Internal server error'
        })
      })
    })

    await page.reload()
    
    await expect(page.getByText(/Failed to load analyses|Internal server error/)).toBeVisible()
  })

  test('responsive design works on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    
    // Check that page still displays correctly
    await expect(page.getByText('All Analyses')).toBeVisible()
    await expect(page.getByText('Sample Speech Analysis')).toBeVisible()
    
    // Pagination should still be accessible
    await expect(page.getByText('Next')).toBeVisible()
  })

  test('keyboard navigation works', async ({ page }) => {
    // Tab through pagination controls
    await page.keyboard.press('Tab')
    await page.keyboard.press('Tab')
    
    // Should be able to navigate with keyboard
    const focusedElement = await page.locator(':focus').textContent()
    expect(['Previous', 'Next', '1', '2']).toContain(focusedElement)
  })
})