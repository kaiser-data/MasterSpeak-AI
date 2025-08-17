# Agent Assignments & Handoff Contracts

## Agent Ownership & Responsibilities

### 🔹 Agent A: Analysis Persistence Foundation
**Owner**: Backend Specialist  
**Priority**: 1 (Critical Path)  
**Timeline**: Week 1 (5 days)  
**PR Size**: <300 LOC total across all deliverables

#### Core Responsibilities
- Implement idempotent analysis persistence with unique(user_id, speech_id)
- Create analysis CRUD operations with proper error handling
- Establish database schema for analysis storage
- Provide stable API contracts for dependent agents

#### Deliverables Checklist
- [ ] `backend/models/analysis.py` - SQLModel with unique constraint
- [ ] `backend/repositories/analysis_repo.py` - Idempotent data access methods
- [ ] `backend/services/analysis_service.py` - Business logic orchestration
- [ ] `backend/api/v1/routes/analyses.py` - REST endpoints implementation
- [ ] Database migration script for Analysis table
- [ ] Unit tests achieving 80%+ coverage
- [ ] Integration tests for API endpoints

#### Handoff Contracts

**To Agent C (History/Nav):**
```json
// POST /api/v1/analysis/complete - Idempotent analysis creation
Request: {user_id, speech_id, transcript?, metrics?, summary?, feedback}
Response: {analysis_id, is_duplicate: boolean, created_at}

// GET /api/v1/analyses - Paginated analysis listing  
Query: {limit?, page?, user_id}
Response: {items: Analysis[], total, page, page_size, total_pages}
```

**Quality Gates:**
- [ ] All tests green with 80%+ coverage
- [ ] API contracts match docs/contracts.md exactly
- [ ] Idempotency verified: duplicate calls return same analysis_id
- [ ] Error handling covers all documented error codes
- [ ] Database migration is additive-only

#### Success Criteria
- Analysis persistence working end-to-end
- Unique constraint prevents duplicate analyses
- API endpoints return consistent response format
- Agent C can build on stable analysis foundation

---

### 🔹 Agent C: History & Navigation Framework
**Owner**: Frontend Specialist  
**Priority**: 2 (Navigation Foundation)  
**Timeline**: Week 2 (5 days)  
**Dependencies**: Agent A complete

#### Core Responsibilities
- Build paginated analysis listing page
- Create analysis detail page framework
- Implement frontend analysis service layer
- Establish navigation patterns for dependent agents

#### Deliverables Checklist
- [ ] `src/app/dashboard/analyses/page.tsx` - Server component with pagination
- [ ] `src/app/dashboard/analyses/[id]/page.tsx` - Analysis detail framework
- [ ] `src/services/analyses.ts` - Frontend service using Agent A APIs
- [ ] Dashboard navigation updates with "View All" links
- [ ] Loading states, error boundaries, empty states
- [ ] Responsive design for mobile/tablet

#### Handoff Contracts

**From Agent A (Analysis Persistence):**
```typescript
// Frontend service methods
getAnalyses(page: number, limit: number): Promise<PaginatedAnalyses>
getAnalysisById(id: string): Promise<Analysis>
createAnalysis(data: CreateAnalysisRequest): Promise<Analysis>
```

**To Agent B (Transcription UI):**
```typescript
// Analysis detail page framework ready for transcript injection
// Components: AnalysisHeader, AnalysisMetrics, AnalysisContent (extensible)
// Props: {analysis: Analysis, children?: ReactNode}
```

**Quality Gates:**
- [ ] All pages load without errors and show appropriate states
- [ ] Pagination works correctly with backend API
- [ ] Analysis detail page displays all analysis data
- [ ] Navigation is intuitive and accessible
- [ ] Component architecture supports extension by Agent B

#### Success Criteria
- Users can view paginated list of analyses
- Analysis detail pages load and display data correctly
- Navigation framework ready for transcript/export features
- Agent B can inject transcription UI into detail page

---

### 🔹 Agent B: Transcription UI & Audio Processing
**Owner**: Full-Stack Specialist  
**Priority**: 3 (Feature Enhancement)  
**Timeline**: Week 3 (5 days)  
**Dependencies**: Agent C complete  
**Feature Flag**: TRANSCRIPTION_UI=1

#### Core Responsibilities
- Implement audio transcription service (Whisper API)
- Build file upload UI with progress tracking
- Integrate transcript display in analysis detail page
- Handle transcription errors and retry logic

#### Deliverables Checklist
- [ ] `backend/api/v1/routes/transcription.py` - Transcription endpoints
- [ ] `backend/services/transcription_service.py` - Whisper integration
- [ ] `src/components/ui/TranscriptionUpload.tsx` - File upload component
- [ ] Transcript section in analysis detail page (flag-gated)
- [ ] Audio file validation and progress indicators
- [ ] Feature flag integration with environment config

#### Handoff Contracts

**From Agent C (Navigation):**
```typescript
// Analysis detail page framework available for extension
<AnalysisDetailPage analysis={analysis}>
  {TRANSCRIPTION_UI && <TranscriptionSection />}
</AnalysisDetailPage>
```

**To Agent D (Export/Share):**
```json
// POST /api/v1/transcription/transcribe - Audio to text conversion
Request: FormData {file: File, language?: string, model?: string}
Response: {transcript, language, duration_seconds, word_count, confidence_score}

// Enhanced analysis detail page with transcript data for export
Analysis: {transcript?: string, enhanced_content: true}
```

**Quality Gates:**
- [ ] Transcription service handles multiple audio formats (mp3, wav, m4a)
- [ ] File upload shows progress and handles errors gracefully
- [ ] Transcript display is properly formatted and copyable
- [ ] Feature flag correctly shows/hides transcription features
- [ ] Audio files >10MB rejected with clear error message

#### Success Criteria
- Users can upload audio files and get transcriptions
- Transcription UI integrates seamlessly with analysis detail page
- Feature flag controls transcription availability
- Agent D can export analyses with transcript data

---

### 🔹 Agent D: Export & Share Functionality
**Owner**: Security-Focused Developer  
**Priority**: 4 (Value-Add Features)  
**Timeline**: Week 4 (5 days)  
**Dependencies**: Agent B complete  
**Feature Flag**: EXPORT_ENABLED=1

#### Core Responsibilities
- Implement PDF export with professional formatting
- Create shareable link system with secure tokens
- Build export/share UI in analysis detail page
- Ensure security for public share links (no PII exposure)

#### Deliverables Checklist
- [ ] `backend/models/share_token.py` - Secure token entity
- [ ] `backend/services/export_service.py` - PDF generation service
- [ ] `backend/api/v1/routes/export.py` - Export endpoints
- [ ] `backend/api/v1/routes/share.py` - Share token management
- [ ] Export/Share buttons in analysis detail page (flag-gated)
- [ ] Public share page with redacted data
- [ ] Token expiration and cleanup job

#### Handoff Contracts

**From Agent B (Transcription):**
```typescript
// Enhanced analysis detail page ready for export integration
<AnalysisDetailPage analysis={analysis}>
  {EXPORT_ENABLED && <ExportShareSection />}
</AnalysisDetailPage>
```

**To Agent E (Progress):**
```json
// Complete analysis data structure for metrics
Analysis: {
  metrics: {word_count, clarity_score, structure_score, filler_word_count},
  created_at: string,
  updated_at: string,
  // All data needed for progress calculations
}

// Export tracking for usage metrics
Export: {analysis_id, export_type: "pdf", created_at}
Share: {analysis_id, token, expires_at, created_at}
```

**Quality Gates:**
- [ ] PDF exports are well-formatted and professional
- [ ] Share tokens are cryptographically secure and time-limited
- [ ] Public share pages never expose PII or transcripts (unless flag set)
- [ ] Export/share features respect feature flags
- [ ] Token cleanup prevents database bloat

#### Success Criteria
- Users can export analyses as professional PDFs
- Shareable links work for public access with appropriate data redaction
- Security audit passes for share token implementation
- Agent E has complete analysis data for progress tracking

---

### 🔹 Agent E: Progress & Metrics Dashboard
**Owner**: Data Visualization Specialist  
**Priority**: 5 (Analytics & Insights)  
**Timeline**: Week 5 (5 days)  
**Dependencies**: Agent D complete  
**Feature Flag**: PROGRESS_UI=1

#### Core Responsibilities
- Build progress metrics aggregation service
- Create interactive progress dashboard
- Implement goal tracking and trends
- Provide actionable insights from analysis history

#### Deliverables Checklist
- [ ] `backend/api/v1/routes/metrics.py` - Metrics aggregation endpoints
- [ ] `backend/services/progress_service.py` - Progress calculations
- [ ] `src/app/dashboard/progress/page.tsx` - Progress dashboard
- [ ] `src/selectors/progress.ts` - Data transformation utilities
- [ ] Chart components for trends and metrics
- [ ] Goal setting and tracking interface

#### Handoff Contracts

**From Agent D (Export/Share):**
```json
// Complete analysis data for metrics calculation
GET /api/v1/analyses → {
  items: [{metrics, created_at, updated_at, user_id}],
  // Rich data for trend analysis and goal tracking
}

// Usage data for comprehensive metrics
Exports: [{analysis_id, export_type, created_at}]
Shares: [{analysis_id, created_at, expires_at}]
```

**Final Integration:**
```json
// GET /api/v1/analyses/metrics - Comprehensive progress data
Response: {
  user_id, date_range, totals, time_series, goals,
  // Complete progress tracking with historical insights
}
```

**Quality Gates:**
- [ ] Metrics calculations are accurate and performant
- [ ] Dashboard loads quickly with large datasets
- [ ] Charts are interactive and accessible
- [ ] Goal tracking motivates user improvement
- [ ] Feature flag properly controls progress features

#### Success Criteria
- Users see meaningful progress insights and trends
- Goal tracking encourages continued platform usage
- Dashboard provides actionable feedback for improvement
- Complete sprint integration delivers all 5 goals

---

## Integration Checkpoints

### Daily Standups
- **Blocker identification**: Any agent blocked by dependencies
- **API contract changes**: Require Orchestrator approval
- **Feature flag coordination**: Ensure consistent flag behavior
- **Quality gate status**: Track progress on test coverage and requirements

### Weekly Reviews
- **Week 1**: Agent A foundation solid, Agent C can proceed
- **Week 2**: Navigation framework ready, Agent B can begin
- **Week 3**: Transcription working, Agent D has requirements
- **Week 4**: Export/share complete, Agent E has full data
- **Week 5**: Final integration testing and deployment

### Handoff Ceremonies
Each agent must demonstrate:
1. All deliverables complete and tested
2. API contracts working as documented
3. Dependent agent can proceed without blockers
4. Documentation updated and accurate
5. Feature flags properly implemented

### Emergency Procedures
- **Breaking change detected**: Immediate Orchestrator review
- **Agent blocked**: Escalate dependency resolution
- **Quality gate failure**: Fix before proceeding to next agent
- **Timeline slip**: Adjust scope or get stakeholder approval