#!/bin/bash

# Run E2E tests locally with proper setup
set -e

echo "🚀 Setting up MasterSpeak AI E2E Testing Environment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is required but not installed"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is required but not installed"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_warning "Docker not found - will run services locally"
        USE_DOCKER=false
    else
        USE_DOCKER=true
    fi
}

# Install E2E dependencies
setup_e2e() {
    print_status "Installing E2E test dependencies..."
    
    cd "$(dirname "$0")/.."
    npm install
    
    print_status "Installing Playwright browsers..."
    npx playwright install
    npx playwright install-deps
}

# Start backend service
start_backend() {
    if [ "$USE_DOCKER" = true ]; then
        print_status "Starting backend with Docker..."
        cd ../
        docker-compose -f docker-compose.e2e.yml up -d backend redis
    else
        print_status "Starting backend locally..."
        cd ../backend
        
        # Check if virtual environment exists
        if [ ! -d "venv" ]; then
            python3 -m venv venv
            source venv/bin/activate
            pip install -r ../requirements.txt
        else
            source venv/bin/activate
        fi
        
        # Set test environment variables
        export ENV=testing
        export DATABASE_URL=sqlite:///./test_data/masterspeak_test.db
        export SECRET_KEY=test-secret-key-for-local-e2e-testing
        export RESET_SECRET=test-reset-secret-for-local-e2e-testing  
        export VERIFICATION_SECRET=test-verification-secret-for-local-e2e-testing
        export ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
        export JWT_LIFETIME_SECONDS=3600
        export DEBUG=false
        
        # Start backend
        uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
        BACKEND_PID=$!
        cd ../e2e
    fi
}

# Start frontend service
start_frontend() {
    if [ "$USE_DOCKER" = true ]; then
        print_status "Starting frontend with Docker..."
        docker-compose -f ../docker-compose.e2e.yml up -d frontend
    else
        print_status "Starting frontend locally..."
        cd ../frontend-nextjs
        
        # Install frontend dependencies if needed
        if [ ! -d "node_modules" ]; then
            npm install
        fi
        
        # Set environment variables
        export NEXT_PUBLIC_API_URL=http://localhost:8000
        export NODE_ENV=development
        
        # Start frontend
        npm run dev &
        FRONTEND_PID=$!
        cd ../e2e
    fi
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for backend
    timeout 60 bash -c '
        while ! curl -f http://localhost:8000/health >/dev/null 2>&1; do
            echo "Waiting for backend..."
            sleep 2
        done
    ' || {
        print_error "Backend failed to start"
        cleanup_and_exit 1
    }
    
    # Wait for frontend
    timeout 60 bash -c '
        while ! curl -f http://localhost:3000 >/dev/null 2>&1; do
            echo "Waiting for frontend..."
            sleep 2
        done
    ' || {
        print_error "Frontend failed to start"
        cleanup_and_exit 1
    }
    
    print_status "All services are ready!"
}

# Run the E2E tests
run_tests() {
    print_status "Running E2E tests..."
    
    # Run tests based on arguments
    if [ $# -eq 0 ]; then
        npx playwright test
    else
        npx playwright test "$@"
    fi
    
    TEST_EXIT_CODE=$?
    
    if [ $TEST_EXIT_CODE -eq 0 ]; then
        print_status "All tests passed!"
    else
        print_error "Some tests failed"
    fi
}

# Cleanup function
cleanup_and_exit() {
    print_status "Cleaning up..."
    
    if [ "$USE_DOCKER" = true ]; then
        cd ../
        docker-compose -f docker-compose.e2e.yml down -v
    else
        # Kill local processes
        if [ ! -z "$BACKEND_PID" ]; then
            kill $BACKEND_PID 2>/dev/null || true
        fi
        if [ ! -z "$FRONTEND_PID" ]; then
            kill $FRONTEND_PID 2>/dev/null || true
        fi
    fi
    
    exit ${1:-$TEST_EXIT_CODE}
}

# Trap to ensure cleanup on script exit
trap cleanup_and_exit EXIT

# Main execution
main() {
    check_dependencies
    setup_e2e
    start_backend
    start_frontend
    wait_for_services
    run_tests "$@"
}

# Handle script arguments
case "$1" in
    --headed)
        shift
        main --headed "$@"
        ;;
    --debug)
        shift
        main --debug "$@"
        ;;
    --ui)
        shift
        main --ui "$@"
        ;;
    --help)
        echo "Usage: $0 [OPTIONS] [TEST_FILES]"
        echo ""
        echo "Options:"
        echo "  --headed    Run tests in headed mode"
        echo "  --debug     Run tests in debug mode"
        echo "  --ui        Run tests in UI mode"
        echo "  --help      Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0                          # Run all tests"
        echo "  $0 --headed                # Run all tests in headed mode"
        echo "  $0 auth.spec.ts            # Run specific test file"
        echo "  $0 --debug auth.spec.ts    # Debug specific test file"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac