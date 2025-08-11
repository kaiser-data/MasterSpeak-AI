'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { authAPI } from '@/lib/api'
import { toast } from 'react-hot-toast'

export default function VerifyEmailPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [status, setStatus] = useState<'verifying' | 'success' | 'error' | 'missing-token'>('verifying')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const token = searchParams?.get('token')
    
    if (!token) {
      setStatus('missing-token')
      setMessage('No verification token provided')
      return
    }

    const verifyEmail = async () => {
      try {
        await authAPI.verifyEmail(token)
        setStatus('success')
        setMessage('Your email has been successfully verified! You can now sign in to your account.')
        toast.success('Email verified successfully!')
        
        // Redirect to signin after 3 seconds
        setTimeout(() => {
          router.push('/auth/signin')
        }, 3000)
        
      } catch (error: any) {
        console.error('Email verification error:', error)
        setStatus('error')
        
        if (error.response?.status === 400) {
          setMessage('Invalid or expired verification token. Please request a new verification email.')
        } else if (error.response?.status === 422) {
          setMessage('The verification token format is invalid.')
        } else {
          setMessage('Failed to verify email. Please try again or contact support.')
        }
        
        toast.error('Email verification failed')
      }
    }

    verifyEmail()
  }, [searchParams, router])

  const handleRequestNewToken = async () => {
    // For now, redirect to signin page where they can request a new token
    router.push('/auth/signin?message=verification-failed')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Email Verification
          </h2>
        </div>

        <div className="mt-8 space-y-6">
          <div className="rounded-md bg-white p-6 shadow-lg">
            {status === 'verifying' && (
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Verifying your email address...</p>
              </div>
            )}

            {status === 'success' && (
              <div className="text-center">
                <div className="rounded-full bg-green-100 p-2 w-12 h-12 mx-auto mb-4 flex items-center justify-center">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Email Verified!</h3>
                <p className="text-gray-600 mb-4">{message}</p>
                <p className="text-sm text-gray-500">Redirecting to sign in...</p>
              </div>
            )}

            {status === 'error' && (
              <div className="text-center">
                <div className="rounded-full bg-red-100 p-2 w-12 h-12 mx-auto mb-4 flex items-center justify-center">
                  <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Verification Failed</h3>
                <p className="text-gray-600 mb-6">{message}</p>
                <div className="space-y-3">
                  <button
                    onClick={handleRequestNewToken}
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Go to Sign In
                  </button>
                </div>
              </div>
            )}

            {status === 'missing-token' && (
              <div className="text-center">
                <div className="rounded-full bg-yellow-100 p-2 w-12 h-12 mx-auto mb-4 flex items-center justify-center">
                  <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Invalid Link</h3>
                <p className="text-gray-600 mb-6">{message}</p>
                <button
                  onClick={() => router.push('/auth/signin')}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Go to Sign In
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}