import { setupWorker } from 'msw/browser'
import { handlers } from './handlers'

// This configures a Service Worker with the given request handlers.
export const worker = setupWorker(...handlers)

// Initialize MSW in development when TRANSCRIPTION_UI flag is enabled
export async function initMocks() {
  if (typeof window === 'undefined') {
    // Server-side: no-op
    return
  }

  if (process.env.NODE_ENV === 'development' && process.env.NEXT_PUBLIC_TRANSCRIPTION_UI === '1') {
    console.log('🎭 Initializing MSW for transcription UI development...')
    
    try {
      await worker.start({
        onUnhandledRequest: 'bypass', // Don't warn about unhandled requests
        serviceWorker: {
          url: '/mockServiceWorker.js' // This file needs to be in public/ directory
        }
      })
      console.log('✅ MSW started successfully')
    } catch (error) {
      console.error('❌ Failed to start MSW:', error)
    }
  } else {
    console.log('⏭️ MSW not initialized (NODE_ENV:', process.env.NODE_ENV, ', TRANSCRIPTION_UI:', process.env.NEXT_PUBLIC_TRANSCRIPTION_UI, ')')
  }
}

// Already exported above on line 5