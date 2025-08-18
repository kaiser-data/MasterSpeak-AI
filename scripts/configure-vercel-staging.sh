#!/bin/bash

# Configure Vercel Environment Variables for Staging
# This script provides instructions for setting up Vercel environment variables

echo "🔧 Vercel Staging Configuration Guide"
echo "======================================"
echo ""

# Railway staging backend URL
RAILWAY_STAGING_URL="https://masterspeak-ai-staging.up.railway.app"

echo "📋 Manual Configuration Steps:"
echo ""
echo "1. Go to Vercel Dashboard: https://vercel.com/dashboard"
echo "2. Select your MasterSpeak-AI project"
echo "3. Go to Project Settings → Environment Variables"
echo "4. Add the following environment variables for PREVIEW environment:"
echo ""
echo "   Variable Name: NEXT_PUBLIC_API_BASE"
echo "   Value: $RAILWAY_STAGING_URL"
echo "   Environment: Preview"
echo ""
echo "   Variable Name: NEXTAUTH_URL"
echo "   Value: https://staging-master-speak-ai.vercel.app"
echo "   Environment: Preview"
echo ""
echo "   Variable Name: NEXTAUTH_SECRET"
echo "   Value: [your-staging-secret-key]"
echo "   Environment: Preview"
echo ""

# Check if Vercel CLI is available
if command -v vercel &> /dev/null; then
    echo "🚀 Automatic Configuration (Vercel CLI available):"
    echo ""
    
    # Set environment variables
    echo "Setting NEXT_PUBLIC_API_BASE for Preview environment..."
    vercel env add NEXT_PUBLIC_API_BASE preview <<< "$RAILWAY_STAGING_URL"
    
    echo "Setting NEXTAUTH_URL for Preview environment..."
    vercel env add NEXTAUTH_URL preview <<< "https://staging-master-speak-ai.vercel.app"
    
    echo "✅ Environment variables configured!"
    echo ""
    echo "🔄 Triggering new deployment to apply changes..."
    vercel --prod=false
    
else
    echo "⚠️  Vercel CLI not found. Please use manual configuration above."
    echo ""
    echo "To install Vercel CLI:"
    echo "npm i -g vercel"
    echo ""
fi

echo "🧪 Testing Configuration:"
echo ""
echo "1. After setting environment variables, trigger a new deployment:"
echo "   - Push to release-candidate branch, or"
echo "   - Redeploy from Vercel dashboard"
echo ""
echo "2. Verify the staging environment:"
echo "   Frontend: https://staging-master-speak-ai.vercel.app"
echo "   Backend:  $RAILWAY_STAGING_URL"
echo ""
echo "3. Test API connectivity:"
echo "   curl -s \"$RAILWAY_STAGING_URL/health\" | jq"
echo ""
echo "4. Test frontend → backend connection:"
echo "   Open browser network tab and check API calls"
echo ""

# Verify Railway staging is healthy
echo "🔍 Verifying Railway staging backend..."
if curl -s "$RAILWAY_STAGING_URL/health" > /dev/null 2>&1; then
    echo "✅ Railway staging backend is responsive"
    echo ""
    echo "Backend Health Status:"
    curl -s "$RAILWAY_STAGING_URL/health" | jq '.' 2>/dev/null || curl -s "$RAILWAY_STAGING_URL/health"
else
    echo "❌ Railway staging backend is not responding"
    echo "Check Railway logs: railway logs --service MasterSpeak-AI --environment staging"
fi

echo ""
echo "📚 Documentation:"
echo "- Vercel Environment Variables: https://vercel.com/docs/concepts/projects/environment-variables"
echo "- Railway Environment: https://docs.railway.app/deploy/environment-variables"
echo ""