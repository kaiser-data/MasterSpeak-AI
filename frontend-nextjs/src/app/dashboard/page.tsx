'use client'

import { useState } from 'react'
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

// Mock data - in real app this would come from API
const mockUser = {
  id: 'a95bf157-d3f3-440f-bf91-6a31f85c833a', // Use the actual test user UUID
  name: 'John Doe', 
  email: 'john@example.com',
  avatar: null,
}

const mockStats = {
  totalSpeeches: 24,
  totalMinutes: 180,
  averageScore: 8.5,
  improvementRate: 15,
}

const mockRecentAnalyses = [
  {
    id: '1',
    title: 'Product Presentation',
    date: '2025-05-10',
    clarity_score: 9,
    structure_score: 8,
    duration: '5:30',
  },
  {
    id: '2', 
    title: 'Team Meeting',
    date: '2025-05-09',
    clarity_score: 7,
    structure_score: 9,
    duration: '3:20',
  },
  {
    id: '3',
    title: 'Sales Pitch',
    date: '2025-05-08',
    clarity_score: 8,
    structure_score: 7,
    duration: '4:15',
  },
]

export default function DashboardPage() {
  const [showUpload, setShowUpload] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<any>(null)
  const [user] = useState(mockUser)

  const handleAnalysisComplete = (result: any) => {
    console.log('🎯 Dashboard received analysis result:', result)
    console.log('🎯 Setting state - showResults will be:', true)
    setAnalysisResult(result)
    setShowUpload(false)
    setShowResults(true)
    console.log('🎯 State updated')
    // In real app, refresh dashboard data
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

  // Test function to simulate results
  const testShowResults = () => {
    const testResult = {
      success: true,
      speech_id: "test-id",
      analysis: {
        clarity_score: 8,
        structure_score: 7,
        filler_word_count: 3,
        feedback: "This is a test feedback message."
      }
    }
    console.log('🧪 Testing with mock data:', testResult)
    setAnalysisResult(testResult)
    setShowUpload(false)
    setShowResults(true)
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
              <a href="#" className="nav-link-active">Dashboard</a>
              <a href="#" className="nav-link">Analyses</a>
              <a href="#" className="nav-link">Progress</a>
              <a href="#" className="nav-link">Settings</a>
            </nav>

            {/* User menu */}
            <div className="flex items-center space-x-4">
              <button className="btn-primary" onClick={() => setShowUpload(true)}>
                <Plus className="h-4 w-4 mr-2" />
                New Analysis
              </button>
              
              {process.env.NODE_ENV === 'development' && (
                <button className="btn-outline" onClick={testShowResults}>
                  Test Results
                </button>
              )}
              
              <button 
                className="btn-outline bg-red-100 border-red-300 text-red-700" 
                onClick={async () => {
                  try {
                    console.log('🧪 FORCE TEST: Calling test endpoint...')
                    const response = await fetch('/api/v1/test-analysis-response')
                    const testData = await response.json()
                    console.log('🧪 FORCE TEST: Response:', testData)
                    setAnalysisResult(testData)
                    setShowUpload(false) 
                    setShowResults(true)
                    console.log('🧪 FORCE TEST: State set, should show results now')
                  } catch (error) {
                    console.error('🧪 FORCE TEST: Failed:', error)
                    alert('Force test failed: ' + error)
                  }
                }}
              >
                🧪 FORCE TEST  
              </button>
              
              <button 
                className="btn-outline bg-yellow-100 border-yellow-300 text-yellow-700" 
                onClick={() => {
                  console.log('⚡ EMERGENCY: Forcing results display without API call...')
                  const emergencyData = {
                    success: true,
                    speech_id: "emergency-test-id",
                    analysis: {
                      clarity_score: 9,
                      structure_score: 8,
                      filler_word_count: 2,
                      feedback: "⚡ EMERGENCY TEST: If you can see this, the AnalysisResults component works. The issue is in the API call or state management flow."
                    }
                  }
                  console.log('⚡ EMERGENCY: Setting result:', emergencyData)
                  setAnalysisResult(emergencyData)
                  setShowUpload(false)
                  setShowResults(true)
                  console.log('⚡ EMERGENCY: Done - results should be visible now')
                }}
              >
                ⚡ EMERGENCY
              </button>
              
              <div className="flex items-center space-x-2">
                <div className="h-8 w-8 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-primary-600">
                    {user.name.split(' ').map(n => n[0]).join('')}
                  </span>
                </div>
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                  {user.name}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="container-responsive py-8">
        {/* Debug info - ALWAYS VISIBLE for debugging */}
        <div className="mb-4 p-2 bg-blue-50 border border-blue-200 text-xs font-mono">
          <strong>DEBUG STATUS:</strong> showResults={String(showResults)}, showUpload={String(showUpload)}, hasResult={String(!!analysisResult)}
          {analysisResult && (
            <div className="mt-1 text-green-700">
              Result Keys: {Object.keys(analysisResult).join(', ')}
              {analysisResult.analysis && ` | Analysis Keys: ${Object.keys(analysisResult.analysis).join(', ')}`}
            </div>
          )}
        </div>
        
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
                  Welcome back, {user.name.split(' ')[0]}!
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
                  value: mockStats.totalSpeeches,
                  icon: FileText,
                  color: 'text-blue-600',
                  bgColor: 'bg-blue-100 dark:bg-blue-900/30',
                  suffix: '',
                },
                {
                  title: 'Total Minutes',
                  value: mockStats.totalMinutes,
                  icon: Clock,
                  color: 'text-green-600',
                  bgColor: 'bg-green-100 dark:bg-green-900/30',
                  suffix: ' min',
                },
                {
                  title: 'Average Score',
                  value: mockStats.averageScore,
                  icon: Target,
                  color: 'text-purple-600',
                  bgColor: 'bg-purple-100 dark:bg-purple-900/30',
                  suffix: '/10',
                },
                {
                  title: 'Improvement',
                  value: mockStats.improvementRate,
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
                <button className="btn-outline">
                  View All
                </button>
              </div>

              <div className="space-y-4">
                {mockRecentAnalyses.map((analysis, index) => (
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
                        <p className="text-sm text-slate-500 dark:text-slate-400">Clarity</p>
                        <div className="flex items-center space-x-1">
                          <span className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                            {analysis.clarity_score}
                          </span>
                          <span className="text-sm text-slate-400">/10</span>
                        </div>
                      </div>
                      
                      <div className="text-center">
                        <p className="text-sm text-slate-500 dark:text-slate-400">Structure</p>
                        <div className="flex items-center space-x-1">
                          <span className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                            {analysis.structure_score}
                          </span>
                          <span className="text-sm text-slate-400">/10</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              {mockRecentAnalyses.length === 0 && (
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