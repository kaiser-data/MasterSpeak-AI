import { http, HttpResponse } from 'msw'
import type { Analysis } from '@/services/analyses'

// Mock data for testing
const mockAnalyses: Analysis[] = [
  {
    analysis_id: 'analysis-1',
    speech_id: 'speech-1',
    user_id: 'user-1',
    transcript: 'Good morning everyone. Today I want to discuss our quarterly results and the strategic direction we\'re taking for the next quarter. Our team has achieved remarkable growth, with a 25% increase in revenue compared to the same period last year. This success is due to our dedicated team members who have consistently delivered exceptional work. However, we still face challenges in customer retention and market expansion. Moving forward, we need to focus on improving our customer experience and developing innovative solutions that meet market demands.',
    summary: 'A quarterly business presentation discussing company growth, revenue increases, team performance, and strategic challenges in customer retention and market expansion.',
    metrics: {
      word_count: 156,
      clarity_score: 8.5,
      structure_score: 7.8,
      filler_word_count: 3
    },
    feedback: 'Your presentation demonstrates strong command of the subject matter with clear articulation of key business metrics. The logical flow from results to strategy is effective. Consider reducing filler words like "um" and "you know" to enhance professional delivery. Your enthusiasm for the team\'s achievements comes through well. To improve engagement, try incorporating more specific examples and data visualizations.',
    created_at: '2024-01-15T10:30:00Z',
    updated_at: '2024-01-15T10:35:00Z'
  },
  {
    analysis_id: 'analysis-2',
    speech_id: 'speech-2',
    user_id: 'user-1',
    transcript: 'We are excited to introduce our revolutionary new product that will transform how businesses manage their digital workflows. This innovative solution combines artificial intelligence with intuitive user experience design. Our research shows that current solutions in the market lack the flexibility and scalability that modern businesses require.',
    summary: 'A product launch presentation introducing an AI-powered business workflow management solution.',
    metrics: {
      word_count: 89,
      clarity_score: 9.2,
      structure_score: 8.1,
      filler_word_count: 1
    },
    feedback: 'Excellent opening with strong energy and clear value proposition. Your confidence in the product is evident and engaging. The structure progresses logically from problem to solution. Consider adding specific customer pain points and quantifiable benefits to strengthen the pitch.',
    created_at: '2024-01-12T14:20:00Z',
    updated_at: '2024-01-12T14:25:00Z'
  },
  {
    analysis_id: 'analysis-3',
    speech_id: 'speech-3',
    user_id: 'user-1',
    transcript: undefined, // Test case with no transcript
    summary: 'A technical presentation covering machine learning advancements and their applications in data analysis.',
    metrics: {
      word_count: 203,
      clarity_score: 7.5,
      structure_score: 8.9,
      filler_word_count: 8
    },
    feedback: 'Strong technical content with good depth of knowledge. The progression from basic concepts to advanced applications is well-structured. However, the pace could be slower for better audience comprehension. Reduce technical jargon when possible and include more practical examples.',
    created_at: '2024-01-10T09:15:00Z',
    updated_at: '2024-01-10T09:20:00Z'
  }
]

export const handlers = [
  // Get analysis by ID
  http.get('/api/v1/analyses/:id', async ({ params }) => {
    const { id } = params
    
    // Simulate loading delay
    await new Promise(resolve => setTimeout(resolve, Math.random() * 500 + 200))
    
    const analysis = mockAnalyses.find(a => a.analysis_id === id)
    
    if (!analysis) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Analysis not found' }),
        { 
          status: 404,
          headers: { 'Content-Type': 'application/json' }
        }
      )
    }

    // Simulate occasional server errors for testing error states (only 2% for better UX)
    if (Math.random() < 0.02) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Internal server error' }),
        { 
          status: 500,
          headers: { 'Content-Type': 'application/json' }
        }
      )
    }

    return HttpResponse.json(analysis, { 
      status: 200,
      headers: {
        'X-Request-ID': `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      }
    })
  }),

  // Get analyses list
  http.get('/api/v1/analyses', ({ request }) => {
    const url = new URL(request.url)
    const skip = parseInt(url.searchParams.get('skip') || '0', 10)
    const limit = parseInt(url.searchParams.get('limit') || '100', 10)
    
    const paginatedAnalyses = mockAnalyses.slice(skip, skip + limit)
    
    return HttpResponse.json(paginatedAnalyses, { status: 200 })
  }),

  // Get recent analyses
  http.get('/api/v1/analyses/recent', ({ request }) => {
    const url = new URL(request.url)
    const limit = parseInt(url.searchParams.get('limit') || '5', 10)
    
    const recentAnalyses = [...mockAnalyses]
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, limit)
    
    return HttpResponse.json(recentAnalyses, { status: 200 })
  }),

  // Delete analysis
  http.delete('/api/v1/analyses/:id', ({ params }) => {
    const { id } = params
    
    const analysisIndex = mockAnalyses.findIndex(a => a.analysis_id === id)
    
    if (analysisIndex === -1) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Analysis not found' }),
        { 
          status: 404,
          headers: { 'Content-Type': 'application/json' }
        }
      )
    }

    // Remove from mock data
    mockAnalyses.splice(analysisIndex, 1)
    
    return new HttpResponse(null, { status: 204 })
  }),

  // Transcribe audio
  http.post('/api/v1/transcription/transcribe', async ({ request }) => {
    const body = await request.json() as { audio_url: string; language?: string }
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))
    
    // Simulate occasional failures for testing error states
    if (Math.random() < 0.1) { // 10% chance of failure
      return new HttpResponse(
        JSON.stringify({ detail: 'Transcription service temporarily unavailable' }),
        { 
          status: 503,
          headers: { 'Content-Type': 'application/json' }
        }
      )
    }

    const mockTranscription = {
      transcript: 'This is a mock transcription of the uploaded audio. The system has processed the audio file and generated this text representation of the spoken content. This would normally contain the actual transcribed speech from the audio file.',
      confidence: 0.85 + Math.random() * 0.14, // 85-99% confidence
      duration: Math.floor(Math.random() * 300) + 30 // 30-330 seconds
    }
    
    return HttpResponse.json(mockTranscription, { 
      status: 200,
      headers: {
        'X-Request-ID': `transcribe-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      }
    })
  }),

  // Export analysis
  http.get('/api/v1/analyses/:id/export', ({ params, request }) => {
    const { id } = params
    const url = new URL(request.url)
    const format = url.searchParams.get('format') || 'pdf'
    
    const analysis = mockAnalyses.find(a => a.analysis_id === id)
    
    if (!analysis) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Analysis not found' }),
        { 
          status: 404,
          headers: { 'Content-Type': 'application/json' }
        }
      )
    }

    // Create mock file content based on format
    let content: string
    let mimeType: string
    
    switch (format) {
      case 'json':
        content = JSON.stringify(analysis, null, 2)
        mimeType = 'application/json'
        break
      case 'txt':
        content = `Analysis Report\n\nTitle: [Title]\nDate: ${analysis.created_at}\n\nTranscript:\n${analysis.transcript || 'Not available'}\n\nFeedback:\n${analysis.feedback}`
        mimeType = 'text/plain'
        break
      default: // pdf
        content = '%PDF-1.4 Mock PDF content for analysis export'
        mimeType = 'application/pdf'
    }
    
    return new HttpResponse(content, {
      status: 200,
      headers: {
        'Content-Type': mimeType,
        'Content-Disposition': `attachment; filename="analysis-${id}.${format}"`
      }
    })
  }),

  // Share analysis
  http.post('/api/v1/analyses/:id/share', async ({ params, request }) => {
    const { id } = params
    const body = await request.json() as { expires_in?: number } || {}
    
    const analysis = mockAnalyses.find(a => a.analysis_id === id)
    
    if (!analysis) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Analysis not found' }),
        { 
          status: 404,
          headers: { 'Content-Type': 'application/json' }
        }
      )
    }

    const shareToken = Math.random().toString(36).substr(2, 16)
    const shareUrl = `${typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000'}/shared/${shareToken}`
    
    return HttpResponse.json({ share_url: shareUrl }, { status: 200 })
  })
]