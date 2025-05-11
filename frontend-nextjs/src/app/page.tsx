'use client'

import { useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { 
  Mic, 
  Brain, 
  BarChart3, 
  Zap, 
  Users, 
  Shield, 
  ArrowRight,
  Play,
  CheckCircle
} from 'lucide-react'

const features = [
  {
    icon: Mic,
    title: 'Speech Analysis',
    description: 'Advanced AI-powered analysis of your speech patterns, clarity, and delivery',
  },
  {
    icon: Brain,
    title: 'AI Feedback',
    description: 'Intelligent recommendations to improve your communication effectiveness',
  },
  {
    icon: BarChart3,
    title: 'Performance Metrics',
    description: 'Detailed insights into your speaking performance with actionable data',
  },
  {
    icon: Zap,
    title: 'Real-time Processing',
    description: 'Instant analysis and feedback to help you improve immediately',
  },
  {
    icon: Users,
    title: 'Progress Tracking',
    description: 'Monitor your improvement over time with comprehensive analytics',
  },
  {
    icon: Shield,
    title: 'Secure & Private',
    description: 'Your data is protected with enterprise-grade security measures',
  },
]

const testimonials = [
  {
    name: 'Sarah Chen',
    role: 'Product Manager',
    content: 'MasterSpeak helped me become a more confident presenter. The AI feedback is incredibly precise.',
  },
  {
    name: 'David Rodriguez',
    role: 'Sales Director',
    content: 'My presentation skills improved dramatically after using MasterSpeak for just one month.',
  },
  {
    name: 'Emily Johnson',
    role: 'CEO',
    content: 'The insights provided by MasterSpeak are game-changing for anyone serious about communication.',
  },
]

export default function HomePage() {
  const [isVideoPlaying, setIsVideoPlaying] = useState(false)

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="container-responsive py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="h-8 w-8 bg-gradient-to-r from-primary-600 to-accent-600 rounded-lg flex items-center justify-center">
              <Mic className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gradient">MasterSpeak AI</span>
          </div>
          
          <div className="hidden md:flex items-center space-x-8">
            <Link href="#features" className="nav-link">Features</Link>
            <Link href="#how-it-works" className="nav-link">How It Works</Link>
            <Link href="#testimonials" className="nav-link">Testimonials</Link>
            <Link href="#pricing" className="nav-link">Pricing</Link>
          </div>

          <div className="flex items-center space-x-4">
            <Link href="/auth/signin" className="nav-link">
              Sign In
            </Link>
            <Link href="/auth/signup" className="btn-primary">
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container-responsive section-spacing">
        <div className="text-center max-w-4xl mx-auto">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-4xl md:text-6xl font-bold mb-6"
          >
            Master Your{' '}
            <span className="text-gradient">Communication</span>{' '}
            with AI
          </motion.h1>
          
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-xl text-slate-600 dark:text-slate-300 mb-8 leading-relaxed"
          >
            Get instant AI-powered feedback on your speech patterns, clarity, and delivery.
            Improve your presentations, meetings, and everyday communication with precision insights.
          </motion.p>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12"
          >
            <Link href="/auth/signup" className="btn-primary text-lg px-8 py-3">
              Start Analyzing Speech
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
            
            <button 
              onClick={() => setIsVideoPlaying(true)}
              className="btn-outline text-lg px-8 py-3 flex items-center"
            >
              <Play className="mr-2 h-5 w-5" />
              Watch Demo
            </button>
          </motion.div>

          {/* Demo metrics */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-8 pt-12 border-t border-slate-200 dark:border-slate-700"
          >
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">10K+</div>
              <div className="text-sm text-slate-600 dark:text-slate-400">Speeches Analyzed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">95%</div>
              <div className="text-sm text-slate-600 dark:text-slate-400">Accuracy Rate</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">2.5x</div>
              <div className="text-sm text-slate-600 dark:text-slate-400">Faster Improvement</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">1000+</div>
              <div className="text-sm text-slate-600 dark:text-slate-400">Happy Users</div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="section-spacing bg-slate-50 dark:bg-slate-800/50">
        <div className="container-responsive">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Powerful Features for{' '}
              <span className="text-gradient">Better Communication</span>
            </h2>
            <p className="text-xl text-slate-600 dark:text-slate-300 max-w-3xl mx-auto">
              Our AI-powered platform provides comprehensive analysis and actionable insights 
              to help you become a more effective communicator.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="card-hover"
              >
                <div className="h-12 w-12 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center mb-4">
                  <feature.icon className="h-6 w-6 text-primary-600 dark:text-primary-400" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-slate-600 dark:text-slate-300">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="section-spacing">
        <div className="container-responsive">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              How It Works
            </h2>
            <p className="text-xl text-slate-600 dark:text-slate-300 max-w-3xl mx-auto">
              Get started with MasterSpeak in three simple steps
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: '01',
                title: 'Upload or Record',
                description: 'Upload an audio file or record your speech directly in the platform',
              },
              {
                step: '02', 
                title: 'AI Analysis',
                description: 'Our advanced AI analyzes your speech for clarity, pace, and effectiveness',
              },
              {
                step: '03',
                title: 'Get Insights',
                description: 'Receive detailed feedback and actionable recommendations for improvement',
              },
            ].map((step, index) => (
              <motion.div
                key={step.step}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <div className="h-16 w-16 bg-gradient-to-r from-primary-600 to-accent-600 rounded-full flex items-center justify-center text-white font-bold text-xl mx-auto mb-4">
                  {step.step}
                </div>
                <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                <p className="text-slate-600 dark:text-slate-300">{step.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="section-spacing bg-slate-50 dark:bg-slate-800/50">
        <div className="container-responsive">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              What Our Users Say
            </h2>
            <p className="text-xl text-slate-600 dark:text-slate-300">
              Join thousands of professionals who have improved their communication skills
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={testimonial.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="card"
              >
                <div className="mb-4">
                  <div className="flex text-yellow-400 mb-2">
                    {[...Array(5)].map((_, i) => (
                      <svg key={i} className="h-4 w-4 fill-current" viewBox="0 0 20 20">
                        <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                      </svg>
                    ))}
                  </div>
                  <p className="text-slate-600 dark:text-slate-300 mb-4">"{testimonial.content}"</p>
                </div>
                <div>
                  <div className="font-semibold">{testimonial.name}</div>
                  <div className="text-sm text-slate-500 dark:text-slate-400">{testimonial.role}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-spacing">
        <div className="container-responsive">
          <div className="card bg-gradient-to-r from-primary-600 to-accent-600 text-white text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready to Master Your Communication?
            </h2>
            <p className="text-xl mb-8 opacity-90">
              Join thousands of professionals who have transformed their speaking skills with MasterSpeak AI
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/auth/signup" className="bg-white text-primary-600 hover:bg-slate-50 font-medium px-8 py-3 rounded-lg transition-colors duration-200">
                Start Free Trial
              </Link>
              <Link href="#features" className="text-white hover:text-slate-200 font-medium px-8 py-3 border border-white/30 rounded-lg hover:bg-white/10 transition-colors duration-200">
                Learn More
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-12">
        <div className="container-responsive">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="h-8 w-8 bg-gradient-to-r from-primary-600 to-accent-600 rounded-lg flex items-center justify-center">
                  <Mic className="h-5 w-5 text-white" />
                </div>
                <span className="text-xl font-bold">MasterSpeak AI</span>
              </div>
              <p className="text-slate-400">
                Empowering better communication through AI-powered speech analysis.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <div className="space-y-2 text-slate-400">
                <Link href="#features" className="block hover:text-white transition-colors">Features</Link>
                <Link href="#pricing" className="block hover:text-white transition-colors">Pricing</Link>
                <Link href="/api-docs" className="block hover:text-white transition-colors">API</Link>
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <div className="space-y-2 text-slate-400">
                <Link href="/about" className="block hover:text-white transition-colors">About</Link>
                <Link href="/contact" className="block hover:text-white transition-colors">Contact</Link>
                <Link href="/careers" className="block hover:text-white transition-colors">Careers</Link>
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Legal</h3>
              <div className="space-y-2 text-slate-400">
                <Link href="/privacy" className="block hover:text-white transition-colors">Privacy Policy</Link>
                <Link href="/terms" className="block hover:text-white transition-colors">Terms of Service</Link>
                <Link href="/security" className="block hover:text-white transition-colors">Security</Link>
              </div>
            </div>
          </div>

          <div className="border-t border-slate-700 mt-8 pt-8 text-center text-slate-400">
            <p>&copy; 2025 MasterSpeak AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}