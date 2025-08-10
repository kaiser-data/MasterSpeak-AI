'use client'

import { motion } from 'framer-motion'
import { 
  CheckCircle, 
  TrendingUp, 
  MessageSquare, 
  BarChart3,
  ArrowLeft,
  Download,
  Share2
} from 'lucide-react'

interface AnalysisResultsProps {
  result: {
    success: boolean
    speech_id: string
    analysis: {
      clarity_score: number
      structure_score: number  
      filler_word_count: number
      feedback: string
    }
  }
  onBack: () => void
  onNewAnalysis?: () => void
}

export default function AnalysisResults({ result, onBack, onNewAnalysis }: AnalysisResultsProps) {
  console.log('📊 AnalysisResults received:', result)
  console.log('📊 Result structure check:', {
    hasResult: !!result,
    success: result?.success,
    hasAnalysis: !!result?.analysis,
    analysisKeys: result?.analysis ? Object.keys(result.analysis) : 'none'
  })
  
  if (!result) {
    console.log('❌ No result provided to AnalysisResults')
    return (
      <div className="card max-w-4xl mx-auto text-center py-8">
        <p className="text-error-600">No analysis results available (no result object)</p>
        <button onClick={onBack} className="btn-outline mt-4">
          Back to Dashboard
        </button>
      </div>
    )
  }

  if (!result.success) {
    console.log('❌ Result success is false:', result)
    return (
      <div className="card max-w-4xl mx-auto text-center py-8">
        <p className="text-error-600">Analysis failed - success is false</p>
        <pre className="text-xs text-left bg-gray-100 p-2 mt-2">{JSON.stringify(result, null, 2)}</pre>
        <button onClick={onBack} className="btn-outline mt-4">
          Back to Dashboard
        </button>
      </div>
    )
  }

  if (!result.analysis) {
    console.log('❌ No analysis data in result:', result)
    return (
      <div className="card max-w-4xl mx-auto text-center py-8">
        <p className="text-error-600">No analysis data found in response</p>
        <pre className="text-xs text-left bg-gray-100 p-2 mt-2">{JSON.stringify(result, null, 2)}</pre>
        <button onClick={onBack} className="btn-outline mt-4">
          Back to Dashboard
        </button>
      </div>
    )
  }

  const { analysis } = result
  const avgScore = Math.round((analysis.clarity_score + analysis.structure_score) / 2)

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600'
    if (score >= 6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreDescription = (score: number) => {
    if (score >= 8) return 'Excellent'
    if (score >= 6) return 'Good'
    return 'Needs Improvement'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6 max-w-4xl mx-auto"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center text-primary-600 hover:text-primary-700 font-medium"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </button>
        
        <div className="flex items-center space-x-2">
          <button className="btn-outline">
            <Share2 className="h-4 w-4 mr-2" />
            Share
          </button>
          <button className="btn-outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Success banner */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="card bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-green-200 dark:border-green-800"
      >
        <div className="flex items-center">
          <CheckCircle className="h-8 w-8 text-green-600 mr-4" />
          <div>
            <h2 className="text-xl font-bold text-green-800 dark:text-green-200">
              Analysis Complete!
            </h2>
            <p className="text-green-600 dark:text-green-300">
              Your speech has been analyzed. Here are your results:
            </p>
          </div>
        </div>
      </motion.div>

      {/* Score cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Overall Score */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card text-center"
        >
          <div className="mb-4">
            <div className="h-16 w-16 mx-auto bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center">
              <BarChart3 className="h-8 w-8 text-primary-600" />
            </div>
          </div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2">
            Overall Score
          </h3>
          <div className="text-3xl font-bold text-primary-600 mb-1">
            {avgScore}/10
          </div>
          <p className={`text-sm font-medium ${getScoreColor(avgScore)}`}>
            {getScoreDescription(avgScore)}
          </p>
        </motion.div>

        {/* Clarity Score */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card text-center"
        >
          <div className="mb-4">
            <div className="h-16 w-16 mx-auto bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
              <MessageSquare className="h-8 w-8 text-blue-600" />
            </div>
          </div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2">
            Clarity
          </h3>
          <div className="text-3xl font-bold text-blue-600 mb-1">
            {analysis.clarity_score}/10
          </div>
          <p className={`text-sm font-medium ${getScoreColor(analysis.clarity_score)}`}>
            {getScoreDescription(analysis.clarity_score)}
          </p>
        </motion.div>

        {/* Structure Score */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card text-center"
        >
          <div className="mb-4">
            <div className="h-16 w-16 mx-auto bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center">
              <TrendingUp className="h-8 w-8 text-purple-600" />
            </div>
          </div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2">
            Structure
          </h3>
          <div className="text-3xl font-bold text-purple-600 mb-1">
            {analysis.structure_score}/10
          </div>
          <p className={`text-sm font-medium ${getScoreColor(analysis.structure_score)}`}>
            {getScoreDescription(analysis.structure_score)}
          </p>
        </motion.div>
      </div>

      {/* Additional metrics */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card"
      >
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
          Additional Metrics
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
            <div className="text-sm text-slate-600 dark:text-slate-400">Filler Words</div>
            <div className="text-2xl font-bold text-slate-900 dark:text-slate-100">
              {analysis.filler_word_count}
            </div>
            <div className="text-sm text-slate-500">
              {analysis.filler_word_count <= 3 ? 'Excellent' : 
               analysis.filler_word_count <= 6 ? 'Good' : 'Needs Work'}
            </div>
          </div>
          <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
            <div className="text-sm text-slate-600 dark:text-slate-400">Speech ID</div>
            <div className="text-sm font-mono text-slate-900 dark:text-slate-100">
              {result.speech_id.slice(0, 8)}...
            </div>
            <div className="text-sm text-slate-500">Reference ID</div>
          </div>
        </div>
      </motion.div>

      {/* Feedback */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="card"
      >
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
          AI Feedback
        </h3>
        <div className="prose prose-slate dark:prose-invert max-w-none">
          <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
            {analysis.feedback || 'No specific feedback available for this analysis.'}
          </p>
        </div>
      </motion.div>

      {/* Next steps */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="card bg-gradient-to-r from-primary-50 to-accent-50 dark:from-primary-900/20 dark:to-accent-900/20"
      >
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
          What's Next?
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button 
            onClick={onNewAnalysis || onBack}
            className="btn-primary"
          >
            Analyze Another Speech
          </button>
          <button className="btn-outline">
            View Progress History
          </button>
        </div>
      </motion.div>
    </motion.div>
  )
}