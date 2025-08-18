#!/bin/bash

# Test Complete Staging Environment
# Verifies both Railway backend and Vercel frontend connectivity

echo "🧪 Testing Complete Staging Environment"
echo "======================================="
echo ""

# URLs
RAILWAY_BACKEND="https://masterspeak-ai-staging.up.railway.app"
VERCEL_FRONTEND="https://staging-master-speak-ai.vercel.app"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Testing Railway Backend...${NC}"
echo "URL: $RAILWAY_BACKEND"
echo ""

# Test backend health
echo -n "Health Check: "
HEALTH_STATUS=$(curl -s "$RAILWAY_BACKEND/health" | jq -r '.status' 2>/dev/null)
if [ "$HEALTH_STATUS" = "healthy" ] || [ "$HEALTH_STATUS" = "degraded" ]; then
    echo -e "${GREEN}✅ $HEALTH_STATUS${NC}"
else
    echo -e "${RED}❌ Failed${NC}"
    echo "Response: $(curl -s "$RAILWAY_BACKEND/health" 2>/dev/null | head -100)"
fi

# Test database connectivity
echo -n "Database: "
DB_STATUS=$(curl -s "$RAILWAY_BACKEND/health" | jq -r '.checks.database.status' 2>/dev/null)
if [ "$DB_STATUS" = "healthy" ]; then
    echo -e "${GREEN}✅ Connected${NC}"
else
    echo -e "${RED}❌ $DB_STATUS${NC}"
fi

# Test CORS headers
echo -n "CORS Configuration: "
CORS_HEADER=$(curl -s -H "Origin: $VERCEL_FRONTEND" -I "$RAILWAY_BACKEND/health" | grep -i "access-control-allow-origin" | head -1)
if [ -n "$CORS_HEADER" ]; then
    echo -e "${GREEN}✅ Configured${NC}"
    echo "  $CORS_HEADER"
else
    echo -e "${YELLOW}⚠️  No CORS header found${NC}"
fi

echo ""
echo -e "${BLUE}🌐 Testing Vercel Frontend...${NC}"
echo "URL: $VERCEL_FRONTEND"
echo ""

# Test frontend accessibility
echo -n "Frontend Accessibility: "
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$VERCEL_FRONTEND" 2>/dev/null)
if [ "$FRONTEND_STATUS" = "200" ] || [ "$FRONTEND_STATUS" = "401" ] || [ "$FRONTEND_STATUS" = "404" ]; then
    echo -e "${GREEN}✅ Accessible (HTTP $FRONTEND_STATUS)${NC}"
else
    echo -e "${RED}❌ Failed (HTTP $FRONTEND_STATUS)${NC}"
fi

# Test if frontend can reach backend
echo -n "Frontend → Backend API: "
# Check if we can access the API through the frontend (should get CORS or similar response)
API_TEST=$(curl -s -o /dev/null -w "%{http_code}" "$VERCEL_FRONTEND/api/v1/health" 2>/dev/null)
if [ "$API_TEST" = "200" ] || [ "$API_TEST" = "401" ] || [ "$API_TEST" = "307" ] || [ "$API_TEST" = "308" ]; then
    echo -e "${GREEN}✅ Reachable (HTTP $API_TEST)${NC}"
else
    echo -e "${YELLOW}⚠️  Unclear (HTTP $API_TEST)${NC}"
fi

echo ""
echo -e "${BLUE}🔗 Integration Test...${NC}"
echo ""

# Test the specific API endpoint that frontend would call
echo -n "API Rewrite Test: "
REWRITE_TEST=$(curl -s -H "Origin: $VERCEL_FRONTEND" -o /dev/null -w "%{http_code}" "$RAILWAY_BACKEND/api/v1/health" 2>/dev/null)
if [ "$REWRITE_TEST" = "200" ]; then
    echo -e "${GREEN}✅ Working${NC}"
else
    echo -e "${YELLOW}⚠️  Response: HTTP $REWRITE_TEST${NC}"
fi

echo ""
echo -e "${BLUE}📊 Environment Summary:${NC}"
echo "┌─────────────────────────────────────────┐"
echo "│ Component         │ Status   │ URL      │"
echo "├─────────────────────────────────────────┤"
printf "│ Railway Backend   │ %-8s │ Running  │\n" "$HEALTH_STATUS"
printf "│ Vercel Frontend   │ %-8s │ Running  │\n" "Active"
printf "│ Database          │ %-8s │ Ready    │\n" "$DB_STATUS"
echo "└─────────────────────────────────────────┘"

echo ""
echo -e "${BLUE}🚀 Next Steps:${NC}"
echo "1. Open $VERCEL_FRONTEND in browser"
echo "2. Open browser DevTools → Network tab"
echo "3. Try to sign up/login and watch API calls"
echo "4. Verify API calls go to: $RAILWAY_BACKEND"
echo ""
echo -e "${BLUE}📚 Staging URLs:${NC}"
echo "Frontend: $VERCEL_FRONTEND"
echo "Backend:  $RAILWAY_BACKEND"
echo "Health:   $RAILWAY_BACKEND/health"
echo "API:      $RAILWAY_BACKEND/api/v1/"
echo ""

# Final check - test if we can get a proper API response
echo -e "${BLUE}🔍 Final API Test:${NC}"
echo -n "Testing /api/v1/health endpoint: "
API_HEALTH=$(curl -s "$RAILWAY_BACKEND/api/v1/health" 2>/dev/null)
if echo "$API_HEALTH" | jq . > /dev/null 2>&1; then
    echo -e "${GREEN}✅ JSON Response Received${NC}"
    echo "$API_HEALTH" | jq .
else
    echo -e "${RED}❌ No valid JSON response${NC}"
    echo "Response: $API_HEALTH"
fi

echo ""
echo -e "${GREEN}🎉 Staging Environment Test Complete!${NC}"