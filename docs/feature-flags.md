# Feature Flag Enforcement Strategy

## Overview
Feature flags control sprint goal rollout with backend-enforced availability and frontend UI gating. All flags default to disabled for safe deployment.

## Flag Definitions

### TRANSCRIPTION_UI=1 (Agent B)
**Purpose**: Gate audio transcription functionality
**Default**: 0 (disabled)
**Scope**: Backend API + Frontend UI

**Backend Enforcement:**
```python
# backend/config.py
class Settings(BaseSettings):
    transcription_ui: bool = Field(default=False, env="TRANSCRIPTION_UI")

# backend/api/v1/routes/transcription.py
@router.post("/transcribe")
async def transcribe_audio(settings: Settings = Depends(get_settings)):
    if not settings.transcription_ui:
        raise HTTPException(
            status_code=404, 
            detail="Transcription service not available"
        )
```

**Frontend Enforcement:**
```typescript
// src/lib/env.ts (already implemented)
export const features = {
  transcriptionUI: env.NEXT_PUBLIC_TRANSCRIPTION_UI,
} as const;

// src/app/dashboard/analyses/[id]/page.tsx
{features.transcriptionUI && (
  <TranscriptionSection analysisId={params.id} />
)}
```

### EXPORT_ENABLED=1 (Agent D)
**Purpose**: Gate PDF export and share link functionality
**Default**: 0 (disabled)
**Scope**: Backend API + Frontend UI

**Backend Enforcement:**
```python
# backend/api/v1/routes/export.py
@router.get("/{analysis_id}/export")
async def export_analysis(settings: Settings = Depends(get_settings)):
    if not settings.export_enabled:
        raise HTTPException(
            status_code=404,
            detail="Export functionality not available"
        )

# backend/api/v1/routes/share.py
@router.post("/{analysis_id}")
async def create_share_link(settings: Settings = Depends(get_settings)):
    if not settings.export_enabled:
        raise HTTPException(
            status_code=404,
            detail="Share functionality not available"
        )
```

**Frontend Enforcement:**
```typescript
// src/app/dashboard/analyses/[id]/page.tsx
{features.exportEnabled && (
  <div className="flex gap-2">
    <ExportButton analysisId={params.id} />
    <ShareButton analysisId={params.id} />
  </div>
)}
```

### PROGRESS_UI=1 (Agent E)
**Purpose**: Gate progress dashboard and metrics
**Default**: 0 (disabled)
**Scope**: Backend API + Frontend UI + Navigation

**Backend Enforcement:**
```python
# backend/api/v1/routes/metrics.py
@router.get("/analyses/metrics")
async def get_progress_metrics(settings: Settings = Depends(get_settings)):
    if not settings.progress_ui:
        raise HTTPException(
            status_code=404,
            detail="Progress metrics not available"
        )
```

**Frontend Enforcement:**
```typescript
// src/app/dashboard/layout.tsx
const navigation = [
  { name: 'Dashboard', href: '/dashboard' },
  { name: 'Analyses', href: '/dashboard/analyses' },
  ...(features.progressUI ? [{ name: 'Progress', href: '/dashboard/progress' }] : []),
];

// src/app/dashboard/progress/page.tsx
export default function ProgressPage() {
  if (!features.progressUI) {
    return <FeatureNotAvailable feature="Progress Tracking" />;
  }
  // ... component implementation
}
```

## Enforcement Architecture

### 1. Backend API Gating
```python
# backend/dependencies/feature_flags.py
from backend.config import get_settings
from fastapi import Depends, HTTPException

def require_transcription_ui(settings = Depends(get_settings)):
    if not settings.transcription_ui:
        raise HTTPException(404, "Feature not available")
    return True

def require_export_enabled(settings = Depends(get_settings)):
    if not settings.export_enabled:
        raise HTTPException(404, "Feature not available")
    return True

def require_progress_ui(settings = Depends(get_settings)):
    if not settings.progress_ui:
        raise HTTPException(404, "Feature not available")
    return True

# Usage in routes
@router.post("/transcribe", dependencies=[Depends(require_transcription_ui)])
async def transcribe_audio(...):
    # Implementation only runs if flag enabled
```

### 2. Frontend Component Gating
```typescript
// src/components/FeatureGate.tsx
interface FeatureGateProps {
  feature: keyof typeof features;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function FeatureGate({ feature, children, fallback }: FeatureGateProps) {
  if (!features[feature]) {
    return <>{fallback}</>;
  }
  return <>{children}</>;
}

// Usage throughout app
<FeatureGate feature="transcriptionUI">
  <TranscriptionUpload />
</FeatureGate>

<FeatureGate feature="exportEnabled">
  <ExportButtons />
</FeatureGate>
```

### 3. Service Layer Protection
```typescript
// src/services/analyses.ts
export class AnalysisService {
  async transcribeAudio(file: File): Promise<TranscriptionResult> {
    if (!features.transcriptionUI) {
      throw new FeatureNotAvailableError('Transcription UI is disabled');
    }
    // Make API call
  }

  async exportToPDF(analysisId: string): Promise<Blob> {
    if (!features.exportEnabled) {
      throw new FeatureNotAvailableError('Export is disabled');
    }
    // Make API call
  }

  async getProgressMetrics(): Promise<ProgressData> {
    if (!features.progressUI) {
      throw new FeatureNotAvailableError('Progress UI is disabled');
    }
    // Make API call
  }
}
```

## Deployment Strategy

### Development Environment
```bash
# .env (backend)
TRANSCRIPTION_UI=1
EXPORT_ENABLED=1
PROGRESS_UI=1

# .env.local (frontend)
NEXT_PUBLIC_TRANSCRIPTION_UI=1
NEXT_PUBLIC_EXPORT_ENABLED=1
NEXT_PUBLIC_PROGRESS_UI=1
```

### Staging Environment
```bash
# Test individual features
TRANSCRIPTION_UI=1
EXPORT_ENABLED=0
PROGRESS_UI=0
```

### Production Rollout
```bash
# Week 1: Agent A complete - no flags needed
# Week 2: Agent C complete - no flags needed

# Week 3: Agent B testing
TRANSCRIPTION_UI=1  # Enable for testing
EXPORT_ENABLED=0
PROGRESS_UI=0

# Week 4: Agent D testing  
TRANSCRIPTION_UI=1
EXPORT_ENABLED=1   # Enable for testing
PROGRESS_UI=0

# Week 5: Full rollout
TRANSCRIPTION_UI=1
EXPORT_ENABLED=1
PROGRESS_UI=1      # Enable final feature
```

## Flag Coordination Rules

### 1. Backend Controls Availability
- Backend flags are authoritative
- API returns 404 when feature disabled
- Frontend flags must match backend flags
- No client-side feature bypassing

### 2. Graceful Degradation
```typescript
// If backend rejects feature request
try {
  const result = await analysisService.transcribeAudio(file);
} catch (error) {
  if (error.status === 404) {
    showNotification('Transcription feature is currently unavailable');
    return;
  }
  throw error; // Other errors bubble up
}
```

### 3. Feature Flag Logging
```typescript
// Log feature flag usage for metrics
import { logFeatureUsage } from '@/lib/log';

function useTranscription() {
  useEffect(() => {
    logFeatureUsage('transcriptionUI', features.transcriptionUI);
  }, []);
}
```

### 4. Error Boundaries for Feature Failures
```typescript
// src/components/FeatureErrorBoundary.tsx
export class FeatureErrorBoundary extends ErrorBoundary {
  componentDidCatch(error: Error) {
    if (error.name === 'FeatureNotAvailableError') {
      // Handle gracefully, don't crash app
      logEvent({
        level: 'warn',
        message: 'Feature unavailable',
        metadata: { feature: error.feature }
      });
    }
  }
}
```

## Testing Strategy

### 1. Flag Combination Testing
```typescript
// test/feature-flags.test.ts
describe('Feature Flag Combinations', () => {
  it('transcription disabled should hide UI', () => {
    process.env.NEXT_PUBLIC_TRANSCRIPTION_UI = '0';
    render(<AnalysisDetailPage />);
    expect(screen.queryByTestId('transcription-section')).toBeNull();
  });

  it('export disabled should return 404', async () => {
    // Mock backend with EXPORT_ENABLED=0
    await expect(analysisService.exportToPDF('123')).rejects.toThrow('404');
  });
});
```

### 2. E2E Flag Testing
```typescript
// e2e/feature-flags.spec.ts
test('disabled features are not accessible', async ({ page }) => {
  // Set environment variables
  await page.goto('/dashboard/analyses/123');
  
  // Verify transcription section is hidden when flag off
  await expect(page.locator('[data-testid="transcription-section"]')).toBeHidden();
  
  // Verify export buttons are hidden when flag off
  await expect(page.locator('[data-testid="export-buttons"]')).toBeHidden();
});
```

## Monitoring & Rollback

### 1. Feature Flag Metrics
- Track feature usage rates
- Monitor error rates by feature
- Alert on flag mismatches between frontend/backend

### 2. Instant Rollback Capability
```bash
# Emergency disable via environment variables
# Railway backend
railway variables set TRANSCRIPTION_UI=0

# Vercel frontend  
vercel env add NEXT_PUBLIC_TRANSCRIPTION_UI 0 production
```

### 3. Gradual Rollout Support
```python
# Future: Percentage-based rollout
class AdvancedFeatureFlags:
    def is_transcription_enabled(self, user_id: str) -> bool:
        if not settings.transcription_ui:
            return False
        
        # Gradual rollout: enable for 10% of users
        user_hash = hash(user_id) % 100
        return user_hash < settings.transcription_rollout_percent
```

## Quality Assurance

### 1. Pre-deployment Checklist
- [ ] All flags documented in contracts.md
- [ ] Backend and frontend flags match
- [ ] API returns proper 404 for disabled features
- [ ] UI gracefully handles disabled features
- [ ] Error boundaries catch feature failures
- [ ] Logging captures feature usage

### 2. Agent Handoff Requirements
- [ ] Feature flag properly implemented
- [ ] Tests verify flag behavior
- [ ] Documentation updated
- [ ] Ready for controlled rollout

This strategy ensures safe, controlled rollout of sprint features with instant rollback capability and comprehensive monitoring.