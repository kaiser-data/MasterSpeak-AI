import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { useRouter, useParams } from 'next/navigation'
import { toast } from 'react-hot-toast'
import AnalysisDetailPage from '@/app/dashboard/analyses/[id]/page'
import { getAnalysisById } from '@/services/analyses'
import type { Analysis } from '@/services/analyses'

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useParams: jest.fn()
}))

jest.mock('react-hot-toast', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
    loading: jest.fn()
  }
}))

jest.mock('@/services/analyses', () => ({
  getAnalysisById: jest.fn(),
  formatRelativeTime: jest.fn((date: string) => '2 hours ago'),
  getScoreColorClass: jest.fn((score: number) => 'text-green-600'),
  calculateOverallScore: jest.fn((metrics: any) => 8.5)
}))

jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>
  }
}))

// Mock environment variables
const originalEnv = process.env
beforeEach(() => {
  process.env = {
    ...originalEnv,
    NEXT_PUBLIC_TRANSCRIPTION_UI: '1'
  }
})

afterEach(() => {
  process.env = originalEnv
  jest.clearAllMocks()
})

const mockAnalysis: Analysis = {
  analysis_id: 'analysis-1',
  speech_id: 'speech-1',
  user_id: 'user-1',
  transcript: 'Good morning everyone. Today I want to discuss our quarterly results.',
  summary: 'A quarterly business presentation discussing company growth.',
  metrics: {
    word_count: 156,
    clarity_score: 8.5,
    structure_score: 7.8,
    filler_word_count: 3
  },
  feedback: 'Your presentation demonstrates strong command of the subject matter.',
  created_at: '2024-01-15T10:30:00Z',
  updated_at: '2024-01-15T10:35:00Z'
}

const mockRouter = {
  push: jest.fn(),
  back: jest.fn(),
  forward: jest.fn(),
  refresh: jest.fn(),
  replace: jest.fn()
}

describe('AnalysisDetailPage', () => {
  beforeEach(() => {
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
    ;(useParams as jest.Mock).mockReturnValue({ id: 'analysis-1' })
    ;(getAnalysisById as jest.Mock).mockResolvedValue(mockAnalysis)
  })

  describe('Loading State', () => {
    it('should show loading spinner initially', () => {
      ;(getAnalysisById as jest.Mock).mockImplementation(() => new Promise(() => {}))
      
      render(<AnalysisDetailPage />)
      
      expect(screen.getByText('Loading analysis...')).toBeInTheDocument()
    })
  })

  describe('Success State', () => {
    it('should render analysis details when data loads successfully', async () => {
      render(<AnalysisDetailPage />)
      
      await waitFor(() => {
        expect(screen.getByText('Analysis Details')).toBeInTheDocument()
      })

      expect(screen.getByText('Transcript')).toBeInTheDocument()
      expect(screen.getByText('Performance Metrics')).toBeInTheDocument()
      expect(screen.getByText('AI Feedback')).toBeInTheDocument()
      expect(screen.getByText('Metadata')).toBeInTheDocument()
    })

    it('should display transcript with expand/collapse functionality', async () => {
      render(<AnalysisDetailPage />)
      
      await waitFor(() => {
        expect(screen.getByText('Transcript')).toBeInTheDocument()
      })

      const expandButton = screen.getByTitle('Expand')
      expect(expandButton).toBeInTheDocument()
      
      fireEvent.click(expandButton)
      expect(screen.getByTitle('Collapse')).toBeInTheDocument()
    })

    it('should show copy button for transcript when available', async () => {
      // Mock clipboard API
      Object.assign(navigator, {
        clipboard: {
          writeText: jest.fn().mockImplementation(() => Promise.resolve())
        }
      })

      render(<AnalysisDetailPage />)
      
      await waitFor(() => {
        expect(screen.getByText('Transcript')).toBeInTheDocument()
      })

      const copyButton = screen.getByTitle('Copy transcript to clipboard')
      expect(copyButton).toBeInTheDocument()
      
      fireEvent.click(copyButton)
      
      await waitFor(() => {
        expect(navigator.clipboard.writeText).toHaveBeenCalledWith(mockAnalysis.transcript)
      })
    })

    it('should display export and share buttons', async () => {
      render(<AnalysisDetailPage />)
      
      await waitFor(() => {
        expect(screen.getByText('Analysis Details')).toBeInTheDocument()
      })

      expect(screen.getByRole('button', { name: /Export/ })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /Share/ })).toBeInTheDocument()
    })
  })

  describe('Error State', () => {
    it('should show error message when analysis fails to load', async () => {
      const errorMessage = 'Analysis not found'
      ;(getAnalysisById as jest.Mock).mockRejectedValue(new Error(errorMessage))
      
      render(<AnalysisDetailPage />)
      
      await waitFor(() => {
        expect(screen.getByText('Failed to Load Analysis')).toBeInTheDocument()
        expect(screen.getByText(errorMessage)).toBeInTheDocument()
      })

      expect(screen.getByRole('button', { name: /Retry/ })).toBeInTheDocument()
    })

    it('should handle retry functionality', async () => {
      ;(getAnalysisById as jest.Mock).mockRejectedValueOnce(new Error('Network error'))
      ;(getAnalysisById as jest.Mock).mockResolvedValueOnce(mockAnalysis)
      
      render(<AnalysisDetailPage />)
      
      await waitFor(() => {
        expect(screen.getByText('Failed to Load Analysis')).toBeInTheDocument()
      })

      const retryButton = screen.getByRole('button', { name: /Retry/ })
      fireEvent.click(retryButton)
      
      await waitFor(() => {
        expect(screen.getByText('Analysis Details')).toBeInTheDocument()
      })
    })
  })

  describe('Feature Flag Behavior', () => {
    it('should hide transcript section when TRANSCRIPTION_UI flag is disabled', async () => {
      process.env.NEXT_PUBLIC_TRANSCRIPTION_UI = '0'
      
      render(<AnalysisDetailPage />)
      
      await waitFor(() => {
        expect(screen.getByText('Analysis Details')).toBeInTheDocument()
      })

      expect(screen.queryByText('Transcript')).not.toBeInTheDocument()
      expect(screen.getByText('Performance Metrics')).toBeInTheDocument()
    })

    it('should show transcript section when TRANSCRIPTION_UI flag is enabled', async () => {
      process.env.NEXT_PUBLIC_TRANSCRIPTION_UI = '1'
      
      render(<AnalysisDetailPage />)
      
      await waitFor(() => {
        expect(screen.getByText('Analysis Details')).toBeInTheDocument()
      })

      expect(screen.getByText('Transcript')).toBeInTheDocument()
      expect(screen.getByText('Performance Metrics')).toBeInTheDocument()
    })
  })

  describe('No Transcript State', () => {
    it('should show appropriate message when transcript is not available', async () => {
      const analysisWithoutTranscript = {
        ...mockAnalysis,
        transcript: undefined
      }
      ;(getAnalysisById as jest.Mock).mockResolvedValue(analysisWithoutTranscript)
      
      render(<AnalysisDetailPage />)
      
      await waitFor(() => {
        expect(screen.getByText('Transcript')).toBeInTheDocument()
      })

      expect(screen.getByText('No transcript available for this analysis')).toBeInTheDocument()
      expect(screen.queryByTitle('Copy transcript to clipboard')).not.toBeInTheDocument()
    })
  })

  describe('Navigation', () => {
    it('should navigate back to analyses when back button is clicked', async () => {
      render(<AnalysisDetailPage />)
      
      await waitFor(() => {
        expect(screen.getByText('Analysis Details')).toBeInTheDocument()
      })

      const backButton = screen.getByText('Back to Analyses')
      fireEvent.click(backButton)
      
      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard/analyses')
    })
  })
})