'use client'

import { useState } from 'react'

export default function DebugPage() {
  const [testResult, setTestResult] = useState<any>(null)
  const [showResults, setShowResults] = useState(false)

  const mockResult = {
    success: true,
    speech_id: "debug-test-123",
    analysis: {
      clarity_score: 9,
      structure_score: 8,
      filler_word_count: 2,
      feedback: "🧪 DEBUG PAGE TEST: This is a completely isolated test of the analysis results display. If you can see this, the component works!"
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-100 border-2 border-red-300 p-4 mb-6 text-center">
          <h1 className="text-2xl font-bold text-red-800">🔧 DEBUG PAGE - v2.1</h1>
          <p className="text-red-700">If you can see this page, frontend deployment is working!</p>
        </div>

        <div className="bg-blue-50 border border-blue-200 p-4 mb-6">
          <h2 className="font-bold mb-2">State Debug:</h2>
          <p>showResults: {String(showResults)}</p>
          <p>hasTestResult: {String(!!testResult)}</p>
          {testResult && (
            <div className="mt-2 text-green-700">
              <p>Result Keys: {Object.keys(testResult).join(', ')}</p>
              {testResult.analysis && <p>Analysis Keys: {Object.keys(testResult.analysis).join(', ')}</p>}
            </div>
          )}
        </div>

        <div className="space-x-4 mb-6">
          <button
            onClick={() => {
              console.log('🔧 DEBUG: Setting test result...')
              setTestResult(mockResult)
              setShowResults(true)
              console.log('🔧 DEBUG: State updated')
            }}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700"
          >
            🧪 SET TEST RESULT
          </button>

          <button
            onClick={() => {
              setTestResult(null)
              setShowResults(false)
            }}
            className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700"
          >
            🗑️ CLEAR
          </button>

          <a 
            href="/dashboard"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 inline-block"
          >
            ← Back to Dashboard
          </a>
        </div>

        {showResults && testResult ? (
          <div className="bg-white border-2 border-green-300 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-green-800 mb-4">✅ SUCCESS! Results Display Working</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <h3 className="font-semibold mb-2">Clarity Score</h3>
                <div className="text-3xl font-bold text-blue-600">{testResult.analysis.clarity_score}/10</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <h3 className="font-semibold mb-2">Structure Score</h3>
                <div className="text-3xl font-bold text-purple-600">{testResult.analysis.structure_score}/10</div>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <h3 className="font-semibold mb-2">Filler Words</h3>
                <div className="text-3xl font-bold text-orange-600">{testResult.analysis.filler_word_count}</div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-semibold mb-2">Feedback:</h3>
              <p className="text-gray-700">{testResult.analysis.feedback}</p>
            </div>

            <div className="mt-4 text-sm text-gray-500">
              <p>Speech ID: {testResult.speech_id}</p>
            </div>
          </div>
        ) : (
          <div className="bg-gray-100 border border-gray-300 rounded-lg p-6 text-center">
            <p className="text-gray-600">Click "SET TEST RESULT" to test the display component</p>
          </div>
        )}

        <div className="mt-6 bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
          <h3 className="font-bold text-yellow-800 mb-2">Debug Instructions:</h3>
          <ol className="list-decimal list-inside text-yellow-700 space-y-1">
            <li>If you can see this page, the frontend deployed correctly</li>
            <li>Click "SET TEST RESULT" - you should see results display immediately</li>
            <li>If results don't show, there's a React rendering issue</li>
            <li>If results DO show, the issue is in the dashboard API flow</li>
          </ol>
        </div>
      </div>
    </div>
  )
}