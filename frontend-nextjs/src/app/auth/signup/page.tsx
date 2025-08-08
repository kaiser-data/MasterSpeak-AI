'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { toast } from 'react-hot-toast'
import { Eye, EyeOff, Loader2, CheckCircle } from 'lucide-react'
import { motion } from 'framer-motion'

import { signUpSchema, type SignUpFormData } from '@/lib/auth-schemas'
import { authAPI } from '@/lib/api'

export default function SignUpPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const router = useRouter()

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<SignUpFormData>({
    resolver: zodResolver(signUpSchema),
  })

  const password = watch('password')

  const getPasswordStrength = (password: string) => {
    if (!password) return 0
    let strength = 0
    if (password.length >= 8) strength++
    if (/[A-Z]/.test(password)) strength++
    if (/[a-z]/.test(password)) strength++
    if (/\d/.test(password)) strength++
    if (/[^A-Za-z0-9]/.test(password)) strength++
    return strength
  }

  const passwordStrength = getPasswordStrength(password || '')

  const onSubmit = async (data: SignUpFormData) => {
    setIsLoading(true)
    try {
      const { confirmPassword, terms, ...signUpData } = data
      
      await authAPI.signUp(signUpData)
      
      toast.success('Account created successfully! You can now sign in.')
      
      // Redirect to sign in page
      setTimeout(() => {
        router.push('/auth/signin')
      }, 1500)
    } catch (error: any) {
      console.error('Sign up error:', error)
      console.error('Error details:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
        code: error.code,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          baseURL: error.config?.baseURL,
        }
      })
      
      if (error.response?.status === 400) {
        if (error.response.data?.detail?.includes('already exists')) {
          toast.error('An account with this email already exists')
        } else {
          toast.error('Please check your information and try again')
        }
      } else if (error.response?.data?.detail) {
        toast.error(error.response.data.detail)
      } else if (error.code === 'ERR_NETWORK') {
        toast.error('Cannot connect to server. Please check if the API is running.')
      } else if (error.message) {
        toast.error(`Signup failed: ${error.message}`)
      } else {
        toast.error('Failed to create account. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
          Create your account
        </h1>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
          Start your journey to better communication with AI-powered speech analysis
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Full Name field */}
        <div>
          <label htmlFor="full_name" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            Full Name
          </label>
          <input
            {...register('full_name')}
            type="text"
            id="full_name"
            autoComplete="name"
            className="input-primary"
            placeholder="Enter your full name"
          />
          {errors.full_name && (
            <p className="mt-1 text-sm text-error-600 dark:text-error-400">
              {errors.full_name.message}
            </p>
          )}
        </div>

        {/* Email field */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            Email address
          </label>
          <input
            {...register('email')}
            type="email"
            id="email"
            autoComplete="email"
            className="input-primary"
            placeholder="Enter your email"
          />
          {errors.email && (
            <p className="mt-1 text-sm text-error-600 dark:text-error-400">
              {errors.email.message}
            </p>
          )}
        </div>

        {/* Password field */}
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            Password
          </label>
          <div className="relative">
            <input
              {...register('password')}
              type={showPassword ? 'text' : 'password'}
              id="password"
              autoComplete="new-password"
              className="input-primary pr-10"
              placeholder="Create a password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 flex items-center pr-3"
            >
              {showPassword ? (
                <EyeOff className="h-4 w-4 text-slate-400" />
              ) : (
                <Eye className="h-4 w-4 text-slate-400" />
              )}
            </button>
          </div>
          
          {/* Password strength indicator */}
          {password && (
            <div className="mt-2">
              <div className="flex space-x-1">
                {[...Array(5)].map((_, i) => (
                  <div
                    key={i}
                    className={`h-1 w-full rounded-full ${
                      i < passwordStrength
                        ? passwordStrength <= 2
                          ? 'bg-error-400'
                          : passwordStrength <= 3
                          ? 'bg-warning-400'
                          : 'bg-success-400'
                        : 'bg-slate-200 dark:bg-slate-700'
                    }`}
                  />
                ))}
              </div>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                {passwordStrength <= 2 && 'Weak password'}
                {passwordStrength === 3 && 'Medium strength'}
                {passwordStrength >= 4 && 'Strong password'}
              </p>
            </div>
          )}
          
          {errors.password && (
            <p className="mt-1 text-sm text-error-600 dark:text-error-400">
              {errors.password.message}
            </p>
          )}
        </div>

        {/* Confirm Password field */}
        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            Confirm Password
          </label>
          <div className="relative">
            <input
              {...register('confirmPassword')}
              type={showConfirmPassword ? 'text' : 'password'}
              id="confirmPassword"
              autoComplete="new-password"
              className="input-primary pr-10"
              placeholder="Confirm your password"
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute inset-y-0 right-0 flex items-center pr-3"
            >
              {showConfirmPassword ? (
                <EyeOff className="h-4 w-4 text-slate-400" />
              ) : (
                <Eye className="h-4 w-4 text-slate-400" />
              )}
            </button>
          </div>
          {errors.confirmPassword && (
            <p className="mt-1 text-sm text-error-600 dark:text-error-400">
              {errors.confirmPassword.message}
            </p>
          )}
        </div>

        {/* Terms and conditions */}
        <div className="flex items-start">
          <div className="flex items-center h-5">
            <input
              {...register('terms')}
              id="terms"
              type="checkbox"
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-slate-300 rounded"
            />
          </div>
          <div className="ml-3 text-sm">
            <label htmlFor="terms" className="text-slate-700 dark:text-slate-300">
              I agree to the{' '}
              <Link href="/terms" className="font-medium text-primary-600 hover:text-primary-500">
                Terms of Service
              </Link>{' '}
              and{' '}
              <Link href="/privacy" className="font-medium text-primary-600 hover:text-primary-500">
                Privacy Policy
              </Link>
            </label>
            {errors.terms && (
              <p className="mt-1 text-error-600 dark:text-error-400">
                {errors.terms.message}
              </p>
            )}
          </div>
        </div>

        {/* Submit button */}
        <button
          type="submit"
          disabled={isLoading || isSubmitting}
          className="w-full btn-primary flex items-center justify-center py-3"
        >
          {isLoading || isSubmitting ? (
            <>
              <Loader2 className="animate-spin h-4 w-4 mr-2" />
              Creating account...
            </>
          ) : (
            <>
              <CheckCircle className="h-4 w-4 mr-2" />
              Create account
            </>
          )}
        </button>

        {/* Features preview */}
        <div className="rounded-md bg-slate-50 dark:bg-slate-800 p-4">
          <h3 className="text-sm font-medium text-slate-800 dark:text-slate-200 mb-2">
            What you'll get:
          </h3>
          <ul className="text-sm text-slate-600 dark:text-slate-400 space-y-1">
            <li>• AI-powered speech analysis</li>
            <li>• Real-time feedback and suggestions</li>
            <li>• Progress tracking and analytics</li>
            <li>• Personalized improvement recommendations</li>
          </ul>
        </div>
      </form>

      {/* Sign in link */}
      <div className="mt-6 text-center">
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Already have an account?{' '}
          <Link
            href="/auth/signin"
            className="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400"
          >
            Sign in
          </Link>
        </p>
      </div>
    </motion.div>
  )
}