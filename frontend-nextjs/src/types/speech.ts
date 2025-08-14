export interface Speech {
  id: string
  user_id: string
  title: string
  content: string
  transcription?: string  // For audio files
  source_type: 'TEXT' | 'AUDIO' | 'VIDEO'
  created_at: string
  updated_at?: string
}

export interface SpeechAnalysis {
  id: string
  speech_id: string
  word_count: number
  clarity_score: number
  structure_score: number
  filler_word_count: number
  feedback: string
  prompt: string
  created_at: string
}

export interface AnalysisResponse {
  speech_id: string
  analysis_id?: string
  word_count?: number
  clarity_score?: number
  structure_score?: number
  filler_words_rating?: number
  feedback?: string
  created_at?: string
  transcription?: string  // For audio analysis results
  source_type?: string
  analysis?: {
    clarity_score: number
    structure_score: number
    filler_word_count: number
    feedback: string
  }
  success?: boolean
}

export interface SpeechUpload {
  file?: File
  text?: string
  title?: string
  user_id: string
  prompt_type: string
}

export interface AudioRecordingState {
  isRecording: boolean
  isPaused: boolean
  duration: number
  audioBlob?: Blob
  audioUrl?: string
}

export interface AnalysisMetrics {
  clarity_score: number
  structure_score: number
  filler_words_rating: number
  word_count: number
  estimated_duration?: number
}

export interface UserStatistics {
  user_id: string
  email: string
  full_name?: string
  total_speeches: number
  total_words_analyzed: number
  average_words_per_speech: number
  is_active: boolean
  created_at?: string
}