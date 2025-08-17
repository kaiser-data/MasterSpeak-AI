'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  AlertCircle,
  RefreshCw,
  Calendar,
  FileText,
  BarChart3,
  Mic,
  CheckCircle,
  Lock,
  Share2,
  Eye
} from 'lucide-react'
import Link from 'next/link'
import toast from 'react-hot-toast'

import { 
  getSharedAnalysis,
  formatRelativeTime, 
  getScoreColorClass, 
  calculateOverallScore
} from '@/services/analyses'
import type { SharedAnalysisResponse } from '@/services/analyses'

export default function SharedAnalysisPage() {
  const params = useParams()
  const token = params?.token as string

  const [analysis, setAnalysis] = useState<SharedAnalysisResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSharedAnalysis = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const analysisData = await getSharedAnalysis(token)
        setAnalysis(analysisData)
        
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load shared analysis'
        setError(errorMessage)
      } finally {
        setLoading(false)
      }
    }

    if (token) {
      fetchSharedAnalysis()
    }
  }, [token])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
        {/* Header */}
        <header className="bg-white dark:bg-slate-800 shadow-sm border-b border-slate-200 dark:border-slate-700">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
                <Share2 className="h-6 w-6 text-primary-600" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
                  Shared Analysis
                </h1>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  MasterSpeak-AI Speech Analysis
                </p>
              </div>
            </div>
          </div>
        </header>

        {/* Loading State */}
        <main className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
              <p className="text-slate-600 dark:text-slate-400">Loading shared analysis...</p>
            </div>
          </div>
        </main>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
        {/* Header */}
        <header className="bg-white dark:bg-slate-800 shadow-sm border-b border-slate-200 dark:border-slate-700">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
                <AlertCircle className="h-6 w-6 text-red-600" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
                  Shared Analysis
                </h1>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  MasterSpeak-AI Speech Analysis
                </p>
              </div>
            </div>
          </div>
        </header>

        {/* Error State */}
        <main className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center min-h-[400px]">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center max-w-md"
            >
              <div className="bg-red-100 dark:bg-red-900/20 rounded-full p-3 w-16 h-16 mx-auto mb-4">
                <AlertCircle className="h-10 w-10 text-red-600 dark:text-red-400" />
              </div>
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
                Unable to Load Analysis
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-6">
                {error}
              </p>
              <div className="space-y-3">
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  This link may have expired or been revoked.
                </p>
                <Link href="/" className="btn-primary">
                  Visit MasterSpeak-AI
                </Link>
              </div>
            </motion.div>
          </div>
        </main>
      </div>
    )
  }

  if (!analysis) {
    return null
  }

  const overallScore = calculateOverallScore(analysis.metrics)

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 shadow-sm border-b border-slate-200 dark:border-slate-700">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
                <Share2 className="h-6 w-6 text-primary-600" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
                  Shared Analysis
                </h1>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  MasterSpeak-AI Speech Analysis
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2 text-sm text-slate-500 dark:text-slate-400">
              <Eye className="h-4 w-4" />
              <span>Read-only view</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 space-y-8">
        {/* Privacy Notice */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4"
        >
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <Lock className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h3 className="text-sm font-medium text-blue-900 dark:text-blue-100">
                Shared Analysis View
              </h3>
              <p className="text-sm text-blue-800 dark:text-blue-200">
                This is a shared, read-only view of a speech analysis. 
                {!analysis.transcript_included && " Transcript has been excluded for privacy."}
              </p>
            </div>
          </div>
        </motion.div>

        {/* Overview Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700 p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-2">
                Analysis Results
              </h2>
              <p className="text-slate-600 dark:text-slate-400">
                Analyzed {formatRelativeTime(analysis.created_at)}
              </p>
            </div>
            <div className="text-right">
              <div className="text-sm text-slate-500 dark:text-slate-400 mb-1">Overall Score</div>
              <div className={`text-3xl font-bold ${getScoreColorClass(overallScore)}`}>
                {overallScore.toFixed(1)}<span className="text-lg text-slate-400">/10</span>
              </div>
            </div>
          </div>

          {/* Summary */}
          {analysis.summary && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-3">
                Summary
              </h3>
              <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
                {analysis.summary}
              </p>
            </div>
          )}
        </motion.div>

        {/* Transcript Section - Only show if included */}
        {analysis.transcript_included && analysis.transcript && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700 p-6"
          >
            <div className="flex items-center space-x-3 mb-4">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
                Transcript
              </h2>
              <span className="px-2 py-1 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300 text-xs font-medium rounded-full">
                Included
              </span>
            </div>
            <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
              <p className="text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
                {analysis.transcript}
              </p>
            </div>
          </motion.div>
        )}

        {/* Performance Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700 p-6"
        >
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-6">
            Performance Metrics
          </h2>

          {analysis.metrics ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="bg-blue-100 dark:bg-blue-900/20 rounded-lg p-4 mb-3">
                  <BarChart3 className="h-8 w-8 text-blue-600 mx-auto" />
                </div>
                <div className="text-sm text-slate-500 dark:text-slate-400 mb-1">Clarity Score</div>
                <div className={`text-2xl font-bold ${getScoreColorClass(analysis.metrics.clarity_score)}`}>
                  {analysis.metrics.clarity_score.toFixed(1)}<span className="text-sm text-slate-400">/10</span>
                </div>
              </div>

              <div className="text-center">
                <div className="bg-green-100 dark:bg-green-900/20 rounded-lg p-4 mb-3">
                  <CheckCircle className="h-8 w-8 text-green-600 mx-auto" />
                </div>
                <div className="text-sm text-slate-500 dark:text-slate-400 mb-1">Structure Score</div>
                <div className={`text-2xl font-bold ${getScoreColorClass(analysis.metrics.structure_score)}`}>
                  {analysis.metrics.structure_score.toFixed(1)}<span className="text-sm text-slate-400">/10</span>
                </div>
              </div>

              <div className="text-center">
                <div className="bg-purple-100 dark:bg-purple-900/20 rounded-lg p-4 mb-3">
                  <FileText className="h-8 w-8 text-purple-600 mx-auto" />
                </div>
                <div className="text-sm text-slate-500 dark:text-slate-400 mb-1">Word Count</div>
                <div className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                  {analysis.metrics.word_count.toLocaleString()}
                </div>
              </div>

              <div className="text-center">
                <div className="bg-orange-100 dark:bg-orange-900/20 rounded-lg p-4 mb-3">
                  <AlertCircle className="h-8 w-8 text-orange-600 mx-auto" />
                </div>
                <div className="text-sm text-slate-500 dark:text-slate-400 mb-1">Filler Words</div>
                <div className={`text-2xl font-bold ${
                  analysis.metrics.filler_word_count <= 2 ? 'text-green-600' :
                  analysis.metrics.filler_word_count <= 5 ? 'text-yellow-600' :
                  analysis.metrics.filler_word_count <= 10 ? 'text-orange-600' : 'text-red-600'
                }`}>
                  {analysis.metrics.filler_word_count}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-8 text-center">
              <BarChart3 className="h-12 w-12 text-slate-400 mx-auto mb-3" />
              <p className="text-slate-600 dark:text-slate-400">
                No metrics available for this analysis
              </p>
            </div>
          )}
        </motion.div>

        {/* AI Feedback */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700 p-6"
        >
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-6">
            AI Feedback
          </h2>
          <div className="prose prose-slate dark:prose-invert max-w-none">
            <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
              {analysis.feedback}
            </p>
          </div>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="text-center py-8"
        >
          <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700 p-6">
            <div className="space-y-4">
              <div className="text-center">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2">
                  Get Your Own Speech Analysis
                </h3>
                <p className="text-slate-600 dark:text-slate-400 mb-4">
                  Improve your public speaking with AI-powered feedback and insights.
                </p>
                <Link 
                  href="/"
                  className="inline-flex items-center px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                  Try MasterSpeak-AI
                </Link>
              </div>
              <div className="text-xs text-slate-500 dark:text-slate-400 border-t border-slate-200 dark:border-slate-700 pt-4">
                <p>
                  Analysis ID: {analysis.analysis_id} • 
                  Created: {new Date(analysis.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  )
}