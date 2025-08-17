'use client'

import { useState, useEffect, Suspense } from 'react'
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
  ChevronRight,
  Search,
  Filter,
  X
} from 'lucide-react'
import Link from 'next/link'

import { 
  getAnalysesPage,
  searchAnalyses,
  formatRelativeTime, 
  truncateText,
  calculateOverallScore,
  getScoreColorClass,
  Analysis,
  AnalysisListResponse,
  AnalysisSearchParams
} from '@/services/analyses'

interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
}

function AnalysesPageContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  
  const [analysesData, setAnalysesData] = useState<AnalysisListResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showFilters, setShowFilters] = useState(false)
  
  // Search and filter state
  const [searchQuery, setSearchQuery] = useState(searchParams?.get('q') || '')
  const [minClarity, setMinClarity] = useState(searchParams?.get('min_clarity') || '')
  const [maxClarity, setMaxClarity] = useState(searchParams?.get('max_clarity') || '')
  const [minStructure, setMinStructure] = useState(searchParams?.get('min_structure') || '')
  const [maxStructure, setMaxStructure] = useState(searchParams?.get('max_structure') || '')
  const [startDate, setStartDate] = useState(searchParams?.get('start_date') || '')
  const [endDate, setEndDate] = useState(searchParams?.get('end_date') || '')
  
  // Get current page from URL params
  const currentPage = parseInt(searchParams?.get('page') || '1', 10)
  
  // Check if any filters are active
  const hasActiveFilters = searchQuery || minClarity || maxClarity || minStructure || maxStructure || startDate || endDate

  useEffect(() => {
    const fetchAnalyses = async () => {
      try {
        setLoading(true)
        setError(null)
        
        let data: AnalysisListResponse
        
        if (hasActiveFilters) {
          // Use search endpoint with filters
          const searchParams: AnalysisSearchParams = {
            page: currentPage,
            limit: 20
          }
          
          if (searchQuery) searchParams.q = searchQuery
          if (minClarity) searchParams.min_clarity = parseFloat(minClarity)
          if (maxClarity) searchParams.max_clarity = parseFloat(maxClarity)
          if (minStructure) searchParams.min_structure = parseFloat(minStructure)
          if (maxStructure) searchParams.max_structure = parseFloat(maxStructure)
          if (startDate) searchParams.start_date = startDate
          if (endDate) searchParams.end_date = endDate
          
          data = await searchAnalyses(searchParams)
        } else {
          // Use regular list endpoint
          data = await getAnalysesPage(currentPage, 20)
        }
        
        setAnalysesData(data)
        
      } catch (error) {
        console.error('Failed to fetch analyses:', error)
        setError(error instanceof Error ? error.message : 'Failed to load analyses')
      } finally {
        setLoading(false)
      }
    }
    
    fetchAnalyses()
  }, [currentPage, searchQuery, minClarity, maxClarity, minStructure, maxStructure, startDate, endDate, hasActiveFilters])
  
  // Handle search and filters
  const applyFilters = () => {
    const params = new URLSearchParams()
    
    if (searchQuery) params.set('q', searchQuery)
    if (minClarity) params.set('min_clarity', minClarity)
    if (maxClarity) params.set('max_clarity', maxClarity)
    if (minStructure) params.set('min_structure', minStructure)
    if (maxStructure) params.set('max_structure', maxStructure)
    if (startDate) params.set('start_date', startDate)
    if (endDate) params.set('end_date', endDate)
    
    params.set('page', '1') // Reset to first page
    router.push(`/dashboard/analyses?${params.toString()}`)
  }
  
  const clearFilters = () => {
    setSearchQuery('')
    setMinClarity('')
    setMaxClarity('')
    setMinStructure('')
    setMaxStructure('')
    setStartDate('')
    setEndDate('')
    router.push('/dashboard/analyses')
  }
  
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
                {analysesData ? `Page ${currentPage} of ${Math.ceil(analysesData.total / analysesData.page_size)}` : ''}
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

        {/* Search and Filter Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-6"
        >
          <div className="card">
            {/* Search Bar */}
            <div className="flex flex-col sm:flex-row gap-4 mb-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-5 w-5" />
                <input
                  type="text"
                  placeholder="Search in feedback and summary..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && applyFilters()}
                  className="w-full pl-10 pr-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={`flex items-center px-4 py-2 border rounded-lg transition-colors ${
                    showFilters || hasActiveFilters
                      ? 'bg-primary-50 border-primary-200 text-primary-700 dark:bg-primary-900/30 dark:border-primary-700 dark:text-primary-300'
                      : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50 dark:bg-slate-800 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-700'
                  }`}
                >
                  <Filter className="h-4 w-4 mr-2" />
                  Filters
                  {hasActiveFilters && (
                    <span className="ml-2 bg-primary-600 text-white text-xs rounded-full px-2 py-1">
                      Active
                    </span>
                  )}
                </button>
                <button
                  onClick={applyFilters}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                  Search
                </button>
                {hasActiveFilters && (
                  <button
                    onClick={clearFilters}
                    className="flex items-center px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600 transition-colors"
                  >
                    <X className="h-4 w-4 mr-2" />
                    Clear
                  </button>
                )}
              </div>
            </div>

            {/* Advanced Filters */}
            {showFilters && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="border-t border-slate-200 dark:border-slate-700 pt-4"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {/* Score Filters */}
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                      Clarity Score Range
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="number"
                        placeholder="Min"
                        min="0"
                        max="10"
                        step="0.1"
                        value={minClarity}
                        onChange={(e) => setMinClarity(e.target.value)}
                        className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
                      />
                      <input
                        type="number"
                        placeholder="Max"
                        min="0"
                        max="10"
                        step="0.1"
                        value={maxClarity}
                        onChange={(e) => setMaxClarity(e.target.value)}
                        className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                      Structure Score Range
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="number"
                        placeholder="Min"
                        min="0"
                        max="10"
                        step="0.1"
                        value={minStructure}
                        onChange={(e) => setMinStructure(e.target.value)}
                        className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
                      />
                      <input
                        type="number"
                        placeholder="Max"
                        min="0"
                        max="10"
                        step="0.1"
                        value={maxStructure}
                        onChange={(e) => setMaxStructure(e.target.value)}
                        className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
                      />
                    </div>
                  </div>

                  {/* Date Filters */}
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                      Date Range
                    </label>
                    <div className="space-y-2">
                      <input
                        type="date"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                        className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
                      />
                      <input
                        type="date"
                        value={endDate}
                        onChange={(e) => setEndDate(e.target.value)}
                        className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
                      />
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
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
                          {analysis.analysis_id}
                        </h3>
                        <div className="flex items-center space-x-4 mt-1">
                          <div className="flex items-center text-sm text-slate-500 dark:text-slate-400">
                            <Calendar className="h-4 w-4 mr-1" />
                            {formatRelativeTime(analysis.created_at)}
                          </div>
                          <div className="text-sm text-slate-500 dark:text-slate-400">
                            {analysis.metrics?.word_count || 0} words
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
                          {analysis.metrics?.clarity_score || 0}
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">Clarity</div>
                      </div>
                      
                      <div className="text-center">
                        <div className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                          {analysis.metrics?.structure_score || 0}
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">Structure</div>
                      </div>
                      
                      <div className="text-center">
                        <div className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                          {analysis.metrics?.filler_word_count || 0}
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">Fillers</div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
            
            {/* Pagination */}
            {Math.ceil(analysesData.total / analysesData.page_size) > 1 && (
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
                  {Array.from({ length: Math.ceil(analysesData.total / analysesData.page_size) }, (_, i) => i + 1)
                    .filter(page => {
                      const totalPages = Math.ceil(analysesData.total / analysesData.page_size)
                      // Show first page, last page, current page, and pages around current
                      return page === 1 || 
                             page === totalPages || 
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
                  disabled={!analysesData.has_next}
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

export default function AnalysesPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-screen">
      <Loader2 className="h-8 w-8 animate-spin" />
    </div>}>
      <AnalysesPageContent />
    </Suspense>
  )
}