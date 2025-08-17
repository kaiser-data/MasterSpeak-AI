// src/__tests__/search_analyses.test.tsx

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { useRouter, useSearchParams } from 'next/navigation'
import { searchAnalyses, AnalysisSearchParams } from '@/services/analyses'
import AnalysesPage from '@/app/dashboard/analyses/page'

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useSearchParams: jest.fn(),
}))

jest.mock('@/services/analyses', () => ({
  getAnalysesPage: jest.fn(),
  searchAnalyses: jest.fn(),
  formatRelativeTime: jest.fn(() => '2 hours ago'),
  truncateText: jest.fn((text: string) => text),
  calculateOverallScore: jest.fn(() => 8.5),
  getScoreColorClass: jest.fn(() => 'text-green-600'),
}))

jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}))

const mockRouter = {
  push: jest.fn(),
  back: jest.fn(),
  forward: jest.fn(),
  refresh: jest.fn(),
  replace: jest.fn(),
}

const mockSearchParams = {
  get: jest.fn(),
  toString: jest.fn(() => ''),
}

describe('AnalysesPage Search Functionality', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
    ;(useSearchParams as jest.Mock).mockReturnValue(mockSearchParams)
  })

  const mockAnalysisResponse = {
    items: [
      {
        analysis_id: '123e4567-e89b-12d3-a456-426614174000',
        speech_id: '123e4567-e89b-12d3-a456-426614174001',
        user_id: '123e4567-e89b-12d3-a456-426614174002',
        speech_title: 'Test Speech',
        metrics: {
          word_count: 100,
          clarity_score: 8.5,
          structure_score: 7.8,
          filler_word_count: 2,
        },
        summary: 'Great speech about innovation',
        feedback: 'Excellent clarity and structure',
        created_at: '2024-01-15T10:30:00Z',
        updated_at: '2024-01-15T10:30:00Z',
      },
    ],
    total: 1,
    page: 1,
    page_size: 1,
    has_next: false,
    has_previous: false,
  }

  it('renders search interface correctly', async () => {
    // Arrange
    ;(searchAnalyses as jest.Mock).mockResolvedValue(mockAnalysisResponse)
    mockSearchParams.get.mockReturnValue(null)

    // Act
    render(<AnalysesPage />)

    // Assert
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search in feedback and summary...')).toBeInTheDocument()
      expect(screen.getByText('Filters')).toBeInTheDocument()
      expect(screen.getByText('Search')).toBeInTheDocument()
    })
  })

  it('performs text search correctly', async () => {
    // Arrange
    ;(searchAnalyses as jest.Mock).mockResolvedValue(mockAnalysisResponse)
    mockSearchParams.get.mockReturnValue(null)

    // Act
    render(<AnalysesPage />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search in feedback and summary...')).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText('Search in feedback and summary...')
    const searchButton = screen.getByText('Search')

    fireEvent.change(searchInput, { target: { value: 'innovation' } })
    fireEvent.click(searchButton)

    // Assert
    await waitFor(() => {
      expect(searchAnalyses).toHaveBeenCalledWith({
        page: 1,
        limit: 20,
        q: 'innovation',
      })
    })

    expect(mockRouter.push).toHaveBeenCalledWith('/dashboard/analyses?q=innovation&page=1')
  })

  it('shows and hides filter panel correctly', async () => {
    // Arrange
    ;(searchAnalyses as jest.Mock).mockResolvedValue(mockAnalysisResponse)
    mockSearchParams.get.mockReturnValue(null)

    // Act
    render(<AnalysesPage />)

    await waitFor(() => {
      expect(screen.getByText('Filters')).toBeInTheDocument()
    })

    const filtersButton = screen.getByText('Filters')

    // Initially filters should be hidden
    expect(screen.queryByText('Clarity Score Range')).not.toBeInTheDocument()

    // Show filters
    fireEvent.click(filtersButton)
    await waitFor(() => {
      expect(screen.getByText('Clarity Score Range')).toBeInTheDocument()
      expect(screen.getByText('Structure Score Range')).toBeInTheDocument()
      expect(screen.getByText('Date Range')).toBeInTheDocument()
    })

    // Hide filters
    fireEvent.click(filtersButton)
    await waitFor(() => {
      expect(screen.queryByText('Clarity Score Range')).not.toBeInTheDocument()
    })
  })

  it('applies score filters correctly', async () => {
    // Arrange
    ;(searchAnalyses as jest.Mock).mockResolvedValue(mockAnalysisResponse)
    mockSearchParams.get.mockReturnValue(null)

    // Act
    render(<AnalysesPage />)

    await waitFor(() => {
      expect(screen.getByText('Filters')).toBeInTheDocument()
    })

    // Open filters
    fireEvent.click(screen.getByText('Filters'))

    await waitFor(() => {
      expect(screen.getByText('Clarity Score Range')).toBeInTheDocument()
    })

    // Set score filters
    const clarityInputs = screen.getAllByDisplayValue('')
    const minClarityInput = clarityInputs.find(input => 
      input.getAttribute('placeholder') === 'Min' && 
      input.closest('div')?.previousSibling?.textContent?.includes('Clarity')
    )
    const maxClarityInput = clarityInputs.find(input => 
      input.getAttribute('placeholder') === 'Max' && 
      input.closest('div')?.previousSibling?.textContent?.includes('Clarity')
    )

    if (minClarityInput && maxClarityInput) {
      fireEvent.change(minClarityInput, { target: { value: '7.0' } })
      fireEvent.change(maxClarityInput, { target: { value: '9.0' } })
    }

    fireEvent.click(screen.getByText('Search'))

    // Assert
    await waitFor(() => {
      expect(searchAnalyses).toHaveBeenCalledWith({
        page: 1,
        limit: 20,
        min_clarity: 7.0,
        max_clarity: 9.0,
      })
    })
  })

  it('applies date filters correctly', async () => {
    // Arrange
    ;(searchAnalyses as jest.Mock).mockResolvedValue(mockAnalysisResponse)
    mockSearchParams.get.mockReturnValue(null)

    // Act
    render(<AnalysesPage />)

    await waitFor(() => {
      expect(screen.getByText('Filters')).toBeInTheDocument()
    })

    // Open filters
    fireEvent.click(screen.getByText('Filters'))

    await waitFor(() => {
      expect(screen.getByText('Date Range')).toBeInTheDocument()
    })

    // Set date filters
    const dateInputs = screen.getAllByDisplayValue('')
    const startDateInput = dateInputs.find(input => input.getAttribute('type') === 'date')
    const endDateInput = dateInputs.filter(input => input.getAttribute('type') === 'date')[1]

    if (startDateInput && endDateInput) {
      fireEvent.change(startDateInput, { target: { value: '2024-01-01' } })
      fireEvent.change(endDateInput, { target: { value: '2024-01-31' } })
    }

    fireEvent.click(screen.getByText('Search'))

    // Assert
    await waitFor(() => {
      expect(searchAnalyses).toHaveBeenCalledWith({
        page: 1,
        limit: 20,
        start_date: '2024-01-01',
        end_date: '2024-01-31',
      })
    })
  })

  it('clears filters correctly', async () => {
    // Arrange
    mockSearchParams.get.mockImplementation((key: string) => {
      if (key === 'q') return 'test'
      if (key === 'min_clarity') return '7.0'
      return null
    })
    ;(searchAnalyses as jest.Mock).mockResolvedValue(mockAnalysisResponse)

    // Act
    render(<AnalysesPage />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('test')).toBeInTheDocument()
      expect(screen.getByText('Clear')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Clear'))

    // Assert
    expect(mockRouter.push).toHaveBeenCalledWith('/dashboard/analyses')
  })

  it('shows active filter indicator', async () => {
    // Arrange
    mockSearchParams.get.mockImplementation((key: string) => {
      if (key === 'q') return 'innovation'
      return null
    })
    ;(searchAnalyses as jest.Mock).mockResolvedValue(mockAnalysisResponse)

    // Act
    render(<AnalysesPage />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Active')).toBeInTheDocument()
      expect(screen.getByText('Clear')).toBeInTheDocument()
    })
  })

  it('handles search on Enter key press', async () => {
    // Arrange
    ;(searchAnalyses as jest.Mock).mockResolvedValue(mockAnalysisResponse)
    mockSearchParams.get.mockReturnValue(null)

    // Act
    render(<AnalysesPage />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search in feedback and summary...')).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText('Search in feedback and summary...')

    fireEvent.change(searchInput, { target: { value: 'test query' } })
    fireEvent.keyDown(searchInput, { key: 'Enter', code: 'Enter' })

    // Assert
    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard/analyses?q=test+query&page=1')
    })
  })

  it('displays search results correctly', async () => {
    // Arrange
    ;(searchAnalyses as jest.Mock).mockResolvedValue(mockAnalysisResponse)
    mockSearchParams.get.mockReturnValue('innovation')

    // Act
    render(<AnalysesPage />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Test Speech')).toBeInTheDocument()
      expect(screen.getByText('Excellent clarity and structure')).toBeInTheDocument()
    })
  })

  it('handles empty search results', async () => {
    // Arrange
    const emptyResponse = {
      ...mockAnalysisResponse,
      items: [],
      total: 0,
    }
    ;(searchAnalyses as jest.Mock).mockResolvedValue(emptyResponse)
    mockSearchParams.get.mockReturnValue('nonexistent')

    // Act
    render(<AnalysesPage />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('No analyses yet')).toBeInTheDocument()
      expect(screen.getByText('Start analyzing your speeches to see results here')).toBeInTheDocument()
    })
  })

  it('handles search errors gracefully', async () => {
    // Arrange
    ;(searchAnalyses as jest.Mock).mockRejectedValue(new Error('Search failed'))
    mockSearchParams.get.mockReturnValue('test')

    // Act
    render(<AnalysesPage />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Search failed')).toBeInTheDocument()
    })
  })
})