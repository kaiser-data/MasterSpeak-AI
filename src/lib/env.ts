import { z } from 'zod';

// Environment variable schema with Zod validation
const envSchema = z.object({
  // API Configuration
  NEXT_PUBLIC_API_BASE: z
    .string()
    .url()
    .default('http://localhost:8000')
    .describe('Base URL for the FastAPI backend'),

  // Feature Flags
  NEXT_PUBLIC_TRANSCRIPTION_UI: z
    .enum(['0', '1', 'true', 'false'])
    .transform((val) => val === '1' || val === 'true')
    .default('0')
    .describe('Enable transcription UI features'),

  NEXT_PUBLIC_EXPORT_ENABLED: z
    .enum(['0', '1', 'true', 'false'])
    .transform((val) => val === '1' || val === 'true')
    .default('0')
    .describe('Enable PDF export and sharing features'),

  NEXT_PUBLIC_PROGRESS_UI: z
    .enum(['0', '1', 'true', 'false'])
    .transform((val) => val === '1' || val === 'true')
    .default('0')
    .describe('Enable progress tracking dashboard'),

  NEXT_PUBLIC_SHARE_LINKS: z
    .enum(['0', '1', 'true', 'false'])
    .transform((val) => val === '1' || val === 'true')
    .default('0')
    .describe('Enable shareable analysis links'),

  NEXT_PUBLIC_ADVANCED_ANALYTICS: z
    .enum(['0', '1', 'true', 'false'])
    .transform((val) => val === '1' || val === 'true')
    .default('0')
    .describe('Enable advanced analytics features'),

  // Development Configuration
  NODE_ENV: z
    .enum(['development', 'production', 'test'])
    .default('development')
    .describe('Runtime environment'),

  NEXT_PUBLIC_LOG_LEVEL: z
    .enum(['debug', 'info', 'warn', 'error'])
    .default('info')
    .describe('Frontend logging level'),

  // Optional: Monitoring and Analytics
  NEXT_PUBLIC_SENTRY_DSN: z
    .string()
    .url()
    .optional()
    .describe('Sentry DSN for error tracking'),

  NEXT_PUBLIC_ANALYTICS_ID: z
    .string()
    .optional()
    .describe('Analytics service ID (Google Analytics, etc.)'),
});

// Parse and validate environment variables
const parseEnv = () => {
  try {
    return envSchema.parse(process.env);
  } catch (error) {
    if (error instanceof z.ZodError) {
      const missingVars = error.errors
        .map((err) => `${err.path.join('.')}: ${err.message}`)
        .join('\n');
      
      throw new Error(
        `Environment validation failed:\n${missingVars}\n\n` +
        'Please check your .env.local file and ensure all required environment variables are set.'
      );
    }
    throw error;
  }
};

// Export validated environment variables
export const env = parseEnv();

// Feature flag helpers
export const features = {
  transcriptionUI: env.NEXT_PUBLIC_TRANSCRIPTION_UI,
  exportEnabled: env.NEXT_PUBLIC_EXPORT_ENABLED,
  progressUI: env.NEXT_PUBLIC_PROGRESS_UI,
  shareLinks: env.NEXT_PUBLIC_SHARE_LINKS,
  advancedAnalytics: env.NEXT_PUBLIC_ADVANCED_ANALYTICS,
} as const;

// Type-safe feature flag checker
export function isFeatureEnabled(feature: keyof typeof features): boolean {
  return features[feature];
}

// Environment helpers
export const isDevelopment = env.NODE_ENV === 'development';
export const isProduction = env.NODE_ENV === 'production';
export const isTest = env.NODE_ENV === 'test';

// API configuration
export const apiConfig = {
  baseURL: env.NEXT_PUBLIC_API_BASE,
  timeout: 30000, // 30 seconds
  retries: 3,
} as const;

// Development helpers
export function getEnvInfo() {
  if (!isDevelopment) {
    return 'Environment info only available in development';
  }

  return {
    nodeEnv: env.NODE_ENV,
    apiBase: env.NEXT_PUBLIC_API_BASE,
    features: features,
    logLevel: env.NEXT_PUBLIC_LOG_LEVEL,
  };
}

// Runtime environment validation
if (typeof window !== 'undefined') {
  // Client-side validation
  console.log('🔧 Environment validated successfully');
  
  if (isDevelopment) {
    console.log('🚀 Development mode features:', {
      transcriptionUI: features.transcriptionUI,
      exportEnabled: features.exportEnabled,
      progressUI: features.progressUI,
      shareLinks: features.shareLinks,
    });
  }
}

// Type exports for other modules
export type Environment = z.infer<typeof envSchema>;
export type FeatureFlags = typeof features;