// src/services/analyses-mock.ts
// Mock implementation for Agent A APIs until backend is ready

export interface AnalysisMetrics {
  word_count: number
  clarity_score: number
  structure_score: number
  filler_word_count: number
}

export interface AnalysisListItem {
  analysis_id: string
  speech_id: string
  speech_title: string
  summary?: string
  metrics: AnalysisMetrics
  created_at: string
}

export interface PaginatedAnalysesResponse {
  items: AnalysisListItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface AnalysisDetails {
  analysis_id: string
  speech_id: string
  user_id: string
  speech_title: string
  speech_content: string
  transcript?: string
  summary?: string
  metrics: AnalysisMetrics
  feedback: string
  created_at: string
  updated_at: string
}

// Mock data generator
function generateMockAnalysis(index: number): AnalysisListItem {
  const titles = [
    'Product Launch Presentation',
    'Quarterly Sales Review', 
    'Team Building Speech',
    'Technical Deep Dive',
    'Customer Success Story',
    'Market Analysis Report',
    'Innovation Showcase',
    'Leadership Vision',
    'Project Milestone Update',
    'Strategic Planning Session'
  ]
  
  const baseDate = new Date('2024-01-01')
  const createdAt = new Date(baseDate.getTime() + (index * 24 * 60 * 60 * 1000))
  
  return {
    analysis_id: `analysis-${String(index + 1).padStart(3, '0')}`,
    speech_id: `speech-${String(index + 1).padStart(3, '0')}`,
    speech_title: titles[index % titles.length] + ` #${Math.floor(index / titles.length) + 1}`,
    summary: index % 3 === 0 ? `Summary for analysis ${index + 1}: This speech demonstrates strong communication skills with clear structure and engaging delivery.` : undefined,
    metrics: {
      word_count: 150 + Math.floor(Math.random() * 300),
      clarity_score: Math.round((7 + Math.random() * 3) * 10) / 10,
      structure_score: Math.round((6.5 + Math.random() * 3.5) * 10) / 10,
      filler_word_count: Math.floor(Math.random() * 8)
    },
    created_at: createdAt.toISOString()
  }
}

function generateMockAnalysisDetails(analysisId: string): AnalysisDetails {
  const analysis = generateMockAnalysis(parseInt(analysisId.split('-')[1]) - 1)
  
  return {
    ...analysis,
    user_id: 'user-123',
    speech_content: 'redacted_for_privacy',
    transcript: Math.random() > 0.5 ? `This is a mock transcript for ${analysis.speech_title}. It contains the full spoken content of the speech for analysis purposes.` : undefined,
    feedback: `Detailed AI feedback for ${analysis.speech_title}: Your speech shows excellent clarity and structure. The main points are well-organized and your delivery is engaging. Consider reducing filler words for even better impact.`,
    updated_at: analysis.created_at
  }
}

/**
 * Mock implementation of getAnalysesPage
 */
export async function getAnalysesPage(
  page: number = 1, 
  limit: number = 20
): Promise<PaginatedAnalysesResponse> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 300 + Math.random() * 200))
  
  // Simulate occasional errors in development
  if (process.env.NODE_ENV === 'development' && Math.random() < 0.05) {
    throw new Error('Mock API error: Network timeout')
  }
  
  const total = 47 // Mock total count
  const totalPages = Math.ceil(total / limit)
  const startIndex = (page - 1) * limit
  const endIndex = Math.min(startIndex + limit, total)
  
  const items: AnalysisListItem[] = []
  for (let i = startIndex; i < endIndex; i++) {
    items.push(generateMockAnalysis(i))
  }
  
  return {
    items,
    total,
    page,
    page_size: limit,
    total_pages: totalPages
  }
}

/**
 * Mock implementation of getAnalysisDetails
 */
export async function getAnalysisDetails(analysisId: string): Promise<AnalysisDetails> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 200 + Math.random() * 100))
  
  // Simulate not found error for invalid IDs
  if (!analysisId.startsWith('analysis-')) {
    throw new Error('Analysis not found')
  }
  
  return generateMockAnalysisDetails(analysisId)
}

/**
 * Format a date to a human-readable relative time
 */
export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffMinutes = Math.floor(diffMs / (1000 * 60))

  if (diffDays > 7) {
    return date.toLocaleDateString()
  } else if (diffDays > 0) {
    return `${diffDays} day${diffDays === 1 ? '' : 's'} ago`
  } else if (diffHours > 0) {
    return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`
  } else if (diffMinutes > 0) {
    return `${diffMinutes} minute${diffMinutes === 1 ? '' : 's'} ago`
  } else {
    return 'Just now'
  }
}

/**
 * Truncate text to a maximum length with ellipsis
 */
export function truncateText(text: string, maxLength: number = 100): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength).trim() + '...'
}