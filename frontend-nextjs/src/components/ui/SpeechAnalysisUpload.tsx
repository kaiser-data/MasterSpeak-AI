'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Upload, 
  File as FileIcon, 
  FileText, 
  Music, 
  X, 
  Loader2, 
  Play, 
  Pause,
  Square,
  Mic
} from 'lucide-react'
import { toast } from 'react-hot-toast'

import { speechAnalysisSchema, type SpeechAnalysisFormData } from '@/lib/auth-schemas'
import { speechAPI } from '@/lib/api'

interface SpeechAnalysisUploadProps {
  userId: string
  onAnalysisComplete?: (result: any) => void
}

interface AudioRecorderState {
  isRecording: boolean
  isPaused: boolean
  duration: number
  mediaRecorder: MediaRecorder | null
  audioBlob: Blob | null
  audioUrl: string | null
}

const PROMPT_TYPES = [
  { value: 'default', label: 'General Analysis', description: 'Comprehensive speech evaluation' },
  { value: 'presentation', label: 'Presentation', description: 'Focus on clarity and structure' },
  { value: 'conversation', label: 'Conversation', description: 'Natural speaking patterns' },
  { value: 'detailed', label: 'Detailed', description: 'In-depth analysis with examples' },
  { value: 'brief', label: 'Brief', description: 'Quick summary and key points' },
]

export default function SpeechAnalysisUpload({ userId, onAnalysisComplete }: SpeechAnalysisUploadProps) {
  const [uploadMode, setUploadMode] = useState<'file' | 'text' | 'record'>('text')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [recordingState, setRecordingState] = useState<AudioRecorderState>({
    isRecording: false,
    isPaused: false,
    duration: 0,
    mediaRecorder: null,
    audioBlob: null,
    audioUrl: null,
  })

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<SpeechAnalysisFormData>({
    resolver: zodResolver(speechAnalysisSchema),
    defaultValues: {
      prompt_type: 'default',
    },
  })

  const selectedFile = watch('file')
  const textContent = watch('text')
  const promptType = watch('prompt_type')

  // File upload with dropzone
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      setValue('file', file)
      setValue('text', undefined)
      setUploadMode('file')
    }
  }, [setValue])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'application/pdf': ['.pdf'],
      'audio/mpeg': ['.mp3'],
      'audio/wav': ['.wav'],
      'audio/mp4': ['.m4a'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
  })

  // Audio recording functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      const audioChunks: BlobPart[] = []

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data)
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' })
        const audioUrl = URL.createObjectURL(audioBlob)
        
        setRecordingState(prev => ({
          ...prev,
          audioBlob,
          audioUrl,
          isRecording: false,
        }))

        // Convert to File object
        const file = new File([audioBlob], 'recording.wav', { type: 'audio/wav' })
        setValue('file', file)
        setValue('text', undefined)
        setUploadMode('record')
        
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setRecordingState(prev => ({
        ...prev,
        isRecording: true,
        mediaRecorder,
        audioBlob: null,
        audioUrl: null,
      }))

      // Start duration timer
      const startTime = Date.now()
      const timer = setInterval(() => {
        setRecordingState(prev => ({
          ...prev,
          duration: Date.now() - startTime,
        }))
      }, 100)

      mediaRecorder.onstop = () => {
        clearInterval(timer)
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' })
        const audioUrl = URL.createObjectURL(audioBlob)
        
        setRecordingState(prev => ({
          ...prev,
          audioBlob,
          audioUrl,
          isRecording: false,
          duration: 0,
        }))

        const file = new File([audioBlob], 'recording.wav', { type: 'audio/wav' })
        setValue('file', file)
        setValue('text', undefined)
        setUploadMode('record')
        
        stream.getTracks().forEach(track => track.stop())
      }
    } catch (error) {
      toast.error('Failed to access microphone')
      console.error('Recording error:', error)
    }
  }

  const stopRecording = () => {
    if (recordingState.mediaRecorder && recordingState.isRecording) {
      recordingState.mediaRecorder.stop()
    }
  }

  const removeFile = () => {
    setValue('file', undefined)
    if (recordingState.audioUrl) {
      URL.revokeObjectURL(recordingState.audioUrl)
    }
    setRecordingState({
      isRecording: false,
      isPaused: false,
      duration: 0,
      mediaRecorder: null,
      audioBlob: null,
      audioUrl: null,
    })
  }

  const onSubmit = async (data: SpeechAnalysisFormData) => {
    setIsAnalyzing(true)
    try {
      let result

      if (data.file) {
        // File upload
        result = await speechAPI.uploadAndAnalyze({
          file: data.file,
          prompt_type: data.prompt_type,
        })
      } else if (data.text) {
        // Text analysis
        result = await speechAPI.analyzeText({
          text: data.text,
          prompt_type: data.prompt_type,
        })
      }

      toast.success('Analysis completed successfully!')
      onAnalysisComplete?.(result)
      reset()
      removeFile()
    } catch (error: any) {
      console.error('Analysis error:', error)
      if (error.response?.data?.detail) {
        toast.error(error.response.data.detail)
      } else {
        toast.error('Failed to analyze speech. Please try again.')
      }
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('audio/')) return Music
    if (file.type === 'application/pdf') return FileText
    return FileIcon
  }

  const formatDuration = (ms: number) => {
    const seconds = Math.floor(ms / 1000)
    const minutes = Math.floor(seconds / 60)
    return `${minutes}:${(seconds % 60).toString().padStart(2, '0')}`
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card max-w-4xl mx-auto"
    >
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-2">
          Analyze Your Speech
        </h2>
        <p className="text-slate-600 dark:text-slate-400">
          Upload a file, paste text, or record audio to get AI-powered feedback on your communication
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Input mode tabs */}
        <div className="flex space-x-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg">
          {[
            { mode: 'text' as const, label: 'Text Input', icon: FileText },
            { mode: 'file' as const, label: 'File Upload', icon: Upload },
            { mode: 'record' as const, label: 'Record Audio', icon: Mic },
          ].map(({ mode, label, icon: Icon }) => (
            <button
              key={mode}
              type="button"
              onClick={() => setUploadMode(mode)}
              className={`flex-1 flex items-center justify-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                uploadMode === mode
                  ? 'bg-white dark:bg-slate-700 text-primary-600 shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
            >
              <Icon className="h-4 w-4 mr-2" />
              {label}
            </button>
          ))}
        </div>

        {/* Text input mode */}
        <AnimatePresence mode="wait">
          {uploadMode === 'text' && (
            <motion.div
              key="text"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Speech Text
              </label>
              <textarea
                {...register('text')}
                rows={8}
                className="input-primary resize-none"
                placeholder="Paste your speech text here or type what you want to analyze..."
              />
              {errors.text && (
                <p className="mt-1 text-sm text-error-600 dark:text-error-400">
                  {errors.text.message}
                </p>
              )}
              {textContent && (
                <div className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                  {textContent.length} characters • ~{Math.ceil(textContent.split(' ').length / 180)} min read
                </div>
              )}
            </motion.div>
          )}

          {/* File upload mode */}
          {uploadMode === 'file' && (
            <motion.div
              key="file"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              {!selectedFile ? (
                <div
                  {...getRootProps()}
                  className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                    isDragActive
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-slate-300 dark:border-slate-600 hover:border-primary-400'
                  }`}
                >
                  <input {...getInputProps()} />
                  <Upload className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-2">
                    {isDragActive ? 'Drop your file here' : 'Upload a file'}
                  </h3>
                  <p className="text-slate-600 dark:text-slate-400 mb-4">
                    Drag and drop a file, or click to browse
                  </p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Supported formats: TXT, PDF, MP3, WAV, M4A (max 10MB)
                  </p>
                </div>
              ) : (
                <div className="border border-slate-200 dark:border-slate-700 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {(() => {
                        const IconComponent = getFileIcon(selectedFile)
                        return <IconComponent className="h-8 w-8 text-primary-600" />
                      })()}
                      <div>
                        <p className="font-medium text-slate-900 dark:text-slate-100">
                          {selectedFile.name}
                        </p>
                        <p className="text-sm text-slate-500 dark:text-slate-400">
                          {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={removeFile}
                      className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded"
                    >
                      <X className="h-4 w-4 text-slate-500" />
                    </button>
                  </div>
                  
                  {recordingState.audioUrl && (
                    <div className="mt-3">
                      <audio controls src={recordingState.audioUrl} className="w-full" />
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          )}

          {/* Recording mode */}
          {uploadMode === 'record' && (
            <motion.div
              key="record"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              {!recordingState.audioBlob ? (
                <div className="text-center p-8 border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-lg">
                  <div className="flex flex-col items-center space-y-4">
                    <div className={`p-4 rounded-full ${
                      recordingState.isRecording 
                        ? 'bg-red-100 dark:bg-red-900/30' 
                        : 'bg-slate-100 dark:bg-slate-800'
                    }`}>
                      <Mic className={`h-8 w-8 ${
                        recordingState.isRecording ? 'text-red-600' : 'text-slate-600'
                      }`} />
                    </div>
                    
                    {recordingState.isRecording ? (
                      <>
                        <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">
                          Recording...
                        </h3>
                        <div className="text-2xl font-mono text-red-600 dark:text-red-400">
                          {formatDuration(recordingState.duration)}
                        </div>
                        <button
                          type="button"
                          onClick={stopRecording}
                          className="flex items-center px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                        >
                          <Square className="h-4 w-4 mr-2" />
                          Stop Recording
                        </button>
                      </>
                    ) : (
                      <>
                        <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">
                          Record Your Speech
                        </h3>
                        <p className="text-slate-600 dark:text-slate-400">
                          Click the button below to start recording
                        </p>
                        <button
                          type="button"
                          onClick={startRecording}
                          className="flex items-center px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                        >
                          <Mic className="h-4 w-4 mr-2" />
                          Start Recording
                        </button>
                      </>
                    )}
                  </div>
                </div>
              ) : (
                <div className="border border-slate-200 dark:border-slate-700 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <Music className="h-8 w-8 text-primary-600" />
                      <div>
                        <p className="font-medium text-slate-900 dark:text-slate-100">
                          Recording.wav
                        </p>
                        <p className="text-sm text-slate-500 dark:text-slate-400">
                          {formatDuration(recordingState.duration)}
                        </p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={removeFile}
                      className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded"
                    >
                      <X className="h-4 w-4 text-slate-500" />
                    </button>
                  </div>
                  
                  {recordingState.audioUrl && (
                    <audio controls src={recordingState.audioUrl} className="w-full" />
                  )}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Analysis type selection */}
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
            Analysis Type
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {PROMPT_TYPES.map((type) => (
              <label
                key={type.value}
                className={`relative flex cursor-pointer rounded-lg border p-4 focus:outline-none ${
                  promptType === type.value
                    ? 'border-primary-600 ring-2 ring-primary-600'
                    : 'border-slate-300 dark:border-slate-600'
                }`}
              >
                <input
                  {...register('prompt_type')}
                  type="radio"
                  value={type.value}
                  className="sr-only"
                />
                <div className="flex-1">
                  <div className="flex items-center">
                    <div className="text-sm font-medium text-slate-900 dark:text-slate-100">
                      {type.label}
                    </div>
                  </div>
                  <div className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    {type.description}
                  </div>
                </div>
                {promptType === type.value && (
                  <div className="absolute top-4 right-4">
                    <div className="h-2 w-2 rounded-full bg-primary-600" />
                  </div>
                )}
              </label>
            ))}
          </div>
        </div>

        {/* Submit button */}
        <button
          type="submit"
          disabled={isAnalyzing || isSubmitting || (!textContent && !selectedFile)}
          className="w-full btn-primary flex items-center justify-center py-3 text-lg"
        >
          {isAnalyzing || isSubmitting ? (
            <>
              <Loader2 className="animate-spin h-5 w-5 mr-2" />
              Analyzing Speech...
            </>
          ) : (
            'Analyze Speech'
          )}
        </button>
      </form>
    </motion.div>
  )
}