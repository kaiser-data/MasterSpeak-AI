'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  Mic, 
  BarChart3, 
  TrendingUp, 
  Clock, 
  Users,
  Settings,
  LogOut,
  Plus,
  FileText,
  Zap,
  Target
} from 'lucide-react'

import SpeechAnalysisUpload from '@/components/ui/SpeechAnalysisUpload'
import AnalysisResults from '@/components/ui/AnalysisResults'
import { authAPI, speechesAPI, userAPI } from '@/lib/api'
import { 
  getRecentAnalyses, 
  Analysis, 
  formatRelativeTime,
  calculateOverallScore,
  getScoreColorClass
} from '@/services/analyses'

interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
}

interface Stats {
  totalSpeeches: number
  totalMinutes: number
  averageScore: number
  improvementRate: number
}

interface RecentAnalysis {
  id: string
  title: string
  date: string
  clarity_score?: number
  structure_score?: number
  duration?: string
  overall_score?: number
}

export default function DashboardPage() {
  const router = useRouter()
  const [showUpload, setShowUpload] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<any>(null)
  const [user, setUser] = useState<User | null>(null)
  const [stats, setStats] = useState<Stats>({ totalSpeeches: 0, totalMinutes: 0, averageScore: 0, improvementRate: 0 })
  const [recentAnalyses, setRecentAnalyses] = useState<RecentAnalysis[]>([])
  const [loading, setLoading] = useState(true)
  const [analysesData, setAnalysesData] = useState<Analysis[]>([])

  // Fetch user data and dashboard stats
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true)
        
        // Get current user (using existing auth)
        const currentUser = await authAPI.getCurrentUser()
        setUser(currentUser)
        
        // Get recent analyses using new service
        const [speeches, analyses] = await Promise.all([
          speechesAPI.getSpeeches(0, 100, currentUser.id),
          getRecentAnalyses(5).catch(() => [])
        ])
        
        setAnalysesData(analyses)
        
        // Calculate stats from speeches and analyses
        const totalSpeeches = speeches.length
        const totalMinutes = speeches.reduce((acc: number, speech: any) => {
          // Estimate reading time: ~180 words per minute
          const wordCount = speech.content ? speech.content.split(' ').length : 0
          return acc + Math.ceil(wordCount / 180)
        }, 0)
        
        // Calculate average score from new analysis metrics
        const averageScore = analyses.length > 0 
          ? analyses.reduce((acc, analysis) => acc + calculateOverallScore(analysis.metrics), 0) / analyses.length
          : 0
        
        // Calculate improvement trend (compare first and last analyses)
        const improvementRate = analyses.length > 1 
          ? ((calculateOverallScore(analyses[0].metrics) - calculateOverallScore(analyses[analyses.length - 1].metrics)) / calculateOverallScore(analyses[analyses.length - 1].metrics)) * 100
          : 0
        
        setStats({
          totalSpeeches,
          totalMinutes,
          averageScore: Number(averageScore.toFixed(1)),
          improvementRate: Number(improvementRate.toFixed(1))
        })
        
        // Format recent analyses for display
        const recentWithAnalyses = analyses.slice(0, 3).map((analysis: Analysis) => {
          const speech = speeches.find((s: any) => s.id === analysis.speech_id)
          return {
            id: analysis.analysis_id,
            title: speech?.title || 'Untitled Speech',
            date: formatRelativeTime(analysis.created_at),
            clarity_score: analysis.metrics?.clarity_score,
            structure_score: analysis.metrics?.structure_score,
            overall_score: calculateOverallScore(analysis.metrics),
            duration: speech?.content ? `${Math.ceil(speech.content.split(' ').length / 180)}:00` : '0:00'
          }
        })
        
        setRecentAnalyses(recentWithAnalyses)
        
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
        // Handle unauthenticated users
        if (error instanceof Error && error.message.includes('401')) {
          window.location.href = '/auth/signin'
        }
      } finally {
        setLoading(false)
      }
    }
    
    fetchDashboardData()
  }, [])

  const handleAnalysisComplete = (result: any) => {
    setAnalysisResult(result)
    setShowUpload(false)
    setShowResults(true)
    // Refresh dashboard data after new analysis
    if (user) {
      // Optionally refresh the dashboard stats here
    }
  }

  const handleBackToDashboard = () => {
    setShowResults(false)
    setAnalysisResult(null)
  }

  const handleNewAnalysis = () => {
    setShowResults(false)
    setShowUpload(true)
    setAnalysisResult(null)
  }


  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-slate-600 dark:text-slate-400">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-slate-600 dark:text-slate-400 mb-4">Please sign in to access your dashboard</p>
          <button 
            onClick={() => window.location.href = '/auth/signin'}
            className="btn-primary"
          >
            Sign In
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 shadow-sm border-b border-slate-200 dark:border-slate-700">
        <div className="container-responsive">
          <div className="flex items-center justify-between py-4">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 bg-gradient-to-r from-primary-600 to-accent-600 rounded-lg flex items-center justify-center">
                <Mic className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gradient">MasterSpeak AI</span>
            </div>

            {/* Navigation */}
            <nav className="hidden md:flex items-center space-x-8">
              <a href="/dashboard" className="nav-link-active">Dashboard</a>
              <a href="/dashboard/analyses" className="nav-link">Analyses</a>
              <a href="/dashboard/progress" className="nav-link">Progress</a>
              <a href="#" className="nav-link">Settings</a>
            </nav>

            {/* User menu */}
            <div className="flex items-center space-x-4">
              <button className="btn-primary" onClick={() => setShowUpload(true)}>
                <Plus className="h-4 w-4 mr-2" />
                New Analysis
              </button>
              
              <div className="flex items-center space-x-2">
                <div className="h-8 w-8 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-primary-600">
                    {user.full_name.split(' ').map(n => n[0]).join('')}
                  </span>
                </div>
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                  {user.full_name}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="container-responsive py-8">
        
        {showResults ? (
          <AnalysisResults 
            result={analysisResult}
            onBack={handleBackToDashboard}
            onNewAnalysis={handleNewAnalysis}
          />
        ) : showUpload ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <div className="mb-4">
              <button
                onClick={() => setShowUpload(false)}
                className="text-primary-600 hover:text-primary-700 font-medium"
              >
                ← Back to Dashboard
              </button>
            </div>
            <SpeechAnalysisUpload
              onAnalysisComplete={handleAnalysisComplete}
            />
          </motion.div>
        ) : (
          <>
            {/* Welcome section */}
            <div className="mb-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-2">
                  Welcome back, {user.full_name.split(' ')[0]}!
                </h1>
                <p className="text-slate-600 dark:text-slate-400">
                  Here's your speech analysis overview and recent activity.
                </p>
              </motion.div>
            </div>

            {/* Stats cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {[
                {
                  title: 'Total Speeches',
                  value: stats.totalSpeeches,
                  icon: FileText,
                  color: 'text-blue-600',
                  bgColor: 'bg-blue-100 dark:bg-blue-900/30',
                  suffix: '',
                },
                {
                  title: 'Total Minutes',
                  value: stats.totalMinutes,
                  icon: Clock,
                  color: 'text-green-600',
                  bgColor: 'bg-green-100 dark:bg-green-900/30',
                  suffix: ' min',
                },
                {
                  title: 'Average Score',
                  value: stats.averageScore,
                  icon: Target,
                  color: 'text-purple-600',
                  bgColor: 'bg-purple-100 dark:bg-purple-900/30',
                  suffix: '/10',
                },
                {
                  title: 'Improvement',
                  value: Math.round(stats.improvementRate),
                  icon: TrendingUp,
                  color: 'text-orange-600',
                  bgColor: 'bg-orange-100 dark:bg-orange-900/30',
                  suffix: '%',
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

            {/* Recent analyses */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="card"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
                  Recent Analyses
                </h2>
                <button 
                  onClick={() => router.push('/dashboard/analyses')}
                  className="btn-outline"
                >
                  View All
                </button>
              </div>

              <div className="space-y-4">
                {recentAnalyses.map((analysis, index) => (
                  <motion.div
                    key={analysis.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 + index * 0.1 }}
                    className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors cursor-pointer"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="h-10 w-10 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
                        <Mic className="h-5 w-5 text-primary-600" />
                      </div>
                      <div>
                        <h3 className="font-medium text-slate-900 dark:text-slate-100">
                          {analysis.title}
                        </h3>
                        <p className="text-sm text-slate-500 dark:text-slate-400">
                          {analysis.date} • {analysis.duration}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-6">
                      <div className="text-center">
                        <p className="text-sm text-slate-500 dark:text-slate-400">Overall</p>
                        <div className="flex items-center space-x-1">
                          <span className={`text-lg font-semibold ${getScoreColorClass(analysis.overall_score || 0)}`}>
                            {(analysis.overall_score || 0).toFixed(1)}
                          </span>
                          <span className="text-sm text-slate-400">/10</span>
                        </div>
                      </div>
                      
                      <div className="text-center">
                        <p className="text-sm text-slate-500 dark:text-slate-400">Clarity</p>
                        <div className="flex items-center space-x-1">
                          <span className={`text-md font-medium ${getScoreColorClass(analysis.clarity_score || 0)}`}>
                            {analysis.clarity_score || 'N/A'}
                          </span>
                          {analysis.clarity_score && <span className="text-sm text-slate-400">/10</span>}
                        </div>
                      </div>
                      
                      <div className="text-center">
                        <p className="text-sm text-slate-500 dark:text-slate-400">Structure</p>
                        <div className="flex items-center space-x-1">
                          <span className={`text-md font-medium ${getScoreColorClass(analysis.structure_score || 0)}`}>
                            {analysis.structure_score || 'N/A'}
                          </span>
                          {analysis.structure_score && <span className="text-sm text-slate-400">/10</span>}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              {recentAnalyses.length === 0 && (
                <div className="text-center py-12">
                  <Mic className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-2">
                    No analyses yet
                  </h3>
                  <p className="text-slate-600 dark:text-slate-400 mb-6">
                    Get started by analyzing your first speech
                  </p>
                  <button 
                    onClick={() => setShowUpload(true)}
                    className="btn-primary"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Start Your First Analysis
                  </button>
                </div>
              )}
            </motion.div>

            {/* Quick actions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="mt-8"
            >
              <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 mb-4">
                Quick Actions
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  {
                    title: 'Record New Speech',
                    description: 'Use your microphone to record and analyze',
                    icon: Mic,
                    action: () => setShowUpload(true),
                  },
                  {
                    title: 'Upload Audio File',
                    description: 'Analyze pre-recorded audio files',
                    icon: FileText,
                    action: () => setShowUpload(true),
                  },
                  {
                    title: 'Analyze Text',
                    description: 'Paste text to get written feedback',
                    icon: Zap,
                    action: () => setShowUpload(true),
                  },
                ].map((action, index) => (
                  <button
                    key={action.title}
                    onClick={action.action}
                    className="card-hover text-left p-6 hover:shadow-lg transition-shadow"
                  >
                    <div className="flex items-center mb-3">
                      <div className="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg mr-3">
                        <action.icon className="h-5 w-5 text-primary-600" />
                      </div>
                      <h3 className="font-medium text-slate-900 dark:text-slate-100">
                        {action.title}
                      </h3>
                    </div>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      {action.description}
                    </p>
                  </button>
                ))}
              </div>
            </motion.div>
          </>
        )}
      </main>
    </div>
  )
}