/**
 * Tests for Progress Page component
 */

import { render, screen, waitFor } from '@testing-library/react'
import { jest } from '@jest/globals'
import ProgressPage from '../page'

// Mock Next.js modules
jest.mock('next/link', () => {
  return function MockLink({ children, href }: { children: React.ReactNode; href: string }) {
    return <a href={href}>{children}</a>
  }
})

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, className, ...props }: any) => <div className={className} {...props}>{children}</div>
  }
}))

// Mock recharts
jest.mock('recharts', () => ({
  LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  Area: () => <div data-testid="area" />,
  AreaChart: ({ children }: any) => <div data-testid="area-chart">{children}</div>,
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  Pie: () => <div data-testid="pie" />,
  Cell: () => <div data-testid="cell" />
}))

// Mock API modules
const mockAuthAPI = {
  getCurrentUser: jest.fn()
}

const mockSpeechesAPI = {
  getRecentAnalyses: jest.fn(),
  getSpeech: jest.fn()
}

jest.mock('@/lib/api', () => ({
  authAPI: mockAuthAPI,
  speechesAPI: mockSpeechesAPI
}))

// Mock progress selectors
const mockProgressSelectors = {
  selectProgressData: jest.fn(),
  selectChartData: jest.fn(),
  selectWeeklyProgress: jest.fn(),
  generateMockProgressData: jest.fn()
}

jest.mock('@/selectors/progress', () => mockProgressSelectors)

// Mock environment
const originalEnv = process.env
beforeEach(() => {
  process.env = { ...originalEnv, NODE_ENV: 'test', PROGRESS_UI: '1' }
})

afterEach(() => {
  process.env = originalEnv
  jest.clearAllMocks()
})

describe('ProgressPage', () => {
  const mockUser = {
    id: 'user-1',
    email: 'test@example.com',
    full_name: 'Test User',
    is_active: true
  }

  const mockMetrics = {
    totalAnalyses: 5,
    averageClarity: 7.5,
    averageStructure: 8.0,
    averageFiller: 3.2,
    totalWords: 2500,
    improvementTrend: 15.5,
    recentActivity: 3
  }

  const mockChartData = [
    {
      date: '2024-01-15',
      clarity: 7.5,
      structure: 8.0,
      filler: 3.0,
      average: 7.75
    }
  ]

  const mockWeeklyData = [
    {
      week: 'Jan 15',
      analyses: 2,
      avgScore: 7.8
    }
  ]

  it('should render loading state initially', () => {
    // Don't setup mocks so component stays in loading state
    render(<ProgressPage />)
    
    expect(screen.getByText('Loading progress...')).toBeInTheDocument()
    expect(screen.getByTestId('loader')).toBeInTheDocument()
  })

  it('should render progress dashboard with mock data', async () => {
    // Setup mock data
    mockProgressSelectors.generateMockProgressData.mockReturnValue({
      analyses: [],
      metrics: mockMetrics,
      chartData: mockChartData,
      weeklyData: mockWeeklyData
    })

    render(<ProgressPage />)

    await waitFor(() => {
      expect(screen.getByText('Progress Overview')).toBeInTheDocument()
    })

    // Check stats cards
    expect(screen.getByText('Total Analyses')).toBeInTheDocument()
    expect(screen.getByText('5')).toBeInTheDocument() // Total analyses value
    expect(screen.getByText('Average Score')).toBeInTheDocument()
    expect(screen.getByText('7.8/10')).toBeInTheDocument() // Average score
    expect(screen.getByText('Improvement')).toBeInTheDocument()
    expect(screen.getByText('15.5%')).toBeInTheDocument() // Improvement value
    expect(screen.getByText('Recent Activity')).toBeInTheDocument()
    expect(screen.getByText('3 this week')).toBeInTheDocument() // Recent activity
  })

  it('should show charts when data is available', async () => {
    mockProgressSelectors.generateMockProgressData.mockReturnValue({
      analyses: [],
      metrics: mockMetrics,
      chartData: mockChartData,
      weeklyData: mockWeeklyData
    })

    render(<ProgressPage />)

    await waitFor(() => {
      expect(screen.getByText('Progress Overview')).toBeInTheDocument()
    })

    // Check for chart components
    expect(screen.getByText('Score Trends Over Time')).toBeInTheDocument()
    expect(screen.getByText('Weekly Activity')).toBeInTheDocument()
    expect(screen.getAllByTestId('responsive-container')).toHaveLength(2)
    expect(screen.getByTestId('line-chart')).toBeInTheDocument()
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument()
  })

  it('should show detailed metrics section', async () => {
    mockProgressSelectors.generateMockProgressData.mockReturnValue({
      analyses: [],
      metrics: mockMetrics,
      chartData: mockChartData,
      weeklyData: mockWeeklyData
    })

    render(<ProgressPage />)

    await waitFor(() => {
      expect(screen.getByText('Detailed Performance Metrics')).toBeInTheDocument()
    })

    // Check detailed metrics
    expect(screen.getByText('Average Clarity')).toBeInTheDocument()
    expect(screen.getByText('Average Structure')).toBeInTheDocument()
    expect(screen.getByText('Avg Filler Score')).toBeInTheDocument()
    
    // Check metric values
    expect(screen.getByText('7.5')).toBeInTheDocument() // Clarity score
    expect(screen.getByText('8')).toBeInTheDocument() // Structure score
    expect(screen.getByText('3.2')).toBeInTheDocument() // Filler score
  })

  it('should show empty state when no analyses', async () => {
    const emptyMetrics = {
      ...mockMetrics,
      totalAnalyses: 0
    }

    mockProgressSelectors.generateMockProgressData.mockReturnValue({
      analyses: [],
      metrics: emptyMetrics,
      chartData: [],
      weeklyData: []
    })

    render(<ProgressPage />)

    await waitFor(() => {
      expect(screen.getByText('No progress data yet')).toBeInTheDocument()
    })

    expect(screen.getByText('Complete some speech analyses to see your progress tracking')).toBeInTheDocument()
    expect(screen.getByText('Start Analyzing')).toBeInTheDocument()
  })

  it('should handle error state', async () => {
    mockAuthAPI.getCurrentUser.mockRejectedValue(new Error('API Error'))

    render(<ProgressPage />)

    await waitFor(() => {
      expect(screen.getByText('Failed to load progress data')).toBeInTheDocument()
    })

    expect(screen.getByText('Back to Dashboard')).toBeInTheDocument()
  })

  it('should show mock mode toggle in development', async () => {
    process.env.PROGRESS_UI = '1'
    
    mockProgressSelectors.generateMockProgressData.mockReturnValue({
      analyses: [],
      metrics: mockMetrics,
      chartData: mockChartData,
      weeklyData: mockWeeklyData
    })

    render(<ProgressPage />)

    await waitFor(() => {
      expect(screen.getByText('Mock Data')).toBeInTheDocument()
    })
  })

  it('should display improvement trend correctly', async () => {
    const negativeMetrics = {
      ...mockMetrics,
      improvementTrend: -5.5
    }

    mockProgressSelectors.generateMockProgressData.mockReturnValue({
      analyses: [],
      metrics: negativeMetrics,
      chartData: mockChartData,
      weeklyData: mockWeeklyData
    })

    render(<ProgressPage />)

    await waitFor(() => {
      expect(screen.getByText('5.5%')).toBeInTheDocument() // Shows absolute value
    })
  })

  it('should handle real data mode', async () => {
    process.env.NODE_ENV = 'production'
    process.env.PROGRESS_UI = '0'

    mockAuthAPI.getCurrentUser.mockResolvedValue(mockUser)
    mockSpeechesAPI.getRecentAnalyses.mockResolvedValue([])
    mockProgressSelectors.selectProgressData.mockReturnValue(mockMetrics)
    mockProgressSelectors.selectChartData.mockReturnValue(mockChartData)
    mockProgressSelectors.selectWeeklyProgress.mockReturnValue(mockWeeklyData)

    render(<ProgressPage />)

    await waitFor(() => {
      expect(screen.getByText('Progress Overview')).toBeInTheDocument()
    })

    expect(mockAuthAPI.getCurrentUser).toHaveBeenCalled()
    expect(mockSpeechesAPI.getRecentAnalyses).toHaveBeenCalledWith(mockUser.id, 100)
  })
})