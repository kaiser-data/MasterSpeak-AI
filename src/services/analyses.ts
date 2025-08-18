/**
 * Analysis service for MasterSpeak-AI frontend.
 * Provides API communication for analysis persistence and retrieval.
 */

import { apiConfig } from '@/lib/env';
import { logAPICall } from '@/lib/log';

// Analysis types matching backend models
export interface AnalysisMetrics {
  word_count: number;
  clarity_score: number;
  structure_score: number;
  filler_word_count: number;
}

export interface Analysis {
  analysis_id: string;
  speech_id: string;
  user_id: string;
  transcript?: string;
  metrics?: AnalysisMetrics;
  summary?: string;
  feedback: string;
  created_at: string;
  updated_at: string;
}

export interface AnalysisListResponse {
  items: Analysis[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface AnalysisCompleteRequest {
  user_id: string;
  speech_id: string;
  transcript?: string;
  metrics?: AnalysisMetrics;
  summary?: string;
  feedback: string;
}

export interface AnalysisSearchParams {
  q?: string;
  min_clarity?: number;
  max_clarity?: number;
  min_structure?: number;
  max_structure?: number;
  start_date?: string;
  end_date?: string;
  page?: number;
  limit?: number;
}

export interface AnalysisCompleteResponse {
  analysis_id: string;
  speech_id: string;
  user_id: string;
  created_at: string;
  is_duplicate: boolean;
  transcript?: string;
  metrics?: AnalysisMetrics;
  summary?: string;
  feedback: string;
}

// Export and Share interfaces
export interface ShareTokenResponse {
  share_url: string;
  expires_at: string;
  token_id: string;
}

export interface ShareTokenCreate {
  analysis_id: string;
  expires_in_days?: number;
}

export interface SharedAnalysisResponse {
  analysis_id: string;
  speech_id: string;
  metrics?: AnalysisMetrics;
  summary?: string;
  feedback: string;
  created_at: string;
  transcript?: string;
  shared: boolean;
  transcript_included: boolean;
}

/**
 * Complete analysis with idempotent behavior.
 */
export async function completeAnalysis(
  request: AnalysisCompleteRequest
): Promise<AnalysisCompleteResponse> {
  return logAPICall(
    'POST',
    `${apiConfig.baseURL}/api/v1/analyses/complete`,
    async () => {
      const response = await fetch(`${apiConfig.baseURL}/api/v1/analyses/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return response.json();
    },
    request
  );
}

/**
 * Get recent analyses for dashboard display.
 */
export async function getRecentAnalyses(limit: number = 5): Promise<Analysis[]> {
  return logAPICall(
    'GET',
    `${apiConfig.baseURL}/api/v1/analyses/recent?limit=${limit}`,
    async () => {
      const response = await fetch(
        `${apiConfig.baseURL}/api/v1/analyses/recent?limit=${limit}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return response.json();
    }
  );
}

/**
 * Get paginated analyses for list page.
 */
export async function getAnalysesPage(
  page: number = 1,
  limit: number = 20
): Promise<AnalysisListResponse> {
  return logAPICall(
    'GET',
    `${apiConfig.baseURL}/api/v1/analyses?page=${page}&limit=${limit}`,
    async () => {
      const response = await fetch(
        `${apiConfig.baseURL}/api/v1/analyses?page=${page}&limit=${limit}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return response.json();
    }
  );
}

/**
 * Get single analysis details by ID.
 */
export async function getAnalysisById(analysisId: string): Promise<Analysis> {
  return logAPICall(
    'GET',
    `${apiConfig.baseURL}/api/v1/analyses/${analysisId}`,
    async () => {
      const response = await fetch(`${apiConfig.baseURL}/api/v1/analyses/${analysisId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        
        if (response.status === 404) {
          throw new Error('Analysis not found');
        }
        if (response.status === 403) {
          throw new Error('Access denied - analysis not owned by user');
        }
        
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return response.json();
    }
  );
}

/**
 * Search analyses with filters.
 */
export async function searchAnalyses(params: AnalysisSearchParams): Promise<AnalysisListResponse> {
  const searchParams = new URLSearchParams();
  
  if (params.q) searchParams.append('q', params.q);
  if (params.min_clarity !== undefined) searchParams.append('min_clarity', params.min_clarity.toString());
  if (params.max_clarity !== undefined) searchParams.append('max_clarity', params.max_clarity.toString());
  if (params.min_structure !== undefined) searchParams.append('min_structure', params.min_structure.toString());
  if (params.max_structure !== undefined) searchParams.append('max_structure', params.max_structure.toString());
  if (params.start_date) searchParams.append('start_date', params.start_date);
  if (params.end_date) searchParams.append('end_date', params.end_date);
  if (params.page !== undefined) searchParams.append('page', params.page.toString());
  if (params.limit !== undefined) searchParams.append('limit', params.limit.toString());
  
  return logAPICall(
    'GET',
    `${apiConfig.baseURL}/api/v1/analyses/search?${searchParams.toString()}`,
    async () => {
      const response = await fetch(
        `${apiConfig.baseURL}/api/v1/analyses/search?${searchParams.toString()}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return response.json();
    }
  );
}

// Utility functions for analysis display

/**
 * Format a date to a human-readable relative time.
 */
export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffMinutes = Math.floor(diffMs / (1000 * 60));

  if (diffDays > 7) {
    return date.toLocaleDateString();
  } else if (diffDays > 0) {
    return `${diffDays} day${diffDays === 1 ? '' : 's'} ago`;
  } else if (diffHours > 0) {
    return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`;
  } else if (diffMinutes > 0) {
    return `${diffMinutes} minute${diffMinutes === 1 ? '' : 's'} ago`;
  } else {
    return 'Just now';
  }
}

/**
 * Truncate text to a maximum length with ellipsis.
 */
export function truncateText(text: string, maxLength: number = 100): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + '...';
}

/**
 * Format score to display with color coding.
 */
export function formatScore(score: number, maxScore: number = 10): string {
  const percentage = (score / maxScore) * 100;
  return `${score}/${maxScore} (${percentage.toFixed(0)}%)`;
}

/**
 * Get score color class for Tailwind CSS.
 */
export function getScoreColorClass(score: number, maxScore: number = 10): string {
  const percentage = (score / maxScore) * 100;
  
  if (percentage >= 80) return 'text-green-600';
  if (percentage >= 60) return 'text-yellow-600';
  if (percentage >= 40) return 'text-orange-600';
  return 'text-red-600';
}

/**
 * Calculate overall analysis score from metrics.
 */
export function calculateOverallScore(metrics?: AnalysisMetrics): number {
  if (!metrics) return 0;
  
  // Weight different metrics (clarity and structure are more important)
  const clarityWeight = 0.4;
  const structureWeight = 0.4;
  const fillerWeight = 0.2;
  
  // Normalize filler word score (fewer is better, max 10 fillers = 0 score)
  const fillerScore = Math.max(0, 10 - metrics.filler_word_count);
  
  const weightedScore = 
    (metrics.clarity_score * clarityWeight) +
    (metrics.structure_score * structureWeight) +
    (fillerScore * fillerWeight);
    
  return Math.round(weightedScore * 10) / 10; // Round to 1 decimal place
}

// Export and Share Functions

/**
 * Export analysis as PDF (feature flagged).
 */
export async function exportAnalysisPDF(
  analysisId: string,
  includeTranscript: boolean = false
): Promise<Blob> {
  return logAPICall(
    'GET',
    `${apiConfig.baseURL}/api/v1/analyses/${analysisId}/export?include_transcript=${includeTranscript}`,
    async () => {
      const response = await fetch(
        `${apiConfig.baseURL}/api/v1/analyses/${analysisId}/export?include_transcript=${includeTranscript}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        
        if (response.status === 404) {
          throw new Error('Export functionality is not enabled or analysis not found');
        }
        if (response.status === 403) {
          throw new Error('Access denied - analysis not owned by user');
        }
        if (response.status === 500 && error.detail?.includes('reportlab')) {
          throw new Error('PDF generation not available. Please contact administrator.');
        }
        
        throw new Error(error.detail || `Export failed: ${response.statusText}`);
      }

      return response.blob();
    }
  );
}

/**
 * Create a shareable link for an analysis (feature flagged).
 */
export async function createShareLink(
  analysisId: string,
  expiresInDays: number = 7
): Promise<ShareTokenResponse> {
  const request: ShareTokenCreate = {
    analysis_id: analysisId,
    expires_in_days: expiresInDays
  };

  return logAPICall(
    'POST',
    `${apiConfig.baseURL}/api/v1/share/${analysisId}`,
    async () => {
      const response = await fetch(`${apiConfig.baseURL}/api/v1/share/${analysisId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        
        if (response.status === 404) {
          throw new Error('Share functionality is not enabled or analysis not found');
        }
        if (response.status === 403) {
          throw new Error('Access denied - analysis not owned by user');
        }
        if (response.status === 400) {
          throw new Error('Invalid request - expiration must be between 1 and 30 days');
        }
        
        throw new Error(error.detail || `Share failed: ${response.statusText}`);
      }

      return response.json();
    },
    request
  );
}

/**
 * Access a shared analysis using a share token (public endpoint).
 */
export async function getSharedAnalysis(token: string): Promise<SharedAnalysisResponse> {
  return logAPICall(
    'GET',
    `${apiConfig.baseURL}/api/v1/share/${token}`,
    async () => {
      const response = await fetch(`${apiConfig.baseURL}/api/v1/share/${token}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        
        if (response.status === 404) {
          throw new Error('Share link not found or expired');
        }
        
        throw new Error(error.detail || `Failed to access shared analysis: ${response.statusText}`);
      }

      return response.json();
    }
  );
}

/**
 * Check if export functionality is enabled.
 */
export function isExportEnabled(): boolean {
  return process.env.NEXT_PUBLIC_EXPORT_ENABLED === '1';
}

/**
 * Download a blob as a file.
 */
export function downloadBlob(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

// Alias for component compatibility
export const getAnalysisDetails = getAnalysisById;