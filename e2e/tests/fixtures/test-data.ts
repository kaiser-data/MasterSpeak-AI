export const testUsers = {
  demo: {
    email: 'demo@masterspeak.ai',
    password: 'Demo123!',
    fullName: 'Demo User'
  },
  testUser: {
    email: 'test@playwright.com', 
    password: 'Test123!',
    fullName: 'Playwright Test User'
  }
};

export const testAudioData = {
  // Base64 encoded short audio sample (1 second of silence)
  shortSample: 'UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj',
  
  // Sample speech texts for analysis
  speechTexts: {
    basic: 'Hello, this is a test speech for analysis. I am speaking clearly and slowly.',
    complex: 'The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet and is commonly used for testing purposes.',
    professional: 'Good morning everyone. Today I would like to present our quarterly results and discuss our strategic initiatives for the upcoming fiscal year.'
  },

  // Expected analysis fields
  expectedFields: [
    'clarity_score',
    'confidence_score', 
    'pace_analysis',
    'volume_analysis',
    'suggestions',
    'overall_score'
  ]
};

export const apiEndpoints = {
  auth: {
    login: '/api/v1/auth/jwt/login',
    register: '/api/v1/auth/register',
    me: '/api/v1/users/me'
  },
  analysis: {
    textAnalysis: '/api/v1/analysis/text',
    audioUpload: '/api/v1/analysis/upload',
    getResults: '/api/v1/analysis'
  },
  health: '/health'
};

export const selectors = {
  auth: {
    emailInput: '[name="email"]',
    passwordInput: '[name="password"]', 
    loginButton: '[type="submit"]',
    signupButton: 'text=Sign Up',
    loginLink: 'text=Sign In',
    errorMessage: '[role="alert"]'
  },
  
  dashboard: {
    welcomeMessage: 'text=Welcome',
    analysisCard: '[data-testid="analysis-card"]',
    uploadButton: 'text=Upload Audio',
    recordButton: 'text=Record Speech',
    textAnalysisButton: 'text=Text Analysis'
  },

  speechAnalysis: {
    fileUpload: 'input[type="file"]',
    textInput: '[data-testid="speech-text-input"]',
    recordButton: '[data-testid="record-button"]',
    stopButton: '[data-testid="stop-button"]',
    analyzeButton: '[data-testid="analyze-button"]',
    loadingSpinner: '[data-testid="loading-spinner"]',
    results: '[data-testid="analysis-results"]',
    clarityScore: '[data-testid="clarity-score"]',
    confidenceScore: '[data-testid="confidence-score"]',
    suggestions: '[data-testid="suggestions"]'
  },

  navigation: {
    homeLink: 'text=Home',
    dashboardLink: 'text=Dashboard', 
    profileLink: 'text=Profile',
    logoutButton: 'text=Logout'
  }
};