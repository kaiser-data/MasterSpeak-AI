/**
 * Progress data selectors - tolerant to missing/incomplete metrics
 */

export interface Analysis {
  speech_id: string
  analysis_id: string
  word_count?: number
  clarity_score?: number
  structure_score?: number
  filler_words_rating?: number
  feedback?: string
  created_at: string
  title?: string
  source_type?: string
}

export interface ProgressMetrics {
  totalAnalyses: number
  averageClarity: number
  averageStructure: number
  averageFiller: number
  totalWords: number
  improvementTrend: number
  recentActivity: number
}

export interface ChartDataPoint {
  date: string
  clarity: number
  structure: number
  filler: number
  average: number
}

export interface WeeklyProgress {
  week: string
  analyses: number
  avgScore: number
}

/**
 * Extract progress metrics from analyses array
 * Tolerant to missing or incomplete data
 */
export const selectProgressData = (analyses: Analysis[]): ProgressMetrics => {
  if (!analyses || analyses.length === 0) {
    return {
      totalAnalyses: 0,
      averageClarity: 0,
      averageStructure: 0,
      averageFiller: 0,
      totalWords: 0,
      improvementTrend: 0,
      recentActivity: 0
    }
  }

  // Filter valid analyses with scores
  const validAnalyses = analyses.filter(a => 
    a && (a.clarity_score !== undefined || a.structure_score !== undefined)
  )

  if (validAnalyses.length === 0) {
    return {
      totalAnalyses: analyses.length,
      averageClarity: 0,
      averageStructure: 0,
      averageFiller: 0,
      totalWords: analyses.reduce((sum, a) => sum + (a?.word_count || 0), 0),
      improvementTrend: 0,
      recentActivity: 0
    }
  }

  // Calculate averages with null safety
  const clarityScores = validAnalyses.map(a => a.clarity_score || 0).filter(s => s > 0)
  const structureScores = validAnalyses.map(a => a.structure_score || 0).filter(s => s > 0)
  const fillerScores = validAnalyses.map(a => a.filler_words_rating || 0).filter(s => s >= 0)

  const averageClarity = clarityScores.length > 0 
    ? clarityScores.reduce((sum, score) => sum + score, 0) / clarityScores.length 
    : 0

  const averageStructure = structureScores.length > 0
    ? structureScores.reduce((sum, score) => sum + score, 0) / structureScores.length
    : 0

  const averageFiller = fillerScores.length > 0
    ? fillerScores.reduce((sum, score) => sum + score, 0) / fillerScores.length
    : 0

  // Calculate improvement trend (last 5 vs first 5 analyses)
  let improvementTrend = 0
  if (validAnalyses.length >= 6) {
    const recent = validAnalyses.slice(0, 5)
    const older = validAnalyses.slice(-5)
    
    const recentAvg = recent.reduce((sum, a) => {
      const clarity = a.clarity_score || 0
      const structure = a.structure_score || 0
      return sum + (clarity + structure) / 2
    }, 0) / recent.length

    const olderAvg = older.reduce((sum, a) => {
      const clarity = a.clarity_score || 0
      const structure = a.structure_score || 0
      return sum + (clarity + structure) / 2
    }, 0) / older.length

    improvementTrend = ((recentAvg - olderAvg) / olderAvg) * 100
  }

  // Recent activity (analyses in last 7 days)
  const lastWeek = new Date()
  lastWeek.setDate(lastWeek.getDate() - 7)
  
  const recentActivity = analyses.filter(a => {
    if (!a?.created_at) return false
    const analysisDate = new Date(a.created_at)
    return analysisDate >= lastWeek
  }).length

  return {
    totalAnalyses: analyses.length,
    averageClarity: Number(averageClarity.toFixed(1)),
    averageStructure: Number(averageStructure.toFixed(1)),
    averageFiller: Number(averageFiller.toFixed(1)),
    totalWords: analyses.reduce((sum, a) => sum + (a?.word_count || 0), 0),
    improvementTrend: Number(improvementTrend.toFixed(1)),
    recentActivity
  }
}

/**
 * Transform analyses into chart data points
 * Groups by date and calculates daily averages
 */
export const selectChartData = (analyses: Analysis[]): ChartDataPoint[] => {
  if (!analyses || analyses.length === 0) return []

  // Group analyses by date
  const grouped = analyses.reduce((acc, analysis) => {
    if (!analysis?.created_at) return acc
    
    const date = new Date(analysis.created_at).toISOString().split('T')[0]
    if (!acc[date]) {
      acc[date] = []
    }
    acc[date].push(analysis)
    return acc
  }, {} as Record<string, Analysis[]>)

  // Convert to chart data points
  const chartData: ChartDataPoint[] = Object.entries(grouped)
    .map(([date, dayAnalyses]) => {
      const validAnalyses = dayAnalyses.filter(a => 
        a.clarity_score !== undefined || a.structure_score !== undefined
      )

      if (validAnalyses.length === 0) {
        return {
          date,
          clarity: 0,
          structure: 0,
          filler: 0,
          average: 0
        }
      }

      const clarity = validAnalyses.reduce((sum, a) => sum + (a.clarity_score || 0), 0) / validAnalyses.length
      const structure = validAnalyses.reduce((sum, a) => sum + (a.structure_score || 0), 0) / validAnalyses.length
      const filler = validAnalyses.reduce((sum, a) => sum + (a.filler_words_rating || 0), 0) / validAnalyses.length
      const average = (clarity + structure) / 2

      return {
        date,
        clarity: Number(clarity.toFixed(1)),
        structure: Number(structure.toFixed(1)),
        filler: Number(filler.toFixed(1)),
        average: Number(average.toFixed(1))
      }
    })
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())

  return chartData
}

/**
 * Calculate weekly progress summary
 */
export const selectWeeklyProgress = (analyses: Analysis[]): WeeklyProgress[] => {
  if (!analyses || analyses.length === 0) return []

  const weeks: Record<string, Analysis[]> = {}
  
  analyses.forEach(analysis => {
    if (!analysis?.created_at) return
    
    const date = new Date(analysis.created_at)
    const weekStart = new Date(date)
    weekStart.setDate(date.getDate() - date.getDay()) // Start of week
    const weekKey = weekStart.toISOString().split('T')[0]
    
    if (!weeks[weekKey]) {
      weeks[weekKey] = []
    }
    weeks[weekKey].push(analysis)
  })

  return Object.entries(weeks)
    .map(([week, weekAnalyses]) => {
      const validAnalyses = weekAnalyses.filter(a => 
        a.clarity_score !== undefined || a.structure_score !== undefined
      )

      let avgScore = 0
      if (validAnalyses.length > 0) {
        const totalScore = validAnalyses.reduce((sum, a) => {
          const clarity = a.clarity_score || 0
          const structure = a.structure_score || 0
          return sum + (clarity + structure) / 2
        }, 0)
        avgScore = totalScore / validAnalyses.length
      }

      return {
        week: new Date(week).toLocaleDateString('en-US', { 
          month: 'short', 
          day: 'numeric' 
        }),
        analyses: weekAnalyses.length,
        avgScore: Number(avgScore.toFixed(1))
      }
    })
    .sort((a, b) => new Date(a.week).getTime() - new Date(b.week).getTime())
    .slice(-8) // Last 8 weeks
}

/**
 * Mock data generator for development
 */
export const generateMockProgressData = (): {
  analyses: Analysis[]
  metrics: ProgressMetrics
  chartData: ChartDataPoint[]
  weeklyData: WeeklyProgress[]
} => {
  const mockAnalyses: Analysis[] = []
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - 30) // Last 30 days

  // Generate 15 mock analyses
  for (let i = 0; i < 15; i++) {
    const date = new Date(startDate)
    date.setDate(date.getDate() + i * 2)
    
    mockAnalyses.push({
      speech_id: `speech-${i}`,
      analysis_id: `analysis-${i}`,
      word_count: Math.floor(Math.random() * 800) + 200,
      clarity_score: Math.floor(Math.random() * 4) + 6 + (i * 0.1), // Gradual improvement
      structure_score: Math.floor(Math.random() * 4) + 5 + (i * 0.15),
      filler_words_rating: Math.max(0, 10 - Math.floor(Math.random() * 3) - (i * 0.2)),
      feedback: `Analysis feedback for speech ${i + 1}`,
      created_at: date.toISOString(),
      title: `Speech Analysis ${i + 1}`,
      source_type: i % 3 === 0 ? 'audio' : 'text'
    })
  }

  return {
    analyses: mockAnalyses,
    metrics: selectProgressData(mockAnalyses),
    chartData: selectChartData(mockAnalyses),
    weeklyData: selectWeeklyProgress(mockAnalyses)
  }
}