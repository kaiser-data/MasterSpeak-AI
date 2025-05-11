import { Metadata } from 'next'
import Link from 'next/link'
import { Mic } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Authentication | MasterSpeak AI',
  description: 'Sign in or create an account to start analyzing your speech with AI-powered feedback.',
}

interface AuthLayoutProps {
  children: React.ReactNode
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex">
      {/* Left side - Auth form */}
      <div className="flex-1 flex flex-col justify-center py-12 px-4 sm:px-6 lg:flex-none lg:px-20 xl:px-24">
        <div className="mx-auto w-full max-w-sm lg:w-96">
          {/* Logo */}
          <div className="mb-8">
            <Link href="/" className="flex items-center space-x-2">
              <div className="h-10 w-10 bg-gradient-to-r from-primary-600 to-accent-600 rounded-lg flex items-center justify-center">
                <Mic className="h-6 w-6 text-white" />
              </div>
              <span className="text-2xl font-bold text-gradient">MasterSpeak AI</span>
            </Link>
          </div>

          {/* Auth content */}
          {children}
        </div>
      </div>

      {/* Right side - Feature showcase */}
      <div className="hidden lg:block relative flex-1">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-600 via-primary-700 to-accent-600">
          <div className="absolute inset-0 bg-black/20" />
          
          {/* Content overlay */}
          <div className="relative h-full flex flex-col justify-center px-12 text-white">
            <div className="max-w-md">
              <h2 className="text-3xl font-bold mb-6">
                Improve Your Communication with AI
              </h2>
              
              <div className="space-y-6">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <div className="h-2 w-2 rounded-full bg-white/80 mt-2" />
                  </div>
                  <div>
                    <h3 className="font-semibold mb-1">Real-time Analysis</h3>
                    <p className="text-white/80 text-sm">
                      Get instant feedback on your speech patterns and delivery
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <div className="h-2 w-2 rounded-full bg-white/80 mt-2" />
                  </div>
                  <div>
                    <h3 className="font-semibold mb-1">AI-Powered Insights</h3>
                    <p className="text-white/80 text-sm">
                      Advanced algorithms provide detailed performance metrics
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <div className="h-2 w-2 rounded-full bg-white/80 mt-2" />
                  </div>
                  <div>
                    <h3 className="font-semibold mb-1">Progress Tracking</h3>
                    <p className="text-white/80 text-sm">
                      Monitor your improvement over time with comprehensive analytics
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-12 p-6 bg-white/10 backdrop-blur-sm rounded-lg border border-white/20">
                <blockquote className="text-sm text-white/90 italic">
                  "MasterSpeak helped me become a more confident presenter. 
                  The AI feedback is incredibly precise and actionable."
                </blockquote>
                <div className="mt-3">
                  <div className="font-semibold text-sm">Sarah Chen</div>
                  <div className="text-xs text-white/70">Product Manager</div>
                </div>
              </div>
            </div>
          </div>

          {/* Decorative elements */}
          <div className="absolute top-20 right-20 w-32 h-32 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute bottom-32 right-32 w-24 h-24 rounded-full bg-accent-400/30 blur-2xl" />
          <div className="absolute top-1/2 right-12 w-16 h-16 rounded-full bg-primary-400/40 blur-xl" />
        </div>
      </div>
    </div>
  )
}