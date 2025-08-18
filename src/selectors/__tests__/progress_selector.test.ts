/**
 * Tests for progress selectors
 */

import {
  selectProgressData,
  selectChartData,
  selectWeeklyProgress,
  generateMockProgressData,
  type Analysis
} from '../progress'

// Mock data for testing
const createMockAnalysis = (
  overrides: Partial<Analysis> = {}
): Analysis => ({
  speech_id: 'speech-1',
  analysis_id: 'analysis-1',
  word_count: 500,
  clarity_score: 7.5,
  structure_score: 8.0,
  filler_words_rating: 3,
  feedback: 'Good analysis',
  created_at: '2024-01-15T10:00:00Z',
  title: 'Test Speech',
  source_type: 'text',
  ...overrides
})

describe('selectProgressData', () => {
  it('should return empty metrics for empty array', () => {
    const result = selectProgressData([])
    
    expect(result).toEqual({
      totalAnalyses: 0,
      averageClarity: 0,
      averageStructure: 0,
      averageFiller: 0,
      totalWords: 0,
      improvementTrend: 0,
      recentActivity: 0
    })
  })

  it('should return empty metrics for null/undefined input', () => {
    const result = selectProgressData(null as any)
    
    expect(result.totalAnalyses).toBe(0)
    expect(result.averageClarity).toBe(0)
  })

  it('should calculate correct averages with valid data', () => {
    const analyses = [
      createMockAnalysis({ clarity_score: 8, structure_score: 7, filler_words_rating: 2, word_count: 300 }),
      createMockAnalysis({ clarity_score: 6, structure_score: 9, filler_words_rating: 4, word_count: 400 })
    ]

    const result = selectProgressData(analyses)

    expect(result.totalAnalyses).toBe(2)
    expect(result.averageClarity).toBe(7.0) // (8 + 6) / 2
    expect(result.averageStructure).toBe(8.0) // (7 + 9) / 2
    expect(result.averageFiller).toBe(3.0) // (2 + 4) / 2
    expect(result.totalWords).toBe(700) // 300 + 400
  })

  it('should handle missing scores gracefully', () => {
    const analyses = [
      createMockAnalysis({ clarity_score: undefined, structure_score: 8, word_count: 300 }),
      createMockAnalysis({ clarity_score: 6, structure_score: undefined, word_count: 400 }),
      createMockAnalysis({ clarity_score: undefined, structure_score: undefined, word_count: 200 })
    ]

    const result = selectProgressData(analyses)

    expect(result.totalAnalyses).toBe(3)
    expect(result.averageClarity).toBe(6.0) // Only one valid score
    expect(result.averageStructure).toBe(8.0) // Only one valid score
    expect(result.totalWords).toBe(900)
  })

  it('should calculate improvement trend correctly', () => {
    const analyses = Array.from({ length: 10 }, (_, i) => 
      createMockAnalysis({
        speech_id: `speech-${i}`,
        analysis_id: `analysis-${i}`,
        clarity_score: 5 + i * 0.3, // Improving trend
        structure_score: 6 + i * 0.2,
        created_at: new Date(2024, 0, i + 1).toISOString()
      })
    )

    const result = selectProgressData(analyses)
    
    // Should show positive improvement
    expect(result.improvementTrend).toBeGreaterThan(0)
  })

  it('should calculate recent activity correctly', () => {
    const now = new Date()
    const lastWeek = new Date(now)
    lastWeek.setDate(now.getDate() - 3) // 3 days ago
    
    const analyses = [
      createMockAnalysis({ created_at: lastWeek.toISOString() }), // Recent
      createMockAnalysis({ created_at: '2024-01-01T10:00:00Z' }) // Old
    ]

    const result = selectProgressData(analyses)
    
    expect(result.recentActivity).toBe(1) // Only one recent analysis
  })
})

describe('selectChartData', () => {
  it('should return empty array for empty input', () => {
    const result = selectChartData([])
    expect(result).toEqual([])
  })

  it('should group analyses by date correctly', () => {
    const analyses = [
      createMockAnalysis({ 
        created_at: '2024-01-15T10:00:00Z',
        clarity_score: 8,
        structure_score: 7
      }),
      createMockAnalysis({ 
        created_at: '2024-01-15T14:00:00Z', // Same date
        clarity_score: 6,
        structure_score: 9
      }),
      createMockAnalysis({ 
        created_at: '2024-01-16T10:00:00Z',
        clarity_score: 7,
        structure_score: 8
      })
    ]

    const result = selectChartData(analyses)

    expect(result).toHaveLength(2) // Two unique dates
    expect(result[0].date).toBe('2024-01-15')
    expect(result[0].clarity).toBe(7.0) // Average of 8 and 6
    expect(result[0].structure).toBe(8.0) // Average of 7 and 9
    expect(result[1].date).toBe('2024-01-16')
  })

  it('should handle missing dates gracefully', () => {
    const analyses = [
      createMockAnalysis({ created_at: undefined as any }),
      createMockAnalysis({ created_at: '2024-01-15T10:00:00Z' })
    ]

    const result = selectChartData(analyses)
    
    expect(result).toHaveLength(1) // Only one valid date
  })
})

describe('selectWeeklyProgress', () => {
  it('should return empty array for empty input', () => {
    const result = selectWeeklyProgress([])
    expect(result).toEqual([])
  })

  it('should group analyses by week correctly', () => {
    const analyses = [
      createMockAnalysis({ 
        created_at: '2024-01-15T10:00:00Z', // Monday
        clarity_score: 8,
        structure_score: 7
      }),
      createMockAnalysis({ 
        created_at: '2024-01-17T10:00:00Z', // Wednesday same week
        clarity_score: 6,
        structure_score: 9
      }),
      createMockAnalysis({ 
        created_at: '2024-01-22T10:00:00Z', // Next week
        clarity_score: 7,
        structure_score: 8
      })
    ]

    const result = selectWeeklyProgress(analyses)

    expect(result).toHaveLength(2) // Two different weeks
    expect(result[0].analyses).toBe(2) // Two analyses in first week
    expect(result[1].analyses).toBe(1) // One analysis in second week
  })

  it('should limit to last 8 weeks', () => {
    const analyses = Array.from({ length: 20 }, (_, i) => {
      const date = new Date()
      date.setDate(date.getDate() - (i * 7)) // One analysis per week, going back
      return createMockAnalysis({ 
        created_at: date.toISOString(),
        speech_id: `speech-${i}`,
        analysis_id: `analysis-${i}`
      })
    })

    const result = selectWeeklyProgress(analyses)
    
    expect(result.length).toBeLessThanOrEqual(8)
  })
})

describe('generateMockProgressData', () => {
  it('should generate valid mock data', () => {
    const mockData = generateMockProgressData()

    expect(mockData.analyses).toHaveLength(15)
    expect(mockData.metrics.totalAnalyses).toBe(15)
    expect(mockData.chartData.length).toBeGreaterThan(0)
    expect(mockData.weeklyData.length).toBeGreaterThan(0)

    // Check that analyses have improving scores
    const firstAnalysis = mockData.analyses[0]
    const lastAnalysis = mockData.analyses[mockData.analyses.length - 1]
    
    expect(lastAnalysis.clarity_score).toBeGreaterThan(firstAnalysis.clarity_score!)
  })

  it('should generate data with consistent types', () => {
    const mockData = generateMockProgressData()

    mockData.analyses.forEach(analysis => {
      expect(typeof analysis.speech_id).toBe('string')
      expect(typeof analysis.analysis_id).toBe('string')
      expect(typeof analysis.word_count).toBe('number')
      expect(typeof analysis.clarity_score).toBe('number')
      expect(typeof analysis.structure_score).toBe('number')
      expect(typeof analysis.created_at).toBe('string')
    })

    expect(typeof mockData.metrics.totalAnalyses).toBe('number')
    expect(typeof mockData.metrics.averageClarity).toBe('number')
    expect(typeof mockData.metrics.improvementTrend).toBe('number')
  })
})