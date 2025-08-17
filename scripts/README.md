# 📜 MasterSpeak AI - Scripts Directory

This directory contains utility scripts for managing the MasterSpeak AI application.

## Available Scripts

### 🚀 `setup-staging.sh`
Sets up a staging environment on Railway for testing release-candidate branches.

**Usage:**
```bash
./scripts/setup-staging.sh
```

**What it does:**
- Creates a staging environment on Railway
- Configures environment variables
- Deploys the release-candidate branch
- Sets up automatic deployments
- Tests the deployment

**Prerequisites:**
- Railway CLI installed (`npm install -g @railway/cli`)
- Railway account and project created
- Git repository with release-candidate branch

### 🧪 `run-local.sh` (E2E Tests)
Runs E2E tests locally (located in `e2e/scripts/`).

**Usage:**
```bash
./e2e/scripts/run-local.sh
```

## Creating New Scripts

When adding new scripts:
1. Make them executable: `chmod +x script-name.sh`
2. Add proper documentation header
3. Include error handling
4. Update this README

## Script Guidelines

- Use `#!/bin/bash` shebang
- Set `set -e` to exit on errors
- Add colored output for better UX
- Include prerequisite checks
- Provide clear error messages
- Add `--help` flag support for complex scripts

## Common Tasks

### Deploy to Staging
```bash
./scripts/setup-staging.sh
```

### Run Tests
```bash
# E2E tests
cd e2e && npm test

# Unit tests
cd backend && pytest
```

### Database Management
```bash
# Reset database
docker compose exec backend python -m backend.seed_db

# Run migrations
docker compose exec backend python -m backend.migrations.run
```

## Environment-Specific Scripts

- **Production**: Handled by CI/CD (no manual scripts)
- **Staging**: Use `setup-staging.sh`
- **Development**: Use Docker Compose commands

## Contributing

When adding new scripts:
1. Follow the existing naming convention
2. Add documentation in the script
3. Update this README
4. Test on multiple platforms (Linux/Mac)
5. Add to `.gitignore` if script contains secrets