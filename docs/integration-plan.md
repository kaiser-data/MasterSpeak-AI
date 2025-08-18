# Integration Plan

5-goal sprint integration plan for MasterSpeak-AI with dependency order A→C→B→D→E.

## 1. Merge Order & Calendar

**Dependency Chain**: A→C→B→D→E

### Week 1: Foundation (Agent A)
- **Day 1-2**: Analysis persistence models & database migration
- **Day 3-4**: Repository & service layer implementation
- **Day 5**: API routes `/analysis/complete` and `/analyses`
- **Merge A**: Foundation complete, enables all dependent agents

### Week 2: Navigation (Agent C)
- **Day 1-2**: Enhanced analyses service & TypeScript types
- **Day 3-4**: Analysis list page updates & detail page creation
- **Day 5**: Navigation integration & component architecture
- **Merge C**: History framework complete, enables B/D/E injection

### Week 3: Features (Agents B, D, E in parallel)
- **Days 1-3**: Agent B (Transcription UI), Agent D (Export/Share), Agent E (Progress)
- **Days 4-5**: Integration testing & feature flag validation
- **Merge B**: Day 4, **Merge D**: Day 5, **Merge E**: Day 5

## 2. PR Rules

### Size & Quality
- **≤300 LOC** per PR (strictly enforced)
- **≥80% test coverage** required
- **API contracts**: No changes without orchestrator approval

### Review Requirements
- All PRs require orchestrator review for contract compliance
- Database migrations must be additive-only
- Feature flags must gate all new functionality
- PII protection validation required (no transcript logging)

### Branch Strategy
- **main**: Production-ready code
- **feature/agent-{A|B|C|D|E}**: Agent-specific development
- **hotfix/**: Emergency fixes only

## 3. CI Gates

### Frontend Gates
```bash
npm run lint        # ESLint + Prettier
npm run typecheck   # TypeScript compilation
npm run test:changed # Jest tests for changed files
```

### Backend Gates
```bash
pytest --cov=backend --cov-report=term-missing
black --check backend/
isort --check-only backend/
mypy backend/
alembic check  # Migration validation
alembic upgrade --sql head > /dev/null  # Dry-run migrations
```

### Contract Validation
- API response schemas match `docs/contracts.md`
- Feature flag enforcement verified
- Database changes are additive-only

## 4. Handoff Checklists

### After Agent A Merge
- [ ] Analysis persistence API endpoints operational
- [ ] Database migrations applied successfully
- [ ] Idempotency validated (duplicate analysis prevention)
- [ ] API contracts published and tested
- [ ] Agent C can begin navigation development

### After Agent C Merge
- [ ] Analysis listing and detail pages functional
- [ ] Navigation framework supports feature injection
- [ ] TypeScript types published for dependent agents
- [ ] Component architecture documented
- [ ] Agents B, D, E can begin parallel development

### After Agents B, D, E Merge
- [ ] Feature flags correctly gate all new functionality
- [ ] Cross-agent integration tested
- [ ] Performance benchmarks met
- [ ] Security audit completed
- [ ] Production deployment ready

## 5. Rollback/Flag Strategy

### Production Safety
- **Production flags**: All OFF by default (`TRANSCRIPTION_UI=0`, `EXPORT_ENABLED=0`, `PROGRESS_UI=0`)
- **Preview environment**: All ON for testing (`TRANSCRIPTION_UI=1`, `EXPORT_ENABLED=1`, `PROGRESS_UI=1`)

### Rollback Procedures
1. **Flag Rollback**: Disable feature flags immediately via environment variables
2. **Code Rollback**: Revert to previous stable commit if flags insufficient
3. **Database Rollback**: Additive-only migrations prevent data loss

### Flag Management
```bash
# Emergency disable (production)
export TRANSCRIPTION_UI=0
export EXPORT_ENABLED=0  
export PROGRESS_UI=0

# Gradual enable (staging → production)
export TRANSCRIPTION_UI=1  # Enable transcription first
# Monitor, then enable others
```

### Monitoring
- Feature flag usage tracked via structured logging
- Performance metrics monitored per feature
- Error rates tracked by feature flag state
- Automatic rollback triggers on >5% error rate increase

---

**Success Metrics**: All 5 goals delivered on schedule with <300 LOC PRs, 80%+ coverage, and seamless flag-based rollout capability.