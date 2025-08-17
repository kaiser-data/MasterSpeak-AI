/**
 * @jest-environment jsdom
 */
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { useRouter, useSearchParams } from 'next/navigation'
import AnalysesPage from '@/app/dashboard/analyses/page-mock'
import * as analysesService from '@/services/analyses-mock'

// Mock Next.js navigation hooks
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useSearchParams: jest.fn(),
}))

// Mock the analyses service
jest.mock('@/services/analyses-mock')

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}))

const mockPush = jest.fn()
const mockRouter = {
  push: mockPush,
  back: jest.fn(),
  forward: jest.fn(),
  refresh: jest.fn(),
  replace: jest.fn(),
}

const mockSearchParams = {
  get: jest.fn(),
}

const mockAnalysesData = {
  items: [
    {
      analysis_id: 'analysis-001',
      speech_id: 'speech-001', 
      speech_title: 'Product Launch Presentation #1',
      summary: 'This speech demonstrates strong communication skills',
      metrics: {
        word_count: 250,
        clarity_score: 8.5,
        structure_score: 7.2,
        filler_word_count: 3,
      },
      created_at: '2024-01-01T12:00:00Z',
    },
    {
      analysis_id: 'analysis-002',
      speech_id: 'speech-002',
      speech_title: 'Quarterly Sales Review #1', 
      summary: undefined,
      metrics: {
        word_count: 180,
        clarity_score: 9.0,
        structure_score: 8.5,
        filler_word_count: 1,
      },
      created_at: '2024-01-02T12:00:00Z',
    },
  ],
  total: 47,
  page: 1,
  page_size: 20,
  total_pages: 3,
}

describe('AnalysesPage (Mock)', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
    ;(useSearchParams as jest.Mock).mockReturnValue(mockSearchParams)
    mockSearchParams.get.mockReturnValue('1') // Default to page 1
  })

  it('renders loading state initially', () => {
    mockSearchParams.get.mockReturnValue('1')
    ;(analysesService.getAnalysesPage as jest.Mock).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )

    render(<AnalysesPage />)
    
    expect(screen.getByText('Loading analyses...')).toBeInTheDocument()
  })

  it('renders analyses list successfully', async () => {
    ;(analysesService.getAnalysesPage as jest.Mock).mockResolvedValue(mockAnalysesData)

    render(<AnalysesPage />)

    await waitFor(() => {
      expect(screen.getByText('All Analyses')).toBeInTheDocument()
    })

    expect(screen.getByText('(47 total)')).toBeInTheDocument()
    expect(screen.getByText('Product Launch Presentation #1')).toBeInTheDocument()
    expect(screen.getByText('Quarterly Sales Review #1')).toBeInTheDocument()
    expect(screen.getByText('250 words')).toBeInTheDocument()
    expect(screen.getByText('180 words')).toBeInTheDocument()
  })

  it('renders empty state when no analyses', async () => {
    const emptyData = {
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      total_pages: 0,
    }
    ;(analysesService.getAnalysesPage as jest.Mock).mockResolvedValue(emptyData)

    render(<AnalysesPage />)

    await waitFor(() => {
      expect(screen.getByText('No analyses yet')).toBeInTheDocument()
    })

    expect(screen.getByText('Start analyzing your speeches to see results here')).toBeInTheDocument()
    expect(screen.getByText('Create Your First Analysis')).toBeInTheDocument()
  })

  it('handles error state', async () => {
    ;(analysesService.getAnalysesPage as jest.Mock).mockRejectedValue(
      new Error('Mock API error: Network timeout')
    )

    render(<AnalysesPage />)

    await waitFor(() => {
      expect(screen.getByText('Mock API error: Network timeout')).toBeInTheDocument()
    })

    expect(screen.getByText('Back to Dashboard')).toBeInTheDocument()
  })

  it('displays metrics correctly', async () => {
    ;(analysesService.getAnalysesPage as jest.Mock).mockResolvedValue(mockAnalysesData)

    render(<AnalysesPage />)

    await waitFor(() => {
      expect(screen.getByText('Product Launch Presentation #1')).toBeInTheDocument()
    })

    // Check metrics for first analysis
    const clarityElements = screen.getAllByText('8.5')
    const structureElements = screen.getAllByText('7.2')
    const fillerElements = screen.getAllByText('3')
    
    expect(clarityElements).toHaveLength(1)
    expect(structureElements).toHaveLength(1) 
    expect(fillerElements).toHaveLength(1)
  })

  it('navigates to analysis detail on click', async () => {
    ;(analysesService.getAnalysesPage as jest.Mock).mockResolvedValue(mockAnalysesData)

    render(<AnalysesPage />)

    await waitFor(() => {
      expect(screen.getByText('Product Launch Presentation #1')).toBeInTheDocument()
    })

    const analysisCard = screen.getByTestId('analysis-item')
    fireEvent.click(analysisCard)

    expect(mockPush).toHaveBeenCalledWith('/dashboard/analyses/analysis-001')
  })

  describe('Pagination', () => {
    beforeEach(() => {
      ;(analysesService.getAnalysesPage as jest.Mock).mockResolvedValue(mockAnalysesData)
    })

    it('renders pagination when multiple pages exist', async () => {
      render(<AnalysesPage />)

      await waitFor(() => {
        expect(screen.getByText('Product Launch Presentation #1')).toBeInTheDocument()
      })

      expect(screen.getByText('Previous')).toBeInTheDocument()
      expect(screen.getByText('Next')).toBeInTheDocument()
      expect(screen.getByText('1')).toBeInTheDocument()
      expect(screen.getByText('3')).toBeInTheDocument() // Last page
    })

    it('disables Previous button on first page', async () => {
      render(<AnalysesPage />)

      await waitFor(() => {
        expect(screen.getByText('Product Launch Presentation #1')).toBeInTheDocument()
      })

      const prevButton = screen.getByText('Previous')
      expect(prevButton).toBeDisabled()
    })

    it('navigates to next page', async () => {
      render(<AnalysesPage />)

      await waitFor(() => {
        expect(screen.getByText('Product Launch Presentation #1')).toBeInTheDocument()
      })

      const nextButton = screen.getByText('Next')
      fireEvent.click(nextButton)

      expect(mockPush).toHaveBeenCalledWith('/dashboard/analyses?page=2')
    })

    it('navigates to specific page', async () => {
      render(<AnalysesPage />)

      await waitFor(() => {
        expect(screen.getByText('Product Launch Presentation #1')).toBeInTheDocument()
      })

      const pageButton = screen.getByText('3')
      fireEvent.click(pageButton)

      expect(mockPush).toHaveBeenCalledWith('/dashboard/analyses?page=3')
    })

    it('handles different page from URL params', async () => {
      mockSearchParams.get.mockReturnValue('2')
      
      render(<AnalysesPage />)

      await waitFor(() => {
        expect(analysesService.getAnalysesPage).toHaveBeenCalledWith(2, 20)
      })
    })

    it('does not render pagination for single page', async () => {
      const singlePageData = {
        ...mockAnalysesData,
        total: 5,
        total_pages: 1,
      }
      ;(analysesService.getAnalysesPage as jest.Mock).mockResolvedValue(singlePageData)

      render(<AnalysesPage />)

      await waitFor(() => {
        expect(screen.getByText('Product Launch Presentation #1')).toBeInTheDocument()
      })

      expect(screen.queryByText('Previous')).not.toBeInTheDocument()
      expect(screen.queryByText('Next')).not.toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('has proper heading structure', async () => {
      ;(analysesService.getAnalysesPage as jest.Mock).mockResolvedValue(mockAnalysesData)

      render(<AnalysesPage />)

      await waitFor(() => {
        expect(screen.getByRole('heading', { level: 1, name: /All Analyses/ })).toBeInTheDocument()
      })
    })

    it('has accessible navigation links', async () => {
      ;(analysesService.getAnalysesPage as jest.Mock).mockResolvedValue(mockAnalysesData)

      render(<AnalysesPage />)

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /Back to Dashboard/ })).toBeInTheDocument()
      })
    })
  })

  describe('Mock Data Generation', () => {
    it('generates consistent mock data', async () => {
      ;(analysesService.getAnalysesPage as jest.Mock).mockResolvedValue(mockAnalysesData)

      render(<AnalysesPage />)

      await waitFor(() => {
        expect(screen.getByText('Product Launch Presentation #1')).toBeInTheDocument()
      })

      // Verify mock data structure
      expect(mockAnalysesData.items[0].analysis_id).toBe('analysis-001')
      expect(mockAnalysesData.items[0].speech_id).toBe('speech-001')
      expect(mockAnalysesData.items[0].metrics.word_count).toBe(250)
    })
  })
})