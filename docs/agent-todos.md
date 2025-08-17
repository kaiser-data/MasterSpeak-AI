# Per-Agent TODO Lists & Specifications

## 🔹 Agent A: Analysis Persistence Foundation

### Backend Models & Database
- [ ] **Create `backend/models/analysis.py`**
  ```python
  class Analysis(SQLModel, table=True):
      id: UUID = Field(default_factory=uuid4, primary_key=True)
      speech_id: UUID = Field(foreign_key="speech.id")
      user_id: UUID = Field(foreign_key="user.id")
      transcript: Optional[str] = None    # PII: Never logged
      metrics: Optional[dict] = None      # JSON: {word_count, clarity_score, structure_score, filler_word_count}
      summary: Optional[str] = None       # AI-generated summary
      feedback: str                       # Required feedback content
      created_at: datetime = Field(default_factory=datetime.utcnow)
      updated_at: datetime = Field(default_factory=datetime.utcnow)
      
      __table_args__ = (UniqueConstraint("user_id", "speech_id"),)  # Idempotency
  ```

- [ ] **Create database migration for Analysis table**
  ```sql
  -- Migration: Add analysis table with unique constraint
  CREATE TABLE analysis (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      speech_id UUID NOT NULL REFERENCES speech(id) ON DELETE CASCADE,
      user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
      transcript TEXT,
      metrics JSONB,
      summary TEXT,
      feedback TEXT NOT NULL,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
      updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
      UNIQUE(user_id, speech_id)
  );
  
  CREATE INDEX idx_analysis_user_id ON analysis(user_id);
  CREATE INDEX idx_analysis_created_at ON analysis(created_at DESC);
  ```

### Repository Layer
- [ ] **Create `backend/repositories/analysis_repo.py`**
  ```python
  class AnalysisRepository:
      def __init__(self, session: AsyncSession):
          self.session = session
      
      async def get_by_user_speech(self, user_id: UUID, speech_id: UUID) -> Optional[Analysis]:
          # Check for existing analysis (idempotency)
      
      async def create(self, analysis_data: AnalysisCreate) -> Analysis:
          # Idempotent create - return existing if duplicate
      
      async def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 20) -> List[Analysis]:
          # Paginated user analyses with speech details
      
      async def get_by_id(self, analysis_id: UUID, user_id: UUID) -> Optional[Analysis]:
          # Get single analysis with ownership check
  ```

### Service Layer  
- [ ] **Create `backend/services/analysis_service.py`**
  ```python
  class AnalysisService:
      def __init__(self, repo: AnalysisRepository):
          self.repo = repo
      
      async def save_analysis(
          self, user_id: UUID, speech_id: UUID,
          transcript: Optional[str] = None,
          metrics: Optional[dict] = None,
          summary: Optional[str] = None,
          feedback: str
      ) -> Tuple[Analysis, bool]:  # (analysis, is_duplicate)
          # Idempotent save with ownership validation
          
      async def get_recent_analyses(self, user_id: UUID, limit: int = 5) -> List[Analysis]:
          # Recent analyses for dashboard
  ```

### API Routes
- [ ] **Create `backend/api/v1/routes/analyses.py`**
  ```python
  @router.post("/analysis/complete")
  async def complete_analysis(
      request: AnalysisCompleteRequest,
      current_user = Depends(get_current_user),
      service: AnalysisService = Depends()
  ) -> AnalysisCompleteResponse:
      # Validate speech ownership
      # Save analysis idempotently  
      # Return {analysis_id, is_duplicate, created_at, summary?, metrics?}
  
  @router.get("/analyses")
  async def get_analyses(
      page: int = 1, limit: int = 20,
      current_user = Depends(get_current_user),
      service: AnalysisService = Depends()
  ) -> PaginatedAnalysesResponse:
      # Return {items, total, page, page_size, total_pages}
  ```

### Testing Requirements
- [ ] **Unit tests for analysis_repo.py** (80%+ coverage)
  - Test idempotency: duplicate calls return same analysis
  - Test unique constraint enforcement
  - Test pagination and filtering

- [ ] **Unit tests for analysis_service.py** (80%+ coverage)
  - Test ownership validation
  - Test error handling for invalid speech_id
  - Test forbidden access for non-owner

- [ ] **Integration tests for analyses routes** (80%+ coverage)
  - Test POST /analysis/complete idempotency
  - Test GET /analyses pagination
  - Test error responses match docs/contracts.md

### Quality Gates
- [ ] All tests pass with 80%+ coverage
- [ ] API responses match docs/contracts.md exactly
- [ ] Database migration is additive-only
- [ ] Unique constraint prevents duplicate analyses
- [ ] Error handling covers all documented error codes (400, 403, 404, 422)
- [ ] PII protection: transcript field never logged

---

## 🔹 Agent C: History & Navigation Framework

### Frontend Services
- [ ] **Update `src/services/analyses.ts`**
  ```typescript
  // Add new methods using Agent A's APIs
  export async function getAnalysesPage(page: number, limit: number): Promise<PaginatedAnalysesResponse> {
    const response = await api.get('/analyses', {
      params: { page, limit }
    });
    return response.data;
  }
  
  export async function getAnalysisById(id: string): Promise<Analysis> {
    const response = await api.get(`/analyses/${id}`);
    return response.data;
  }
  
  export async function createAnalysis(data: CreateAnalysisRequest): Promise<Analysis> {
    const response = await api.post('/analysis/complete', data);
    return response.data;
  }
  
  // Utility functions
  export function formatRelativeTime(date: string): string {
    // Format dates for display
  }
  
  export function truncateText(text: string, maxLength: number): string {
    // Truncate text with ellipsis
  }
  ```

### Page Components
- [ ] **Enhance `src/app/dashboard/analyses/page.tsx`** (already exists)
  ```typescript
  // Enhanced server component with:
  // - Pagination using URL params (?page=1)
  // - Loading states with skeleton UI
  // - Error boundaries with retry
  // - Empty state with CTA
  // - Responsive grid layout
  // - Click handlers for navigation to detail page
  ```

- [ ] **Create `src/app/dashboard/analyses/[id]/page.tsx`**
  ```typescript
  export default function AnalysisDetailPage({ params }: { params: { id: string } }) {
    // Server component structure:
    // - AnalysisHeader: title, date, metrics overview
    // - AnalysisContent: feedback, extensible for transcription
    // - AnalysisActions: placeholder for export/share buttons
    // - Error handling for 403/404
    // - Loading states and fallbacks
  }
  ```

### Component Architecture
- [ ] **Create reusable analysis components**
  ```typescript
  // src/components/analysis/AnalysisCard.tsx
  interface AnalysisCardProps {
    analysis: AnalysisItem;
    onClick?: () => void;
  }
  
  // src/components/analysis/AnalysisHeader.tsx
  interface AnalysisHeaderProps {
    analysis: Analysis;
    children?: ReactNode; // For future export/share buttons
  }
  
  // src/components/analysis/AnalysisMetrics.tsx
  interface AnalysisMetricsProps {
    metrics: AnalysisMetrics;
    layout?: 'horizontal' | 'vertical';
  }
  ```

### Navigation Updates
- [ ] **Update dashboard navigation**
  ```typescript
  // src/app/dashboard/page.tsx
  // Update "View All" button to link to /dashboard/analyses
  // Update recent analyses to link to detail pages
  
  // src/app/dashboard/layout.tsx  
  // Add navigation breadcrumbs
  // Update sidebar/navigation menu
  ```

### Type Definitions
- [ ] **Create TypeScript types**
  ```typescript
  // src/types/analysis.ts
  interface Analysis {
    analysis_id: string;
    speech_id: string;
    user_id: string;
    speech_title: string;
    transcript?: string;
    metrics: AnalysisMetrics;
    summary?: string;
    feedback: string;
    created_at: string;
    updated_at: string;
  }
  
  interface PaginatedAnalysesResponse {
    items: AnalysisItem[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  }
  ```

### Testing Requirements
- [ ] **Component tests** (80%+ coverage)
  - Test analyses list renders correctly
  - Test pagination controls work
  - Test analysis detail page loads
  - Test error states and loading states
  - Test responsive design

- [ ] **Service tests** (80%+ coverage)
  - Test API integration with mock responses
  - Test error handling for network failures
  - Test data transformation utilities

### Quality Gates
- [ ] All pages load without errors
- [ ] Pagination works correctly with backend API
- [ ] Analysis detail page displays all analysis data
- [ ] Navigation is intuitive and accessible (WCAG 2.1 AA)
- [ ] Component architecture supports extension by Agent B
- [ ] Mobile-responsive design (320px+ width)

---

## 🔹 Agent B: Transcription UI & Audio Processing

### Backend Transcription Service
- [ ] **Create `backend/services/transcription_service.py`**
  ```python
  class TranscriptionService:
      def __init__(self, openai_client, settings):
          self.openai_client = openai_client
          self.settings = settings
      
      async def transcribe_audio(self, file: UploadFile, language: str = "en", model: str = "whisper-1") -> TranscriptionResult:
          # Validate file type and size (<10MB)
          # Call OpenAI Whisper API
          # Return structured transcription result
          # Handle API errors and timeouts
  ```

- [ ] **Create `backend/api/v1/routes/transcription.py`**
  ```python
  @router.post("/transcribe")
  @require_transcription_ui  # Feature flag dependency
  async def transcribe_audio(
      file: UploadFile = File(...),
      language: str = Form("en"),
      model: str = Form("whisper-1"),
      service: TranscriptionService = Depends()
  ) -> TranscriptionResponse:
      # Validate audio file format (mp3, wav, m4a)
      # Process with transcription service
      # Return {transcript, language, duration_seconds, word_count, confidence_score, processing_time_ms}
  ```

### Frontend Components  
- [ ] **Create `src/components/ui/TranscriptionUpload.tsx`**
  ```typescript
  interface TranscriptionUploadProps {
    onTranscriptionComplete: (result: TranscriptionResult) => void;
    onError: (error: string) => void;
  }
  
  export function TranscriptionUpload({ onTranscriptionComplete, onError }: TranscriptionUploadProps) {
    // File drag-and-drop zone
    // Progress indicator during upload/processing
    // Audio format validation (mp3, wav, m4a)
    // File size validation (<10MB)
    // Error handling with retry button
    // Feature flag gating
  }
  ```

- [ ] **Create transcription section for analysis detail**
  ```typescript
  // src/components/analysis/TranscriptionSection.tsx
  interface TranscriptionSectionProps {
    analysisId: string;
    transcript?: string;
  }
  
  export function TranscriptionSection({ analysisId, transcript }: TranscriptionSectionProps) {
    // Collapsible transcript display
    // Copy to clipboard functionality
    // Upload new transcription (if none exists)
    // Feature flag gating (TRANSCRIPTION_UI)
  }
  ```

### Service Integration
- [ ] **Add transcription methods to `src/services/analyses.ts`**
  ```typescript
  export async function transcribeAudio(file: File, language?: string): Promise<TranscriptionResult> {
    if (!features.transcriptionUI) {
      throw new FeatureNotAvailableError('Transcription UI is disabled');
    }
    // FormData upload to /transcribe endpoint
  }
  
  export async function updateAnalysisTranscript(analysisId: string, transcript: string): Promise<void> {
    // Update analysis with transcript data
  }
  ```

### UI Integration
- [ ] **Update `src/app/dashboard/analyses/[id]/page.tsx`**
  ```typescript
  // Add transcription section to analysis detail
  {features.transcriptionUI && (
    <TranscriptionSection 
      analysisId={params.id} 
      transcript={analysis.transcript} 
    />
  )}
  ```

### Testing Requirements
- [ ] **Backend tests** (80%+ coverage)
  - Test transcription service with mock OpenAI responses
  - Test file validation (type, size limits)
  - Test feature flag enforcement
  - Test error handling for API failures

- [ ] **Frontend tests** (80%+ coverage)
  - Test file upload component behavior
  - Test feature flag gating
  - Test error states and retry functionality
  - Test transcript display and copy functionality

### Quality Gates
- [ ] Transcription service handles multiple audio formats correctly
- [ ] File upload shows progress and handles errors gracefully
- [ ] Transcript display is properly formatted and copyable
- [ ] Feature flag (TRANSCRIPTION_UI) correctly shows/hides features
- [ ] Audio files >10MB are rejected with clear error message
- [ ] Integration works with Agent C's analysis detail framework

---

## 🔹 Agent D: Export & Share Functionality

### Backend Models & Services
- [ ] **Create `backend/models/share_token.py`**
  ```python
  class ShareToken(SQLModel, table=True):
      id: UUID = Field(default_factory=uuid4, primary_key=True)
      analysis_id: UUID = Field(foreign_key="analysis.id")
      hashed_token: str = Field(index=True)  # SHA-256 hash, never store plain
      expires_at: datetime
      created_at: datetime = Field(default_factory=datetime.utcnow)
      
      # Security: 72-hour expiration by default
  ```

- [ ] **Create `backend/services/export_service.py`**
  ```python
  class ExportService:
      async def generate_pdf(self, analysis: Analysis, include_transcript: bool = False) -> bytes:
          # Professional PDF formatting
          # Include analysis metrics, feedback
          # Conditionally include transcript based on flag
          # Return PDF binary data
  
      async def create_share_token(self, analysis_id: UUID, expires_in_hours: int = 72) -> ShareToken:
          # Generate cryptographically secure token
          # Hash token before storage (never store plain)
          # Set expiration time
          # Return token for URL generation
  ```

### API Routes
- [ ] **Create `backend/api/v1/routes/export.py`**
  ```python
  @router.get("/{analysis_id}/export")
  @require_export_enabled  # Feature flag dependency
  async def export_analysis(
      analysis_id: UUID,
      format: str = "pdf",
      include_transcript: bool = False,
      current_user = Depends(get_current_user),
      service: ExportService = Depends()
  ) -> Response:
      # Validate ownership
      # Generate PDF with export service
      # Return binary data with proper headers
  ```

- [ ] **Create `backend/api/v1/routes/share.py`**
  ```python
  @router.post("/{analysis_id}")
  @require_export_enabled
  async def create_share_link(
      analysis_id: UUID,
      request: CreateShareRequest,
      current_user = Depends(get_current_user),
      service: ExportService = Depends()
  ) -> ShareResponse:
      # Create secure share token
      # Return {share_url, token, expires_at, created_at}
  
  @router.get("/share/{token}")
  async def get_shared_analysis(
      token: str,
      service: ExportService = Depends()
  ) -> PublicAnalysisResponse:
      # Validate token and expiration
      # Return redacted analysis data (no PII)
      # Include transcript only if ALLOW_TRANSCRIPT_SHARE=1
  ```

### Frontend Components
- [ ] **Create export/share UI components**
  ```typescript
  // src/components/analysis/ExportButtons.tsx
  interface ExportButtonsProps {
    analysisId: string;
    analysis: Analysis;
  }
  
  export function ExportButtons({ analysisId, analysis }: ExportButtonsProps) {
    // PDF export button with download handling
    // Share link creation with copy functionality
    // Loading states during processing
    // Feature flag gating (EXPORT_ENABLED)
  }
  
  // src/components/analysis/ShareDialog.tsx
  interface ShareDialogProps {
    analysisId: string;
    onClose: () => void;
  }
  
  export function ShareDialog({ analysisId, onClose }: ShareDialogProps) {
    // Share link generation form
    // Expiration time selection
    // Copy link functionality
    // Security warnings about public sharing
  }
  ```

### Public Share Page
- [ ] **Create `src/app/share/[token]/page.tsx`**
  ```typescript
  export default function PublicSharePage({ params }: { params: { token: string } }) {
    // Public analysis view (no auth required)
    // Redacted data display (no PII)
    // Professional layout for shared content
    // Error handling for invalid/expired tokens
  }
  ```

### Service Integration
- [ ] **Add export methods to `src/services/analyses.ts`**
  ```typescript
  export async function exportAnalysisPDF(analysisId: string, includeTranscript: boolean = false): Promise<Blob> {
    if (!features.exportEnabled) {
      throw new FeatureNotAvailableError('Export is disabled');
    }
    // API call to export endpoint
  }
  
  export async function createShareLink(analysisId: string, expiresInHours: number = 72): Promise<ShareResponse> {
    if (!features.exportEnabled) {
      throw new FeatureNotAvailableError('Export is disabled');
    }
    // API call to create share token
  }
  ```

### Testing Requirements
- [ ] **Backend tests** (80%+ coverage)
  - Test PDF generation with proper formatting
  - Test share token security (cryptographic randomness)
  - Test token expiration and cleanup
  - Test ownership validation for exports
  - Test public access with redacted data

- [ ] **Frontend tests** (80%+ coverage)
  - Test export button functionality
  - Test share dialog workflow
  - Test feature flag gating
  - Test public share page rendering

### Quality Gates
- [ ] PDF exports are well-formatted and professional
- [ ] Share tokens are cryptographically secure (256-bit entropy)
- [ ] Public share pages never expose PII or transcripts (unless explicitly allowed)
- [ ] Export/share features respect EXPORT_ENABLED flag
- [ ] Token cleanup prevents database bloat (automatic expiration)
- [ ] Security audit passes for token implementation

---

## 🔹 Agent E: Progress & Metrics Dashboard

### Backend Services
- [ ] **Create `backend/services/progress_service.py`**
  ```python
  class ProgressService:
      def __init__(self, analysis_repo: AnalysisRepository):
          self.analysis_repo = analysis_repo
      
      async def calculate_user_metrics(
          self, user_id: UUID, 
          from_date: Optional[datetime] = None,
          to_date: Optional[datetime] = None,
          granularity: str = "week"
      ) -> ProgressMetrics:
          # Aggregate analysis data into metrics
          # Calculate improvement trends
          # Generate time series data
          # Include goal progress if applicable
  
      async def get_progress_goals(self, user_id: UUID) -> List[ProgressGoal]:
          # Retrieve user's progress goals
          # Calculate current progress toward goals
  ```

### API Routes
- [ ] **Create `backend/api/v1/routes/metrics.py`**
  ```python
  @router.get("/analyses/metrics")
  @require_progress_ui  # Feature flag dependency
  async def get_progress_metrics(
      from_date: Optional[datetime] = None,
      to_date: Optional[datetime] = None,
      granularity: str = "week",
      current_user = Depends(get_current_user),
      service: ProgressService = Depends()
  ) -> ProgressMetricsResponse:
      # Return {user_id, date_range, totals, time_series, goals}
  ```

### Frontend Components
- [ ] **Create `src/app/dashboard/progress/page.tsx`**
  ```typescript
  export default function ProgressPage() {
    if (!features.progressUI) {
      return <FeatureNotAvailable feature="Progress Tracking" />;
    }
    
    // Progress dashboard with:
    // - Overview metrics cards
    // - Trend charts (clarity, structure over time)
    // - Goal tracking section
    // - Improvement insights
  }
  ```

- [ ] **Create progress components**
  ```typescript
  // src/components/progress/MetricsOverview.tsx
  interface MetricsOverviewProps {
    metrics: ProgressTotals;
  }
  
  // src/components/progress/TrendChart.tsx
  interface TrendChartProps {
    timeSeries: TimeSeriesData[];
    metric: 'clarity_score' | 'structure_score' | 'word_count';
  }
  
  // src/components/progress/GoalTracker.tsx
  interface GoalTrackerProps {
    goals: ProgressGoal[];
    onUpdateGoal: (goal: ProgressGoal) => void;
  }
  ```

### Data Processing
- [ ] **Create `src/selectors/progress.ts`**
  ```typescript
  export function selectProgressData(analyses: Analysis[]): ProgressData {
    // Transform analysis data for charts
    // Calculate trends and improvements
    // Handle missing metrics gracefully
    // Generate insights and recommendations
  }
  
  export function calculateImprovementTrend(timeSeries: TimeSeriesData[]): number {
    // Linear regression or simple trend calculation
    // Return improvement percentage
  }
  ```

### Service Integration
- [ ] **Add progress methods to `src/services/analyses.ts`**
  ```typescript
  export async function getProgressMetrics(
    fromDate?: string, 
    toDate?: string, 
    granularity?: string
  ): Promise<ProgressMetricsResponse> {
    if (!features.progressUI) {
      throw new FeatureNotAvailableError('Progress UI is disabled');
    }
    // API call to metrics endpoint
  }
  ```

### Navigation Updates
- [ ] **Update dashboard navigation**
  ```typescript
  // src/app/dashboard/layout.tsx
  // Add Progress tab when PROGRESS_UI=1
  const navigation = [
    { name: 'Dashboard', href: '/dashboard' },
    { name: 'Analyses', href: '/dashboard/analyses' },
    ...(features.progressUI ? [{ name: 'Progress', href: '/dashboard/progress' }] : []),
  ];
  ```

### Testing Requirements
- [ ] **Backend tests** (80%+ coverage)
  - Test metrics calculation accuracy
  - Test time series aggregation
  - Test feature flag enforcement
  - Test date range filtering

- [ ] **Frontend tests** (80%+ coverage)
  - Test progress dashboard rendering
  - Test chart components with mock data
  - Test feature flag gating
  - Test goal tracking functionality

### Quality Gates
- [ ] Metrics calculations are accurate and performant
- [ ] Dashboard loads quickly with large datasets (>1000 analyses)
- [ ] Charts are interactive and accessible (WCAG 2.1 AA)
- [ ] Goal tracking motivates user improvement
- [ ] Feature flag (PROGRESS_UI) properly controls access
- [ ] Data selectors handle missing metrics gracefully

---

## Integration Success Criteria

### Cross-Agent Integration
- [ ] Agent A provides stable API foundation for all dependent agents
- [ ] Agent C navigation framework supports B, D, E feature injection
- [ ] Agent B transcription integrates seamlessly with C's detail page
- [ ] Agent D export/share uses complete analysis data from A-C
- [ ] Agent E progress dashboard aggregates data from A-D

### Feature Flag Coordination
- [ ] All agents respect their designated feature flags
- [ ] Backend APIs return 404 when features disabled
- [ ] Frontend gracefully handles disabled features
- [ ] Flag mismatches don't cause application errors

### Quality Assurance
- [ ] All PRs <300 LOC with 80%+ test coverage
- [ ] API contracts match docs/contracts.md exactly
- [ ] Database changes are additive-only
- [ ] PII protection enforced (no transcript/audio logging)
- [ ] Error responses follow consistent format

### Performance Requirements
- [ ] Analysis listing loads in <2s with 1000+ records
- [ ] PDF export completes in <10s for typical analysis
- [ ] Transcription processing completes in <30s for 5-minute audio
- [ ] Progress dashboard renders in <3s with 6 months of data
- [ ] Share links load in <1s for public access