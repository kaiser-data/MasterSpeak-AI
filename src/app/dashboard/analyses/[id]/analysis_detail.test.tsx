import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { useParams, useRouter } from 'next/navigation'
import { toast } from 'react-hot-toast'
import AnalysisDetailPage from './page'
import * as analysesService from '@/services/analyses'

// Mock dependencies
jest.mock('next/navigation', () => ({
  useParams: jest.fn(),
  useRouter: jest.fn(),
}))

jest.mock('react-hot-toast')

jest.mock('@/services/analyses', () => ({
  getAnalysisDetails: jest.fn(),
}))

jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}))

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: jest.fn(),
  },
})

const mockRouter = {
  push: jest.fn(),
  back: jest.fn(),
  forward: jest.fn(),
  refresh: jest.fn(),
  replace: jest.fn(),
}

const mockAnalysisData = {
  analysis_id: 'analysis-1',
  speech_id: 'speech-1',
  speech_title: 'Test Speech',
  speech_content: 'This is test speech content.',
  transcript: 'This is the full transcript of the speech with all the words that were spoken during the presentation.',
  summary: 'A test speech summary.',
  metrics: {
    word_count: 150,
    clarity_score: 8.5,
    structure_score: 7.8,
    filler_word_count: 3,
  },
  feedback: 'Great job on the presentation! Your clarity was excellent.',
  created_at: '2024-01-15T10:30:00Z',
  updated_at: '2024-01-15T10:35:00Z'
}

describe('AnalysisDetailPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(useParams as jest.Mock).mockReturnValue({ id: 'analysis-1' })
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
    ;(analysesService.getAnalysisDetails as jest.Mock).mockResolvedValue(mockAnalysisData)
  })

  describe('Loading State', () => {
    it('should show loading indicator initially', () => {
      ;(analysesService.getAnalysisDetails as jest.Mock).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      )

      render(<AnalysisDetailPage />)
      
      expect(screen.getByText('Loading analysis...')).toBeInTheDocument()
      expect(screen.getByRole('status', { hidden: true })).toBeInTheDocument() // Loading spinner
    })
  })

  describe('Success State', () => {
    beforeEach(() => {
      // Set environment variable for transcript UI
      process.env.NEXT_PUBLIC_TRANSCRIPTION_UI = '1'
    })

    afterEach(() => {
      delete process.env.NEXT_PUBLIC_TRANSCRIPTION_UI
    })

    it('should render analysis details correctly', async () => {
      render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Test Speech')).toBeInTheDocument()
      })

      // Check that all main sections are present
      expect(screen.getByText('Analysis from 1/15/2024')).toBeInTheDocument()
      expect(screen.getByText('Transcript')).toBeInTheDocument()
      expect(screen.getByText('Analysis Results')).toBeInTheDocument()
      expect(screen.getByText('Summary')).toBeInTheDocument()
      expect(screen.getByText('Metadata')).toBeInTheDocument()
      expect(screen.getByText('Scores')).toBeInTheDocument()
    })

    it('should display transcript content when available', async () => {
      render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText(/This is the full transcript/)).toBeInTheDocument()
      })
    })

    it('should hide transcript section when TRANSCRIPTION_UI flag is not set', async () => {
      delete process.env.NEXT_PUBLIC_TRANSCRIPTION_UI

      render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Test Speech')).toBeInTheDocument()
      })

      expect(screen.queryByText('Transcript')).not.toBeInTheDocument()
    })

    it('should display metadata correctly', async () => {
      render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('150')).toBeInTheDocument() // Word count
        expect(screen.getByText('3')).toBeInTheDocument() // Filler words
        expect(screen.getByText('1/15/2024')).toBeInTheDocument() // Created date
      })
    })

    it('should display scores with correct values', async () => {
      render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('8.5/10')).toBeInTheDocument() // Clarity score
        expect(screen.getByText('7.8/10')).toBeInTheDocument() // Structure score
        expect(screen.getByText('8.2/10')).toBeInTheDocument() // Overall score
      })
    })

    it('should handle transcript expansion/collapse', async () => {
      const user = userEvent.setup()
      render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Test Speech')).toBeInTheDocument()
      })

      const expandButton = screen.getByRole('button', { name: /expand/i })
      await user.click(expandButton)

      expect(screen.getByRole('button', { name: /collapse/i })).toBeInTheDocument()

      const collapseButton = screen.getByRole('button', { name: /collapse/i })
      await user.click(collapseButton)

      expect(screen.getByRole('button', { name: /expand/i })).toBeInTheDocument()
    })

    it('should copy transcript to clipboard', async () => {
      const user = userEvent.setup()
      const mockWriteText = jest.fn()
      ;(navigator.clipboard.writeText as jest.Mock).mockImplementation(mockWriteText)

      render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Test Speech')).toBeInTheDocument()
      })

      const copyButton = screen.getByRole('button', { name: /copy/i })
      await user.click(copyButton)

      expect(mockWriteText).toHaveBeenCalledWith(mockAnalysisData.transcript)
      expect(toast.success).toHaveBeenCalledWith('Transcript copied to clipboard')
    })

    it('should disable copy button when no transcript available', async () => {
      const dataWithoutTranscript = {
        ...mockAnalysisData,
        transcript: undefined,
      }
      ;(analysesService.getAnalysisDetails as jest.Mock).mockResolvedValue(dataWithoutTranscript)

      render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Test Speech')).toBeInTheDocument()
      })

      const copyButton = screen.getByRole('button', { name: /copy/i })
      expect(copyButton).toBeDisabled()
    })

    it('should navigate back to analyses when back button clicked', async () => {
      const user = userEvent.setup()
      render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Test Speech')).toBeInTheDocument()
      })

      const backButton = screen.getByRole('button', { name: /back to analyses/i })
      await user.click(backButton)

      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard/analyses')
    })
  })

  describe('Error State', () => {
    it('should show error message when analysis fetch fails', async () => {
      const errorMessage = 'Analysis not found'
      ;(analysesService.getAnalysisDetails as jest.Mock).mockRejectedValue(new Error(errorMessage))

      render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Error Loading Analysis')).toBeInTheDocument()
        expect(screen.getByText(errorMessage)).toBeInTheDocument()
      })

      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /back to analyses/i })).toBeInTheDocument()
    })

    it('should retry fetching when retry button clicked', async () => {
      const user = userEvent.setup()
      ;(analysesService.getAnalysisDetails as jest.Mock)
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce(mockAnalysisData)

      render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Error Loading Analysis')).toBeInTheDocument()
      })

      const retryButton = screen.getByRole('button', { name: /retry/i })
      await user.click(retryButton)

      await waitFor(() => {
        expect(screen.getByText('Test Speech')).toBeInTheDocument()
      })

      expect(analysesService.getAnalysisDetails).toHaveBeenCalledTimes(2)
    })

    it('should navigate back when back button clicked in error state', async () => {
      const user = userEvent.setup()
      ;(analysesService.getAnalysisDetails as jest.Mock).mockRejectedValue(new Error('Network error'))

      render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Error Loading Analysis')).toBeInTheDocument()
      })

      const backButton = screen.getByRole('button', { name: /back to analyses/i })
      await user.click(backButton)

      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard/analyses')
    })
  })

  describe('Not Found State', () => {
    it('should show not found message when analysis is null', async () => {
      ;(analysesService.getAnalysisDetails as jest.Mock).mockResolvedValue(null)

      render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Analysis Not Found')).toBeInTheDocument()
        expect(screen.getByText('The requested analysis could not be found.')).toBeInTheDocument()
      })

      expect(screen.getByRole('button', { name: /back to analyses/i })).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    beforeEach(() => {
      process.env.NEXT_PUBLIC_TRANSCRIPTION_UI = '1'
    })

    afterEach(() => {
      delete process.env.NEXT_PUBLIC_TRANSCRIPTION_UI
    })

    it('should have proper ARIA labels and roles', async () => {
      render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Test Speech')).toBeInTheDocument()
      })

      // Check for main heading
      expect(screen.getByRole('heading', { level: 1, name: 'Test Speech' })).toBeInTheDocument()

      // Check for section headings
      expect(screen.getByRole('heading', { level: 2, name: 'Transcript' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { level: 2, name: 'Analysis Results' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { level: 2, name: 'Summary' })).toBeInTheDocument()

      // Check for interactive elements
      expect(screen.getByRole('button', { name: /copy/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /expand/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /back to analyses/i })).toBeInTheDocument()
    })

    it('should support keyboard navigation', async () => {
      const user = userEvent.setup()
      render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Test Speech')).toBeInTheDocument()
      })

      const backButton = screen.getByRole('button', { name: /back to analyses/i })
      const copyButton = screen.getByRole('button', { name: /copy/i })
      const expandButton = screen.getByRole('button', { name: /expand/i })

      // Tab through interactive elements
      await user.tab()
      expect(backButton).toHaveFocus()

      await user.tab()
      expect(screen.getByRole('button', { name: /export/i })).toHaveFocus()

      await user.tab()
      expect(screen.getByRole('button', { name: /share/i })).toHaveFocus()

      // Find and focus copy button
      await user.click(copyButton)
      expect(copyButton).toHaveFocus()

      // Test Enter key activation
      await user.keyboard('{Enter}')
      expect(toast.success).toHaveBeenCalledWith('Transcript copied to clipboard')
    })
  })

  describe('Data Formatting', () => {
    it('should format dates correctly', async () => {
      render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Analysis from 1/15/2024')).toBeInTheDocument()
        expect(screen.getByText('1/15/2024')).toBeInTheDocument() // In metadata
      })
    })

    it('should format numbers correctly', async () => {
      const dataWithLargeNumbers = {
        ...mockAnalysisData,
        metrics: {
          ...mockAnalysisData.metrics,
          word_count: 1234,
        },
      }
      ;(analysesService.getAnalysisDetails as jest.Mock).mockResolvedValue(dataWithLargeNumbers)

      render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('1,234')).toBeInTheDocument() // Formatted word count
      })
    })

    it('should calculate overall score correctly', async () => {
      render(<AnalysisDetailPage />)

      await waitFor(() => {
        // Overall score should be (8.5 + 7.8) / 2 = 8.15, rounded to 8.2
        expect(screen.getByText('8.2/10')).toBeInTheDocument()
      })
    })
  })

  describe('Edge Cases', () => {
    it('should handle missing optional fields gracefully', async () => {
      const minimalData = {
        analysis_id: 'analysis-1',
        speech_id: 'speech-1',
        speech_title: 'Minimal Speech',
        speech_content: 'Content',
        metrics: {
          word_count: 50,
          clarity_score: 5.0,
          structure_score: 6.0,
          filler_word_count: 0,
        },
        feedback: 'Basic feedback',
        created_at: '2024-01-15T10:30:00Z',
        updated_at: '2024-01-15T10:35:00Z'
      }
      ;(analysesService.getAnalysisDetails as jest.Mock).mockResolvedValue(minimalData)

      render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Minimal Speech')).toBeInTheDocument()
      })

      // Should show "Transcript not available" when no transcript
      expect(screen.getByText('Transcript not available')).toBeInTheDocument()
      
      // Should not show summary section when no summary
      expect(screen.queryByText('Summary')).not.toBeInTheDocument()
    })

    it('should handle zero scores', async () => {
      const zeroScoreData = {
        ...mockAnalysisData,
        metrics: {
          word_count: 10,
          clarity_score: 0,
          structure_score: 0,
          filler_word_count: 10,
        },
      }
      ;(analysesService.getAnalysisDetails as jest.Mock).mockResolvedValue(zeroScoreData)

      render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('0/10')).toBeInTheDocument() // Should display 0 scores
        expect(screen.getByText('0.0/10')).toBeInTheDocument() // Overall score
      })
    })

    it('should handle analysis ID parameter changes', async () => {
      const { rerender } = render(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Test Speech')).toBeInTheDocument()
      })

      // Change the analysis ID
      ;(useParams as jest.Mock).mockReturnValue({ id: 'analysis-2' })
      const newAnalysisData = { ...mockAnalysisData, speech_title: 'Different Speech' }
      ;(analysesService.getAnalysisDetails as jest.Mock).mockResolvedValue(newAnalysisData)

      rerender(<AnalysisDetailPage />)

      await waitFor(() => {
        expect(screen.getByText('Different Speech')).toBeInTheDocument()
      })

      expect(analysesService.getAnalysisDetails).toHaveBeenCalledWith('analysis-2')
    })
  })
})