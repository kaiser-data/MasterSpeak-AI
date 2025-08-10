import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/providers/Providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: {
    default: 'MasterSpeak AI v2.4 - DEPLOYMENT TEST',
    template: '%s | MasterSpeak AI v2.4',
  },
  description: 'Advanced Speech Analysis with AI-powered feedback for improved communication skills',
  keywords: ['speech analysis', 'AI feedback', 'communication', 'presentation skills', 'public speaking'],
  authors: [{ name: 'MasterSpeak Team' }],
  creator: 'MasterSpeak AI',
  metadataBase: new URL(process.env.NEXTAUTH_URL || 'http://localhost:3000'),
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: process.env.NEXTAUTH_URL || 'http://localhost:3000',
    title: 'MasterSpeak AI - Advanced Speech Analysis',
    description: 'Improve your communication skills with AI-powered speech analysis and feedback',
    siteName: 'MasterSpeak AI',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'MasterSpeak AI',
    description: 'Advanced Speech Analysis with AI-powered feedback',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
        <meta name="theme-color" content="#0ea5e9" />
      </head>
      <body className={`${inter.className} antialiased`}>
        <Providers>
          {/* DEPLOYMENT TEST v2.4 - VERY VISIBLE */}
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            backgroundColor: '#dc2626',
            color: 'white',
            textAlign: 'center',
            padding: '8px',
            fontSize: '18px',
            fontWeight: 'bold',
            zIndex: 9999
          }}>
            🚨 DEPLOYMENT TEST v2.4 - IF YOU SEE THIS, DEPLOYMENT WORKS! 🚨
          </div>
          <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800" style={{paddingTop: '50px'}}>
            {children}
          </div>
        </Providers>
      </body>
    </html>
  )
}