import axios, { AxiosError, AxiosResponse } from 'axios'
import { toast } from 'react-hot-toast'

// Use Next.js rewrites instead of hardcoded URLs
console.log('🔧 Using Next.js rewrites for API calls')

// Create axios instance with rewrite-based config
export const api = axios.create({
  baseURL: '/api/v1',  // Uses Next.js rewrites
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Create auth-specific client with credentials for cookie handling
export const authAPI_client = axios.create({
  baseURL: '/api',  // Direct to auth endpoints via rewrites
  timeout: 30000,
  withCredentials: true,  // Include cookies for auth
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Debug logging for API requests
    console.log('🚀 API Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      fullURL: `${config.baseURL}${config.url}`,
      headers: config.headers
    })
    
    // Get token from localStorage or cookie
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error: AxiosError) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('access_token')
      window.location.href = '/auth/signin'
      return Promise.reject(error)
    }

    if (error.response?.status === 429) {
      toast.error('Rate limit exceeded. Please try again later.')
      return Promise.reject(error)
    }

    if (error.response?.status === 500) {
      toast.error('Server error. Please try again later.')
      return Promise.reject(error)
    }

    if (error.code === 'ECONNABORTED') {
      toast.error('Request timeout. Please check your connection.')
      return Promise.reject(error)
    }

    if (!error.response) {
      // Log the actual error for debugging
      console.error('Network error details:', {
        message: error.message,
        code: error.code,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          baseURL: error.config?.baseURL,
        }
      })
      toast.error(`Network error: ${error.message}. Please check your connection.`)
      return Promise.reject(error)
    }

    return Promise.reject(error)
  }
)

// Response interceptor for auth client with X-Request-ID extraction
authAPI_client.interceptors.response.use(
  (response: AxiosResponse) => {
    // Extract X-Request-ID for debugging
    const requestId = response.headers['x-request-id']
    if (requestId) {
      console.log('🔍 Auth Response X-Request-ID:', requestId)
    }
    return response
  },
  (error: AxiosError) => {
    // Extract X-Request-ID from error response
    const requestId = error.response?.headers['x-request-id']
    if (requestId) {
      console.error('❌ Auth Error X-Request-ID:', requestId)
      // Attach to error for UI display
      ;(error as any).requestId = requestId
    }
    
    // Classify errors for better UX
    if (!error.response) {
      // CORS/preflight or network error
      const corsError = new Error('Sign-in blocked by browser (CORS).')
      corsError.name = 'CORSError'
      throw corsError
    }
    
    if (error.response.status === 401 || error.response.status === 403) {
      const authError = new Error('Invalid credentials.')
      authError.name = 'AuthError'
      throw authError
    }
    
    if (error.response.status >= 400 && error.response.status < 500) {
      const validationError = new Error((error.response.data as any)?.detail || 'Validation error.')
      validationError.name = 'ValidationError'
      throw validationError
    }
    
    if (error.response.status >= 500) {
      const serverError = new Error(`Server error${requestId ? ` (ID: ${requestId})` : ''}`)
      serverError.name = 'ServerError'
      throw serverError
    }
    
    throw error
  }
)

// API functions
export const authAPI = {
  signIn: async (credentials: { email: string; password: string }) => {
    const formData = new FormData()
    formData.append('username', credentials.email)
    formData.append('password', credentials.password)
    
    const response = await authAPI_client.post('/auth/jwt/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  signUp: async (userData: {
    email: string
    password: string
    full_name?: string
  }) => {
    const response = await api.post('/auth/register', userData)
    return response.data
  },

  signOut: async () => {
    const response = await api.post('/auth/jwt/logout')
    return response.data
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },

  forgotPassword: async (email: string) => {
    const response = await api.post('/auth/forgot-password', { email })
    return response.data
  },

  resetPassword: async (token: string, password: string) => {
    const response = await api.post('/auth/reset-password', { token, password })
    return response.data
  },

  verifyEmail: async (token: string) => {
    const response = await api.post('/auth/verify', { token })
    return response.data
  },

  requestVerify: async (email: string) => {
    const response = await api.post('/auth/request-verify-token', { email })
    return response.data
  },
}

export const speechAPI = {
  analyzeText: async (data: {
    text: string
    prompt?: string
    title?: string
  }) => {
    const payload = {
      text: data.text,
      prompt: data.prompt || 'default',
      title: data.title
    }

    const response = await api.post('/analysis/text', payload, {
      headers: {
        'Content-Type': 'application/json',
      },
    })
    return response.data
  },

  uploadAndAnalyze: async (data: {
    file: File
    prompt_type: string
  }) => {
    const formData = new FormData()
    formData.append('file', data.file)
    formData.append('prompt_type', data.prompt_type)

    const response = await api.post('/analysis/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  getAnalysisResults: async (speechId: string) => {
    const response = await api.get(`/analysis/results/${speechId}`)
    return response.data
  },

  getUserAnalyses: async (userId: string, skip = 0, limit = 100) => {
    const response = await api.get(`/analysis/user/${userId}`, {
      params: { skip, limit },
    })
    return response.data
  },
}

export const userAPI = {
  getUsers: async (skip = 0, limit = 100) => {
    const response = await api.get('/users/', {
      params: { skip, limit },
    })
    return response.data
  },

  getUser: async (userId: string) => {
    const response = await api.get(`/users/${userId}`)
    return response.data
  },

  getUserStatistics: async (userId: string) => {
    const response = await api.get(`/users/${userId}/statistics`)
    return response.data
  },
}

export const speechesAPI = {
  getSpeeches: async (skip = 0, limit = 100, userId?: string) => {
    const response = await api.get('/speeches/', {
      params: { skip, limit, user_id: userId },
    })
    return response.data
  },

  getSpeech: async (speechId: string) => {
    const response = await api.get(`/speeches/${speechId}`)
    return response.data
  },

  deleteSpeech: async (speechId: string) => {
    const response = await api.delete(`/speeches/${speechId}`)
    return response.data
  },

  getSpeechAnalysis: async (speechId: string) => {
    const response = await api.get(`/speeches/${speechId}/analysis`)
    return response.data
  },
}

export const healthAPI = {
  getHealth: async () => {
    const response = await api.get('/health')
    return response.data
  },

  getStatus: async () => {
    const response = await api.get('/status')
    return response.data
  },
}

export default api