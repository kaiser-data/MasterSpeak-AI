'use client'

import { useState, useEffect } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  ArrowLeft,
  Mic,
  Calendar,
  BarChart3,
  FileText,
  Loader2,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import Link from 'next/link'

import { 
  getAnalysesPage, 
  formatRelativeTime, 
  truncateText,
  type PaginatedAnalysesResponse 
} from '@/services/analyses-mock'

export default function AnalysesPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  
  const [analysesData, setAnalysesData] = useState<PaginatedAnalysesResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Get current page from URL params
  const currentPage = parseInt(searchParams?.get('page') || '1', 10)

  useEffect(() => {
    const fetchAnalyses = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const data = await getAnalysesPage(currentPage, 20)
        setAnalysesData(data)
        
      } catch (error) {
        console.error('Failed to fetch analyses:', error)
        setError(error instanceof Error ? error.message : 'Failed to load analyses')
      } finally {
        setLoading(false)
      }
    }
    
    fetchAnalyses()
  }, [currentPage])
  
  // Handle page navigation
  const goToPage = (page: number) => {
    const params = new URLSearchParams(searchParams || '')
    params.set('page', page.toString())
    router.push(`/dashboard/analyses?${params.toString()}`)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="animate-spin h-12 w-12 text-primary-600 mx-auto mb-4" />
          <p className="text-slate-600 dark:text-slate-400">Loading analyses...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <Link href="/dashboard" className="btn-primary">
            Back to Dashboard
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
              <Link href="/dashboard" className="flex items-center text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100">
                <ArrowLeft className="h-5 w-5 mr-2" />
                Back to Dashboard
              </Link>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-slate-600 dark:text-slate-400">
                {analysesData ? `Page ${currentPage} of ${analysesData.total_pages}` : ''}
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
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-2">
            All Analyses
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Complete history of your speech analyses and feedback
            {analysesData && (
              <span className="ml-2 text-sm">
                ({analysesData.total} total)
              </span>
            )}
          </p>
        </motion.div>

        {!analysesData || analysesData.items.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-12"
          >
            <BarChart3 className="h-16 w-16 text-slate-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-slate-900 dark:text-slate-100 mb-2">
              No analyses yet
            </h3>
            <p className="text-slate-600 dark:text-slate-400 mb-6">
              Start analyzing your speeches to see results here
            </p>
            <Link href="/dashboard" className="btn-primary">
              Create Your First Analysis
            </Link>
          </motion.div>
        ) : (
          <>
            <div className="space-y-4">
              {analysesData.items.map((analysis, index) => (
                <motion.div
                  key={analysis.analysis_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="card hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => router.push(`/dashboard/analyses/${analysis.analysis_id}`)}
                  data-testid="analysis-item"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4 flex-1">
                      <div className="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
                        <FileText className="h-6 w-6 text-primary-600" />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 truncate">
                          {analysis.speech_title}
                        </h3>
                        <div className="flex items-center space-x-4 mt-1">
                          <div className="flex items-center text-sm text-slate-500 dark:text-slate-400">
                            <Calendar className="h-4 w-4 mr-1" />
                            {formatRelativeTime(analysis.created_at)}
                          </div>
                          <div className="text-sm text-slate-500 dark:text-slate-400">
                            {analysis.metrics.word_count} words
                          </div>
                        </div>
                        {analysis.summary && (
                          <p className="text-sm text-slate-600 dark:text-slate-400 mt-2 line-clamp-2">
                            {truncateText(analysis.summary, 150)}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-6 ml-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                          {analysis.metrics.clarity_score}
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">Clarity</div>
                      </div>
                      
                      <div className="text-center">
                        <div className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                          {analysis.metrics.structure_score}
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">Structure</div>
                      </div>
                      
                      <div className="text-center">
                        <div className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                          {analysis.metrics.filler_word_count}
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">Fillers</div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
            
            {/* Pagination */}
            {analysesData.total_pages > 1 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="flex items-center justify-center space-x-2 mt-8"
              >
                <button
                  onClick={() => goToPage(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="flex items-center px-3 py-2 text-sm font-medium text-slate-500 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 hover:text-slate-700 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-slate-800 dark:border-slate-600 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-slate-300"
                >
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Previous
                </button>
                
                <div className="flex items-center space-x-1">
                  {Array.from({ length: analysesData.total_pages }, (_, i) => i + 1)
                    .filter(page => {
                      // Show first page, last page, current page, and pages around current
                      return page === 1 || 
                             page === analysesData.total_pages || 
                             Math.abs(page - currentPage) <= 1
                    })
                    .map((page, index, array) => {
                      // Add ellipsis if there's a gap
                      const showEllipsis = index > 0 && page - array[index - 1] > 1
                      return (
                        <div key={page} className="flex items-center">
                          {showEllipsis && (
                            <span className="px-2 py-1 text-slate-400">...</span>
                          )}
                          <button
                            onClick={() => goToPage(page)}
                            className={`px-3 py-2 text-sm font-medium rounded-lg ${
                              page === currentPage
                                ? 'bg-primary-600 text-white'
                                : 'text-slate-500 bg-white border border-slate-300 hover:bg-slate-50 hover:text-slate-700 dark:bg-slate-800 dark:border-slate-600 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-slate-300'
                            }`}
                          >
                            {page}
                          </button>
                        </div>
                      )
                    })}
                </div>
                
                <button
                  onClick={() => goToPage(currentPage + 1)}
                  disabled={currentPage === analysesData.total_pages}
                  className="flex items-center px-3 py-2 text-sm font-medium text-slate-500 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 hover:text-slate-700 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-slate-800 dark:border-slate-600 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-slate-300"
                >
                  Next
                  <ChevronRight className="h-4 w-4 ml-1" />
                </button>
              </motion.div>
            )}
          </>
        )}
      </main>
    </div>
  )
}