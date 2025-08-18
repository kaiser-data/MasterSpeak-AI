#!/bin/bash

# ============================================================================
# MasterSpeak AI - Railway Staging Environment Setup Script
# ============================================================================
# This script sets up a staging environment on Railway for testing 
# release-candidate branches before merging to production.
#
# Prerequisites:
# - Railway CLI installed (npm install -g @railway/cli)
# - Railway account and project already created
# - Git repository with release-candidate branch
#
# Usage:
#   ./scripts/setup-staging.sh
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 MasterSpeak AI - Railway Staging Environment Setup"
echo "====================================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    print_error "Railway CLI is not installed!"
    echo "Please install it first: npm install -g @railway/cli"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "backend" ]; then
    print_error "Please run this script from the MasterSpeak-AI root directory"
    exit 1
fi

# Step 1: Ensure we're on release-candidate branch
echo ""
echo "Step 1: Checking Git branch..."
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "release-candidate" ]; then
    print_warning "Not on release-candidate branch. Switching..."
    git checkout release-candidate || {
        print_error "Failed to switch to release-candidate branch"
        echo "Please ensure the release-candidate branch exists"
        exit 1
    }
fi
print_status "On release-candidate branch"

# Step 2: Login to Railway (if needed)
echo ""
echo "Step 2: Checking Railway authentication..."
railway whoami &> /dev/null || {
    print_warning "Not logged in to Railway. Logging in..."
    railway login
}
print_status "Authenticated with Railway"

# Step 3: Link to project (if not already linked)
echo ""
echo "Step 3: Linking to Railway project..."
if [ ! -f ".railway" ]; then
    print_warning "Project not linked. Please select your project:"
    railway link
else
    print_status "Project already linked"
fi

# Step 4: Create staging environment
echo ""
echo "Step 4: Creating staging environment..."
railway environment list | grep -q "staging" && {
    print_warning "Staging environment already exists"
    echo "Do you want to use the existing staging environment? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        echo "Exiting..."
        exit 0
    fi
} || {
    railway environment create staging
    print_status "Staging environment created"
}

# Switch to staging environment
railway environment staging
print_status "Switched to staging environment"

# Step 5: Set environment variables
echo ""
echo "Step 5: Setting environment variables..."
echo "Choose an option:"
echo "1) Copy from production (recommended)"
echo "2) Set manually"
echo "3) Skip (already configured)"
read -r env_choice

case $env_choice in
    1)
        print_warning "Please copy environment variables from production in Railway dashboard:"
        echo "1. Go to Railway dashboard"
        echo "2. Select your project"
        echo "3. Switch to 'production' environment"
        echo "4. Go to Variables tab"
        echo "5. Click '...' menu → 'Copy to another environment' → Select 'staging'"
        echo ""
        echo "Press Enter when done..."
        read -r
        ;;
    2)
        echo "Setting staging environment variables..."
        
        # Required variables
        railway variables set ENV="staging"
        railway variables set DEBUG="true"
        railway variables set DATABASE_URL="sqlite:///./staging_data/masterspeak_staging.db"
        
        # Optional: Set other variables
        echo "Enter your OpenAI API key (or press Enter to skip):"
        read -rs OPENAI_KEY
        if [ ! -z "$OPENAI_KEY" ]; then
            railway variables set OPENAI_API_KEY="$OPENAI_KEY"
        fi
        
        echo "Enter staging secret key (or press Enter for default):"
        read -rs SECRET_KEY
        if [ -z "$SECRET_KEY" ]; then
            SECRET_KEY="staging-secret-key-$(date +%s)"
        fi
        railway variables set SECRET_KEY="$SECRET_KEY"
        
        echo "Enter allowed origins (comma-separated, or press Enter for default):"
        read -r ALLOWED_ORIGINS
        if [ -z "$ALLOWED_ORIGINS" ]; then
            ALLOWED_ORIGINS="http://localhost:3000,https://*.vercel.app"
        fi
        railway variables set ALLOWED_ORIGINS="$ALLOWED_ORIGINS"
        
        print_status "Environment variables set"
        ;;
    3)
        print_status "Skipping environment variable configuration"
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

# Step 6: Deploy to staging
echo ""
echo "Step 6: Deploying to staging..."
echo "Do you want to deploy now? (y/n)"
read -r deploy_choice

if [ "$deploy_choice" = "y" ]; then
    print_status "Deploying release-candidate to staging..."
    railway up
    
    # Get the deployment URL
    echo ""
    STAGING_URL=$(railway domain 2>/dev/null || echo "")
    if [ -z "$STAGING_URL" ]; then
        print_warning "No domain set. Generating one..."
        railway domain create
        STAGING_URL=$(railway domain)
    fi
    
    print_status "Staging deployment complete!"
    echo "Staging URL: $STAGING_URL"
else
    print_status "Skipping deployment. Run 'railway up' when ready."
fi

# Step 7: Configure automatic deployments
echo ""
echo "Step 7: Configure automatic deployments"
echo "Please configure in Railway dashboard:"
echo "1. Go to Settings → Deployments"
echo "2. Add Deploy Trigger:"
echo "   - Environment: staging"
echo "   - Branch: release-candidate"
echo "3. Enable 'Check Suites' for PR testing"

# Step 8: Update frontend configuration
echo ""
echo "Step 8: Update Frontend Configuration"
echo "======================================="
if [ ! -z "$STAGING_URL" ]; then
    echo "Add this to Vercel environment variables (Preview environment):"
    echo "NEXT_PUBLIC_API_URL=$STAGING_URL"
    echo ""
    echo "Or create .env.staging locally:"
    echo "NEXT_PUBLIC_API_URL=$STAGING_URL" > .env.staging.example
    print_status "Created .env.staging.example"
fi

# Step 9: Test the setup
echo ""
echo "Step 9: Testing staging environment..."
if [ ! -z "$STAGING_URL" ]; then
    echo "Testing health endpoint..."
    sleep 5  # Give Railway a moment to provision
    
    if curl -f -s "$STAGING_URL/health" > /dev/null 2>&1; then
        print_status "Health check passed! ✨"
        curl -s "$STAGING_URL/health" | python -m json.tool 2>/dev/null || curl -s "$STAGING_URL/health"
    else
        print_warning "Health check failed. The deployment might still be in progress."
        echo "Try again in a few minutes: curl $STAGING_URL/health"
    fi
fi

# Final summary
echo ""
echo "====================================================="
echo "🎉 Staging Environment Setup Complete!"
echo "====================================================="
echo ""
echo "Summary:"
echo "--------"
echo "Environment: staging"
echo "Branch: release-candidate"
if [ ! -z "$STAGING_URL" ]; then
    echo "Backend URL: $STAGING_URL"
fi
echo ""
echo "Next Steps:"
echo "-----------"
echo "1. Update Vercel preview environment variables"
echo "2. Configure automatic deployments in Railway dashboard"
echo "3. Test the complete staging environment:"
echo "   - Backend: curl $STAGING_URL/health"
echo "   - Frontend: Visit your Vercel preview URL"
echo "   - E2E Tests: cd e2e && BACKEND_URL=$STAGING_URL npm test"
echo ""
echo "Useful Commands:"
echo "----------------"
echo "railway environment          # Switch environments"
echo "railway up                   # Deploy current branch"
echo "railway logs                 # View logs"
echo "railway domain              # Get deployment URL"
echo "railway variables           # Manage environment variables"
echo ""
print_status "Setup script completed successfully!"