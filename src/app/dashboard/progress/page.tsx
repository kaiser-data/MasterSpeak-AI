'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Activity,
  Target,
  BarChart3,
  Clock,
  Loader2,
  Calendar,
  Award,
  Zap
} from 'lucide-react'
import Link from 'next/link'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Area,
  AreaChart,
  PieChart,
  Pie,
  Cell
} from 'recharts'

import { authAPI, speechesAPI } from '@/lib/api'
import { 
  selectProgressData, 
  selectChartData, 
  selectWeeklyProgress,
  generateMockProgressData,
  type Analysis,
  type ProgressMetrics,
  type ChartDataPoint,
  type WeeklyProgress
} from '@/selectors/progress'

interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
}

// Environment flag for mock data
const PROGRESS_UI = process.env.NODE_ENV === 'development' || process.env.PROGRESS_UI === '1'

export default function ProgressPage() {
  const [user, setUser] = useState<User | null>(null)
  const [analyses, setAnalyses] = useState<Analysis[]>([])
  const [metrics, setMetrics] = useState<ProgressMetrics | null>(null)
  const [chartData, setChartData] = useState<ChartDataPoint[]>([])
  const [weeklyData, setWeeklyData] = useState<WeeklyProgress[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [mockMode, setMockMode] = useState(PROGRESS_UI)

  useEffect(() => {
    const fetchProgressData = async () => {
      try {
        setLoading(true)
        setError(null)

        if (mockMode) {
          // Use mock data for development
          console.log('🎭 Using mock progress data (PROGRESS_UI=1)')
          const mockData = generateMockProgressData()
          
          setAnalyses(mockData.analyses)
          setMetrics(mockData.metrics)
          setChartData(mockData.chartData)
          setWeeklyData(mockData.weeklyData)
          
          // Mock user
          setUser({
            id: 'mock-user',
            email: 'demo@example.com',
            full_name: 'Demo User',
            is_active: true
          })
          
          return
        }

        // Real data fetching
        const currentUser = await authAPI.getCurrentUser()
        setUser(currentUser)
        
        // Get all user analyses for progress tracking
        const userAnalyses = await speechesAPI.getRecentAnalyses(currentUser.id, 100)
        
        // Get speech details for each analysis
        const analysesWithDetails = await Promise.all(
          userAnalyses.map(async (analysis: any) => {
            try {
              const speech = await speechesAPI.getSpeech(analysis.speech_id)
              return {
                ...analysis,
                title: speech.title,
                source_type: speech.source_type
              }
            } catch {
              return {
                ...analysis,
                title: 'Untitled Speech',
                source_type: 'text'
              }
            }
          })
        )
        
        setAnalyses(analysesWithDetails)
        
        // Calculate progress metrics
        const progressMetrics = selectProgressData(analysesWithDetails)
        const progressChartData = selectChartData(analysesWithDetails)
        const progressWeeklyData = selectWeeklyProgress(analysesWithDetails)
        
        setMetrics(progressMetrics)
        setChartData(progressChartData)
        setWeeklyData(progressWeeklyData)
        
      } catch (error) {
        console.error('Failed to fetch progress data:', error)
        setError(error instanceof Error ? error.message : 'Failed to load progress data')
        
        if (error instanceof Error && error.message.includes('401')) {
          window.location.href = '/auth/signin'
        }
      } finally {
        setLoading(false)
      }
    }
    
    fetchProgressData()
  }, [mockMode])

  const toggleMockMode = () => {
    setMockMode(!mockMode)
    setLoading(true)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="animate-spin h-12 w-12 text-primary-600 mx-auto mb-4" />
          <p className="text-slate-600 dark:text-slate-400">Loading progress...</p>
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

  if (!metrics) return null

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444']

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
            <div className="flex items-center space-x-4">
              {PROGRESS_UI && (
                <button
                  onClick={toggleMockMode}
                  className="text-xs px-2 py-1 bg-amber-100 text-amber-700 rounded dark:bg-amber-900/30 dark:text-amber-400"
                >
                  {mockMode ? 'Mock Data' : 'Real Data'}
                </button>
              )}
              <span className="text-sm text-slate-600 dark:text-slate-400">
                {user?.full_name}
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
            Progress Overview
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Track your speech analysis improvements and development over time
          </p>
        </motion.div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[
            {
              title: 'Total Analyses',
              value: metrics.totalAnalyses,
              icon: Activity,
              color: 'text-blue-600',
              bgColor: 'bg-blue-100 dark:bg-blue-900/30',
              suffix: '',
            },
            {
              title: 'Average Score',
              value: ((metrics.averageClarity + metrics.averageStructure) / 2).toFixed(1),
              icon: Target,
              color: 'text-green-600',
              bgColor: 'bg-green-100 dark:bg-green-900/30',
              suffix: '/10',
            },
            {
              title: 'Improvement',
              value: Math.abs(metrics.improvementTrend).toFixed(1),
              icon: metrics.improvementTrend >= 0 ? TrendingUp : TrendingDown,
              color: metrics.improvementTrend >= 0 ? 'text-green-600' : 'text-red-600',
              bgColor: metrics.improvementTrend >= 0 ? 'bg-green-100 dark:bg-green-900/30' : 'bg-red-100 dark:bg-red-900/30',
              suffix: '%',
            },
            {
              title: 'Recent Activity',
              value: metrics.recentActivity,
              icon: Clock,
              color: 'text-purple-600',
              bgColor: 'bg-purple-100 dark:bg-purple-900/30',
              suffix: ' this week',
            },
          ].map((stat, index) => (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="card-hover"
            >
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${stat.bgColor} mr-4`}>
                  <stat.icon className={`h-6 w-6 ${stat.color}`} />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
                    {stat.title}
                  </p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                    {stat.value}{stat.suffix}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Charts Section */}
        {chartData.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Progress Trend Chart */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="card"
            >
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
                Score Trends Over Time
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  />
                  <YAxis domain={[0, 10]} />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                    formatter={(value: number, name: string) => [value.toFixed(1), name === 'clarity' ? 'Clarity' : name === 'structure' ? 'Structure' : 'Average']}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="clarity" 
                    stroke="#3B82F6" 
                    strokeWidth={2}
                    dot={{ r: 4 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="structure" 
                    stroke="#10B981" 
                    strokeWidth={2}
                    dot={{ r: 4 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="average" 
                    stroke="#8B5CF6" 
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </motion.div>

            {/* Weekly Activity Chart */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="card"
            >
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
                Weekly Activity
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="week" tick={{ fontSize: 12 }} />
                  <YAxis />
                  <Tooltip 
                    formatter={(value: number, name: string) => [
                      value, 
                      name === 'analyses' ? 'Analyses' : 'Avg Score'
                    ]}
                  />
                  <Bar dataKey="analyses" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </motion.div>
          </div>
        ) : null}

        {/* Detailed Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
              Detailed Performance Metrics
            </h3>
            <Award className="h-5 w-5 text-amber-500" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Clarity Score */}
            <div className="text-center p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {metrics.averageClarity}
              </div>
              <div className="text-sm text-slate-600 dark:text-slate-400 mb-1">Average Clarity</div>
              <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full" 
                  style={{ width: `${(metrics.averageClarity / 10) * 100}%` }}
                ></div>
              </div>
            </div>

            {/* Structure Score */}
            <div className="text-center p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {metrics.averageStructure}
              </div>
              <div className="text-sm text-slate-600 dark:text-slate-400 mb-1">Average Structure</div>
              <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                <div 
                  className="bg-green-600 h-2 rounded-full" 
                  style={{ width: `${(metrics.averageStructure / 10) * 100}%` }}
                ></div>
              </div>
            </div>

            {/* Filler Words */}
            <div className="text-center p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <div className="text-3xl font-bold text-amber-600 mb-2">
                {metrics.averageFiller}
              </div>
              <div className="text-sm text-slate-600 dark:text-slate-400 mb-1">Avg Filler Score</div>
              <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                <div 
                  className="bg-amber-600 h-2 rounded-full" 
                  style={{ width: `${(metrics.averageFiller / 10) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Empty State */}
        {metrics.totalAnalyses === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-12"
          >
            <BarChart3 className="h-16 w-16 text-slate-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-slate-900 dark:text-slate-100 mb-2">
              No progress data yet
            </h3>
            <p className="text-slate-600 dark:text-slate-400 mb-6">
              Complete some speech analyses to see your progress tracking
            </p>
            <Link href="/dashboard" className="btn-primary">
              <Zap className="h-4 w-4 mr-2" />
              Start Analyzing
            </Link>
          </motion.div>
        )}
      </main>
    </div>
  )
}