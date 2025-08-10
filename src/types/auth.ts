export interface User {
  id: string
  email: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
  is_verified: boolean
  created_at?: string
  updated_at?: string
}

export interface AuthTokens {
  access_token: string
  token_type: string
  expires_in?: number
}

export interface SignInCredentials {
  email: string
  password: string
}

export interface SignUpData {
  email: string
  password: string
  full_name?: string
}

export interface ForgotPasswordData {
  email: string
}

export interface ResetPasswordData {
  token: string
  password: string
}

export interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  error: string | null
}

export interface AuthContextType extends AuthState {
  signIn: (credentials: SignInCredentials) => Promise<void>
  signUp: (data: SignUpData) => Promise<void>
  signOut: () => Promise<void>
  forgotPassword: (data: ForgotPasswordData) => Promise<void>
  resetPassword: (data: ResetPasswordData) => Promise<void>
  clearError: () => void
}