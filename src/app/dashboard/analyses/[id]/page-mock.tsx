'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  ArrowLeft,
  Calendar,
  FileText,
  Loader2,
  BarChart3,
  Target,
  Mic
} from 'lucide-react'
import Link from 'next/link'

import { getAnalysisDetails, formatRelativeTime, type AnalysisDetails } from '@/services/analyses-mock'

export default function AnalysisDetailPage() {
  const params = useParams()
  const router = useRouter()
  const analysisId = params?.id as string

  const [analysis, setAnalysis] = useState<AnalysisDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const data = await getAnalysisDetails(analysisId)
        setAnalysis(data)
        
      } catch (error) {
        console.error('Failed to fetch analysis:', error)
        setError(error instanceof Error ? error.message : 'Failed to load analysis')
      } finally {
        setLoading(false)
      }
    }
    
    if (analysisId) {
      fetchAnalysis()
    }
  }, [analysisId])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="animate-spin h-12 w-12 text-primary-600 mx-auto mb-4" />
          <p className="text-slate-600 dark:text-slate-400">Loading analysis...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <Link href="/dashboard/analyses" className="btn-primary">
            Back to Analyses
          </Link>
        </div>
      </div>
    )
  }

  if (!analysis) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-slate-600 dark:text-slate-400 mb-4">Analysis not found</p>
          <Link href="/dashboard/analyses" className="btn-primary">
            Back to Analyses
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 shadow-sm border-b border-slate-200 dark:border-slate-700">
        <div className="container-responsive">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard/analyses" className="flex items-center text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100">
                <ArrowLeft className="h-5 w-5 mr-2" />
                Back to Analyses
              </Link>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-slate-600 dark:text-slate-400">
                Analysis Details
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="container-responsive py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Analysis Header */}
          <div className="card">
            <div className="flex items-start space-x-4">
              <div className="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
                <FileText className="h-8 w-8 text-primary-600" />
              </div>
              
              <div className="flex-1">
                <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-2">
                  {analysis.speech_title}
                </h1>
                <div className="flex items-center space-x-4 text-sm text-slate-500 dark:text-slate-400">
                  <div className="flex items-center">
                    <Calendar className="h-4 w-4 mr-1" />
                    {formatRelativeTime(analysis.created_at)}
                  </div>
                  <div>
                    {analysis.metrics.word_count} words
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                title: 'Clarity Score',
                value: analysis.metrics.clarity_score,
                max: 10,
                color: 'text-blue-600',
                bgColor: 'bg-blue-100 dark:bg-blue-900/30',
              },
              {
                title: 'Structure Score',
                value: analysis.metrics.structure_score,
                max: 10,
                color: 'text-green-600',
                bgColor: 'bg-green-100 dark:bg-green-900/30',
              },
              {
                title: 'Filler Words',
                value: analysis.metrics.filler_word_count,
                max: null,
                color: 'text-orange-600',
                bgColor: 'bg-orange-100 dark:bg-orange-900/30',
              },
            ].map((metric, index) => (
              <motion.div
                key={metric.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="card-hover"
              >
                <div className="flex items-center">
                  <div className={`p-3 rounded-lg ${metric.bgColor} mr-4`}>
                    <BarChart3 className={`h-6 w-6 ${metric.color}`} />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
                      {metric.title}
                    </p>
                    <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                      {metric.value}{metric.max ? `/${metric.max}` : ''}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Transcript */}
          {analysis.transcript && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="card"
            >
              <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 mb-4 flex items-center">
                <Mic className="h-5 w-5 mr-2 text-primary-600" />
                Transcript
              </h2>
              <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
                  {analysis.transcript}
                </p>
              </div>
            </motion.div>
          )}

          {/* Feedback */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="card"
          >
            <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 mb-4">
              AI Feedback
            </h2>
            <div className="prose prose-slate dark:prose-invert max-w-none">
              <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
                {analysis.feedback}
              </p>
            </div>
          </motion.div>

          {/* Summary */}
          {analysis.summary && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="card"
            >
              <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 mb-4">
                Summary
              </h2>
              <div className="prose prose-slate dark:prose-invert max-w-none">
                <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
                  {analysis.summary}
                </p>
              </div>
            </motion.div>
          )}

          {/* Future Features Placeholder */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="card bg-slate-50 dark:bg-slate-800/50 border-dashed"
          >
            <div className="text-center py-8">
              <p className="text-slate-500 dark:text-slate-400 mb-2">
                🚧 More features coming soon
              </p>
              <p className="text-sm text-slate-400 dark:text-slate-500">
                Export options and sharing will be available here
              </p>
            </div>
          </motion.div>
        </motion.div>
      </main>
    </div>
  )
}