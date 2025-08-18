'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  ArrowLeft,
  Copy,
  Download,
  Share2,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  RefreshCw,
  Calendar,
  FileText,
  BarChart3,
  Mic,
  CheckCircle
} from 'lucide-react'
import toast from 'react-hot-toast'

import { 
  getAnalysisById, 
  formatRelativeTime, 
  getScoreColorClass, 
  calculateOverallScore,
  exportAnalysisPDF,
  createShareLink,
  downloadBlob,
  isExportEnabled
} from '@/services/analyses'
import type { Analysis } from '@/services/analyses'

export default function AnalysisDetailPage() {
  const params = useParams()
  const router = useRouter()
  const analysisId = params?.id as string

  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isTranscriptExpanded, setIsTranscriptExpanded] = useState(false)
  const [retryCount, setRetryCount] = useState(0)
  const [exportLoading, setExportLoading] = useState(false)
  const [shareLoading, setShareLoading] = useState(false)

  // Feature flag checks
  const isTranscriptUIEnabled = process.env.NEXT_PUBLIC_TRANSCRIPTION_UI === '1'
  const isExportFeatureEnabled = isExportEnabled()

  const fetchAnalysis = async (showRetryToast = false) => {
    try {
      setLoading(true)
      setError(null)
      
      if (showRetryToast) {
        toast.loading('Retrying...', { id: 'retry-toast' })
      }

      const analysisData = await getAnalysisById(analysisId)
      setAnalysis(analysisData)
      setRetryCount(0)
      
      if (showRetryToast) {
        toast.success('Analysis loaded successfully', { id: 'retry-toast' })
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load analysis'
      setError(errorMessage)
      setRetryCount(prev => prev + 1)
      
      if (showRetryToast) {
        toast.error('Failed to load analysis', { id: 'retry-toast' })
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (analysisId) {
      fetchAnalysis()
    }
  }, [analysisId])

  const handleCopyTranscript = async () => {
    if (!analysis?.transcript) {
      toast.error('No transcript available to copy')
      return
    }

    try {
      await navigator.clipboard.writeText(analysis.transcript)
      toast.success('Transcript copied to clipboard')
    } catch (err) {
      toast.error('Failed to copy transcript')
    }
  }

  const handleExport = async () => {
    if (!analysis || !isExportFeatureEnabled) {
      toast.error('Export functionality is not available')
      return
    }

    try {
      setExportLoading(true)
      
      // Get user preference for including transcript
      const includeTranscript = confirm('Include transcript in the PDF export?')
      
      toast.loading('Generating PDF...', { id: 'export-toast' })
      
      const pdfBlob = await exportAnalysisPDF(analysis.analysis_id, includeTranscript)
      
      // Generate filename with analysis date
      const date = new Date(analysis.created_at).toISOString().split('T')[0]
      const filename = `analysis-${date}-${analysis.analysis_id.slice(0, 8)}.pdf`
      
      downloadBlob(pdfBlob, filename)
      
      toast.success('PDF exported successfully', { id: 'export-toast' })
      
    } catch (error) {
      console.error('Export failed:', error)
      toast.error(error instanceof Error ? error.message : 'Export failed', { id: 'export-toast' })
    } finally {
      setExportLoading(false)
    }
  }

  const handleShare = async () => {
    if (!analysis || !isExportFeatureEnabled) {
      toast.error('Share functionality is not available')
      return
    }

    try {
      setShareLoading(true)
      
      toast.loading('Creating share link...', { id: 'share-toast' })
      
      const shareResponse = await createShareLink(analysis.analysis_id, 7) // 7 days expiry
      
      // Copy share URL to clipboard
      await navigator.clipboard.writeText(shareResponse.share_url)
      
      const expiryDate = new Date(shareResponse.expires_at).toLocaleDateString()
      
      toast.success(`Share link copied to clipboard! Expires: ${expiryDate}`, { 
        id: 'share-toast',
        duration: 5000
      })
      
    } catch (error) {
      console.error('Share failed:', error)
      
      if (error instanceof Error && error.message.includes('clipboard')) {
        toast.error('Share link created but clipboard copy failed', { id: 'share-toast' })
      } else {
        toast.error(error instanceof Error ? error.message : 'Share failed', { id: 'share-toast' })
      }
    } finally {
      setShareLoading(false)
    }
  }

  const handleRetry = () => {
    fetchAnalysis(true)
  }

  if (loading) {
    return (
      <div className="min-h-screen">
        {/* Header */}
        <header className="bg-white dark:bg-slate-800 shadow-sm border-b border-slate-200 dark:border-slate-700">
          <div className="container-responsive">
            <div className="flex items-center justify-between py-4">
              <button
                onClick={() => router.push('/dashboard/analyses')}
                className="flex items-center space-x-2 text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
              >
                <ArrowLeft className="h-5 w-5" />
                <span>Back to Analyses</span>
              </button>
            </div>
          </div>
        </header>

        {/* Loading State */}
        <main className="container-responsive py-8">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
              <p className="text-slate-600 dark:text-slate-400">Loading analysis...</p>
            </div>
          </div>
        </main>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen">
        {/* Header */}
        <header className="bg-white dark:bg-slate-800 shadow-sm border-b border-slate-200 dark:border-slate-700">
          <div className="container-responsive">
            <div className="flex items-center justify-between py-4">
              <button
                onClick={() => router.push('/dashboard/analyses')}
                className="flex items-center space-x-2 text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
              >
                <ArrowLeft className="h-5 w-5" />
                <span>Back to Analyses</span>
              </button>
            </div>
          </div>
        </header>

        {/* Error State */}
        <main className="container-responsive py-8">
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
                Failed to Load Analysis
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-6">
                {error}
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button
                  onClick={handleRetry}
                  className="btn-primary"
                  disabled={loading}
                >
                  <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                  Retry {retryCount > 0 && `(${retryCount})`}
                </button>
                <button
                  onClick={() => router.push('/dashboard/analyses')}
                  className="btn-outline"
                >
                  Back to Analyses
                </button>
              </div>
            </motion.div>
          </div>
        </main>
      </div>
    )
  }

  if (!analysis) {
    return (
      <div className="min-h-screen">
        {/* Header */}
        <header className="bg-white dark:bg-slate-800 shadow-sm border-b border-slate-200 dark:border-slate-700">
          <div className="container-responsive">
            <div className="flex items-center justify-between py-4">
              <button
                onClick={() => router.push('/dashboard/analyses')}
                className="flex items-center space-x-2 text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
              >
                <ArrowLeft className="h-5 w-5" />
                <span>Back to Analyses</span>
              </button>
            </div>
          </div>
        </header>

        {/* Not Found State */}
        <main className="container-responsive py-8">
          <div className="flex items-center justify-center min-h-[400px]">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center max-w-md"
            >
              <div className="bg-slate-100 dark:bg-slate-800 rounded-full p-3 w-16 h-16 mx-auto mb-4">
                <FileText className="h-10 w-10 text-slate-400" />
              </div>
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
                Analysis Not Found
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-6">
                The analysis you're looking for doesn't exist or you don't have permission to view it.
              </p>
              <button
                onClick={() => router.push('/dashboard/analyses')}
                className="btn-primary"
              >
                Back to Analyses
              </button>
            </motion.div>
          </div>
        </main>
      </div>
    )
  }

  const overallScore = calculateOverallScore(analysis.metrics)
  const hasTranscript = Boolean(analysis.transcript)

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 shadow-sm border-b border-slate-200 dark:border-slate-700">
        <div className="container-responsive">
          <div className="flex items-center justify-between py-4">
            <button
              onClick={() => router.push('/dashboard/analyses')}
              className="flex items-center space-x-2 text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
            >
              <ArrowLeft className="h-5 w-5" />
              <span>Back to Analyses</span>
            </button>

            {/* Actions - Only show if export is enabled */}
            {isExportFeatureEnabled && (
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleExport}
                  disabled={exportLoading || !analysis}
                  className="btn-outline"
                  title="Export Analysis as PDF"
                >
                  {exportLoading ? (
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Download className="h-4 w-4 mr-2" />
                  )}
                  {exportLoading ? 'Exporting...' : 'Export'}
                </button>
                <button
                  onClick={handleShare}
                  disabled={shareLoading || !analysis}
                  className="btn-outline"
                  title="Create shareable link"
                >
                  {shareLoading ? (
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Share2 className="h-4 w-4 mr-2" />
                  )}
                  {shareLoading ? 'Sharing...' : 'Share'}
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container-responsive py-8 space-y-8">
        {/* Overview Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-2">
                Analysis Details
              </h1>
              <p className="text-slate-600 dark:text-slate-400">
                Created {formatRelativeTime(analysis.created_at)}
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

        {/* Transcript Section - Only show when feature flag is enabled */}
        {isTranscriptUIEnabled && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
                  Transcript
                </h2>
                {hasTranscript && (
                  <span className="px-2 py-1 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300 text-xs font-medium rounded-full">
                    Available
                  </span>
                )}
              </div>
              <div className="flex items-center space-x-2">
                {hasTranscript && (
                  <button
                    onClick={handleCopyTranscript}
                    className="btn-outline btn-sm"
                    title="Copy transcript to clipboard"
                  >
                    <Copy className="h-4 w-4 mr-1" />
                    Copy
                  </button>
                )}
                <button
                  onClick={() => setIsTranscriptExpanded(!isTranscriptExpanded)}
                  className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400"
                  title={isTranscriptExpanded ? 'Collapse' : 'Expand'}
                >
                  {isTranscriptExpanded ? (
                    <ChevronUp className="h-5 w-5" />
                  ) : (
                    <ChevronDown className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>

            {hasTranscript ? (
              <motion.div
                initial={false}
                animate={{ height: isTranscriptExpanded ? 'auto' : '120px' }}
                className="overflow-hidden"
              >
                <div className={`bg-slate-50 dark:bg-slate-800 rounded-lg p-4 ${!isTranscriptExpanded ? 'relative' : ''}`}>
                  <p className="text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
                    {analysis.transcript}
                  </p>
                  {!isTranscriptExpanded && (
                    <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-slate-50 dark:from-slate-800 to-transparent pointer-events-none" />
                  )}
                </div>
              </motion.div>
            ) : (
              <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-8 text-center">
                <Mic className="h-12 w-12 text-slate-400 mx-auto mb-3" />
                <p className="text-slate-600 dark:text-slate-400">
                  No transcript available for this analysis
                </p>
              </div>
            )}
          </motion.div>
        )}

        {/* Performance Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
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
          transition={{ delay: 0.3 }}
          className="card"
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

        {/* Metadata */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-6">
            Metadata
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-center space-x-3">
              <div className="bg-slate-100 dark:bg-slate-800 rounded-lg p-2">
                <Calendar className="h-5 w-5 text-slate-600 dark:text-slate-400" />
              </div>
              <div>
                <div className="text-sm text-slate-500 dark:text-slate-400">Created</div>
                <div className="font-medium text-slate-900 dark:text-slate-100">
                  {new Date(analysis.created_at).toLocaleString()}
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <div className="bg-slate-100 dark:bg-slate-800 rounded-lg p-2">
                <FileText className="h-5 w-5 text-slate-600 dark:text-slate-400" />
              </div>
              <div>
                <div className="text-sm text-slate-500 dark:text-slate-400">Analysis ID</div>
                <div className="font-mono text-sm text-slate-900 dark:text-slate-100">
                  {analysis.analysis_id}
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <div className="bg-slate-100 dark:bg-slate-800 rounded-lg p-2">
                <Mic className="h-5 w-5 text-slate-600 dark:text-slate-400" />
              </div>
              <div>
                <div className="text-sm text-slate-500 dark:text-slate-400">Speech ID</div>
                <div className="font-mono text-sm text-slate-900 dark:text-slate-100">
                  {analysis.speech_id}
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <div className="bg-slate-100 dark:bg-slate-800 rounded-lg p-2">
                <Calendar className="h-5 w-5 text-slate-600 dark:text-slate-400" />
              </div>
              <div>
                <div className="text-sm text-slate-500 dark:text-slate-400">Last Updated</div>
                <div className="font-medium text-slate-900 dark:text-slate-100">
                  {new Date(analysis.updated_at).toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  )
}