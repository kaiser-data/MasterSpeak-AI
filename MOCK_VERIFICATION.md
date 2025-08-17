# Mock Implementation Verification Guide

## Overview
This guide provides steps to verify the mock implementation of navigation and paginated analyses list functionality.

## Pre-requisites
- Frontend development server running (`npm run dev`)
- Mock service files properly imported and configured

## Manual Verification Steps

### 1. Dashboard Navigation
1. Navigate to `http://localhost:3000/dashboard`
2. Scroll down to "Recent Analyses" section
3. Click the "View All" button
4. **Expected**: Should navigate to `/dashboard/analyses`
5. **Expected**: URL should update and page should load

### 2. Analyses List Page - Basic Functionality
1. On `/dashboard/analyses` page:
2. **Expected**: See "All Analyses" heading
3. **Expected**: See total count in subtitle (e.g., "(47 total)")
4. **Expected**: See list of mock analyses with titles like:
   - "Product Launch Presentation #1"
   - "Quarterly Sales Review #1" 
   - "Team Building Speech #1"
5. **Expected**: Each analysis shows:
   - Title
   - Relative timestamp (e.g., "2 days ago")
   - Word count (e.g., "250 words")
   - Metrics: Clarity, Structure, Fillers scores

### 3. Loading States
1. Refresh the `/dashboard/analyses` page
2. **Expected**: See loading spinner with "Loading analyses..." text
3. **Expected**: Loading should complete within 1 second (mock delay)

### 4. Pagination
1. On analyses list page:
2. **Expected**: See pagination controls at bottom:
   - "Previous" button (disabled on page 1)
   - Page numbers (1, 2, 3, etc.)
   - "Next" button
3. Click "Next" button
4. **Expected**: URL updates to `/dashboard/analyses?page=2`
5. **Expected**: Page content refreshes with new mock data
6. **Expected**: "Previous" button becomes enabled
7. Click page number "3"
8. **Expected**: URL updates to `/dashboard/analyses?page=3`
9. Click "Previous"
10. **Expected**: Goes back to page 2

### 5. Analysis Detail Navigation
1. On analyses list page:
2. Click on any analysis card/row
3. **Expected**: Navigate to `/dashboard/analyses/analysis-001` (or similar)
4. **Expected**: See "Analysis Details" page with:
   - Analysis title
   - Metrics cards (Clarity, Structure, Filler Words)
   - Mock feedback text
   - Mock transcript (if available)
   - Mock summary (if available)

### 6. Back Navigation
1. From analysis detail page:
2. Click "Back to Analyses" button
3. **Expected**: Return to `/dashboard/analyses`
4. **Expected**: Previous page state preserved (same page number)

### 7. Empty State (Simulated)
1. Modify mock service to return empty results:
   - Edit `src/services/analyses-mock.ts`
   - Change `const total = 47` to `const total = 0`
   - Change `const items: AnalysisListItem[] = []` (remove the for loop)
2. Refresh `/dashboard/analyses`
3. **Expected**: See empty state with:
   - Chart icon
   - "No analyses yet" heading
   - "Start analyzing your speeches to see results here"
   - "Create Your First Analysis" button

### 8. Error State (Simulated)
1. Modify mock service to simulate errors:
   - Edit `src/services/analyses-mock.ts`
   - Change error probability: `if (Math.random() < 0.95)` (increase to 95%)
2. Refresh `/dashboard/analyses` multiple times
3. **Expected**: Occasionally see error state with:
   - Error message "Mock API error: Network timeout"
   - "Back to Dashboard" button

### 9. Responsive Design
1. Open browser dev tools
2. Switch to mobile viewport (375px width)
3. Navigate to `/dashboard/analyses`
4. **Expected**: Page layout adapts to mobile:
   - Single column layout
   - Pagination still accessible
   - Navigation remains usable

### 10. Performance Testing
1. Navigate between pages rapidly
2. **Expected**: Smooth transitions with appropriate loading states
3. **Expected**: No console errors
4. **Expected**: Mock delays feel realistic (300-500ms)

## Testing Different Scenarios

### Large Dataset Simulation
1. In `analyses-mock.ts`, increase `const total = 150`
2. Verify pagination shows correct total pages
3. Test navigation to last page

### Different Mock Data
1. Modify titles array in `generateMockAnalysis`
2. Add your own speech titles
3. Verify they appear in the list

### Error Recovery
1. After simulating errors, restore normal behavior
2. Verify page recovers and loads normally
3. Check that error state clears properly

## Success Criteria

✅ **Navigation**: Dashboard → Analyses list works smoothly
✅ **Loading**: Shows appropriate loading states
✅ **Data Display**: Mock data renders correctly with all fields
✅ **Pagination**: All pagination controls function properly
✅ **Detail View**: Analysis detail pages load and display properly
✅ **Back Navigation**: Can return to list from detail view
✅ **Empty State**: Gracefully handles no data scenarios
✅ **Error Handling**: Shows appropriate error messages
✅ **Responsive**: Works on mobile and desktop
✅ **Performance**: Fast loading with realistic delays

## Troubleshooting

### Common Issues:
1. **404 on navigation**: Check that mock page files are named correctly
2. **No data showing**: Verify mock service is properly imported
3. **TypeScript errors**: Ensure interfaces match between service and components
4. **Pagination not working**: Check URL parameter handling

### Debug Steps:
1. Open browser console for error messages
2. Check network tab for any actual API calls (should be none)
3. Verify file imports in components
4. Test with different page numbers in URL directly

## Cleanup

After verification, remember to:
1. Restore original mock settings (total count, error rates)
2. Switch back to real API integration when Agent A is ready
3. Update imports from `-mock` files to real service files