#!/bin/bash

# ============================================================================
# MasterSpeak AI - Universal Deployment Script
# ============================================================================
# Platform-agnostic deployment script supporting multiple providers
# Supports: Railway, Render, Heroku, Fly.io, Docker, Kubernetes
#
# Usage:
#   ./scripts/deploy.sh [platform] [environment] [options]
#
# Examples:
#   ./scripts/deploy.sh railway staging
#   ./scripts/deploy.sh render production
#   ./scripts/deploy.sh docker local
#   ./scripts/deploy.sh --interactive
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/.deploy.config"

# Default values
PLATFORM=""
ENVIRONMENT=""
BRANCH=""
INTERACTIVE=false
DRY_RUN=false
SKIP_TESTS=false
VERBOSE=false

# Platform configurations
declare -A PLATFORM_CONFIGS=(
    ["railway"]="cli:railway,deploy:up,env:environment,logs:logs,url:domain"
    ["render"]="cli:render,deploy:deploy,env:env,logs:logs,url:services"
    ["heroku"]="cli:heroku,deploy:push,env:config,logs:logs,url:info"
    ["fly"]="cli:flyctl,deploy:deploy,env:secrets,logs:logs,url:info"
    ["docker"]="cli:docker,deploy:compose,env:env,logs:logs,url:local"
    ["kubernetes"]="cli:kubectl,deploy:apply,env:configmap,logs:logs,url:ingress"
    ["vercel"]="cli:vercel,deploy:deploy,env:env,logs:logs,url:inspect"
)

# Helper functions
print_header() {
    echo ""
    echo -e "${CYAN}============================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}============================================${NC}"
}

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_step() {
    echo -e "${MAGENTA}▶${NC} $1"
}

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --interactive|-i)
                INTERACTIVE=true
                shift
                ;;
            --dry-run|-d)
                DRY_RUN=true
                shift
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            --platform|-p)
                PLATFORM="$2"
                shift 2
                ;;
            --environment|-e)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --branch|-b)
                BRANCH="$2"
                shift 2
                ;;
            *)
                if [ -z "$PLATFORM" ]; then
                    PLATFORM="$1"
                elif [ -z "$ENVIRONMENT" ]; then
                    ENVIRONMENT="$1"
                fi
                shift
                ;;
        esac
    done
}

# Show help
show_help() {
    cat << EOF
MasterSpeak AI - Universal Deployment Script

Usage: $0 [platform] [environment] [options]

Platforms:
  railway     Railway.app deployment
  render      Render.com deployment
  heroku      Heroku deployment
  fly         Fly.io deployment
  docker      Docker/Docker Compose deployment
  kubernetes  Kubernetes deployment
  vercel      Vercel deployment (frontend)

Environments:
  production  Production environment
  staging     Staging/testing environment
  development Development environment
  local       Local environment

Options:
  -i, --interactive     Interactive mode with prompts
  -d, --dry-run        Show what would be done without doing it
  -v, --verbose        Verbose output
  --skip-tests         Skip running tests before deployment
  -p, --platform       Specify platform
  -e, --environment    Specify environment
  -b, --branch        Specify git branch
  -h, --help          Show this help message

Examples:
  $0 railway staging              Deploy to Railway staging
  $0 render production -d         Dry run for Render production
  $0 --interactive                Interactive deployment wizard
  $0 docker local --skip-tests    Local Docker deployment without tests

EOF
}

# Interactive mode
interactive_mode() {
    print_header "Interactive Deployment Wizard"
    
    # Select platform
    echo "Select deployment platform:"
    echo "1) Railway"
    echo "2) Render"
    echo "3) Heroku"
    echo "4) Fly.io"
    echo "5) Docker"
    echo "6) Kubernetes"
    echo "7) Vercel (Frontend)"
    read -p "Choice (1-7): " platform_choice
    
    case $platform_choice in
        1) PLATFORM="railway" ;;
        2) PLATFORM="render" ;;
        3) PLATFORM="heroku" ;;
        4) PLATFORM="fly" ;;
        5) PLATFORM="docker" ;;
        6) PLATFORM="kubernetes" ;;
        7) PLATFORM="vercel" ;;
        *) print_error "Invalid choice"; exit 1 ;;
    esac
    
    # Select environment
    echo ""
    echo "Select environment:"
    echo "1) Production"
    echo "2) Staging"
    echo "3) Development"
    echo "4) Local"
    read -p "Choice (1-4): " env_choice
    
    case $env_choice in
        1) ENVIRONMENT="production" ;;
        2) ENVIRONMENT="staging" ;;
        3) ENVIRONMENT="development" ;;
        4) ENVIRONMENT="local" ;;
        *) print_error "Invalid choice"; exit 1 ;;
    esac
    
    # Confirm settings
    echo ""
    echo "Deployment settings:"
    echo "  Platform: $PLATFORM"
    echo "  Environment: $ENVIRONMENT"
    echo "  Branch: $(git branch --show-current)"
    echo ""
    read -p "Continue? (y/n): " confirm
    
    if [ "$confirm" != "y" ]; then
        echo "Deployment cancelled"
        exit 0
    fi
}

# Load configuration
load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        print_info "Loading configuration from .deploy.config"
        source "$CONFIG_FILE"
    fi
    
    # Override with environment variables
    PLATFORM="${DEPLOY_PLATFORM:-$PLATFORM}"
    ENVIRONMENT="${DEPLOY_ENVIRONMENT:-$ENVIRONMENT}"
}

# Save configuration
save_config() {
    cat > "$CONFIG_FILE" << EOF
# MasterSpeak AI Deployment Configuration
# Generated: $(date)

DEPLOY_PLATFORM=$PLATFORM
DEPLOY_ENVIRONMENT=$ENVIRONMENT
LAST_DEPLOY=$(date +%s)
EOF
    print_status "Configuration saved to .deploy.config"
}

# Check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check if platform CLI is installed
    local platform_config="${PLATFORM_CONFIGS[$PLATFORM]}"
    local cli_tool=$(echo "$platform_config" | grep -oP 'cli:\K[^,]+')
    
    if ! command -v "$cli_tool" &> /dev/null; then
        print_error "$cli_tool CLI is not installed!"
        echo "Installation instructions:"
        case $PLATFORM in
            railway)
                echo "  npm install -g @railway/cli"
                ;;
            render)
                echo "  brew install render/tap/render (Mac)"
                echo "  Or download from: https://render.com/docs/cli"
                ;;
            heroku)
                echo "  brew tap heroku/brew && brew install heroku (Mac)"
                echo "  Or: curl https://cli-assets.heroku.com/install.sh | sh"
                ;;
            fly)
                echo "  curl -L https://fly.io/install.sh | sh"
                ;;
            vercel)
                echo "  npm install -g vercel"
                ;;
            docker)
                echo "  Install Docker Desktop from https://docker.com"
                ;;
            kubernetes)
                echo "  Install kubectl from https://kubernetes.io/docs/tasks/tools/"
                ;;
        esac
        exit 1
    fi
    
    print_status "Prerequisites checked"
}

# Platform-specific deployment functions

deploy_railway() {
    print_header "Railway Deployment"
    
    # Check if logged in
    if ! railway whoami &> /dev/null; then
        print_warning "Not logged in to Railway"
        railway login
    fi
    
    # Check if project is linked
    if [ ! -f ".railway" ] && [ "$ENVIRONMENT" != "local" ]; then
        print_warning "Project not linked"
        railway link
    fi
    
    # Handle environment
    if [ "$ENVIRONMENT" != "production" ]; then
        print_step "Checking for $ENVIRONMENT environment..."
        if ! railway environment list | grep -q "$ENVIRONMENT"; then
            print_warning "Creating $ENVIRONMENT environment"
            [ "$DRY_RUN" = false ] && railway environment create "$ENVIRONMENT"
        fi
        [ "$DRY_RUN" = false ] && railway environment "$ENVIRONMENT"
    fi
    
    # Deploy
    print_step "Deploying to Railway $ENVIRONMENT..."
    if [ "$DRY_RUN" = false ]; then
        railway up
        sleep 5
        DEPLOY_URL=$(railway domain 2>/dev/null || echo "No domain set")
        print_status "Deployed to: $DEPLOY_URL"
    else
        print_info "Would deploy to Railway $ENVIRONMENT"
    fi
}

deploy_render() {
    print_header "Render Deployment"
    
    # Render uses render.yaml or blueprint spec
    if [ ! -f "render.yaml" ]; then
        print_warning "render.yaml not found. Creating one..."
        create_render_config
    fi
    
    print_step "Deploying to Render $ENVIRONMENT..."
    if [ "$DRY_RUN" = false ]; then
        if [ "$ENVIRONMENT" = "production" ]; then
            render deploy --service masterspeak-backend
        else
            render deploy --service "masterspeak-backend-$ENVIRONMENT"
        fi
    else
        print_info "Would deploy to Render $ENVIRONMENT"
    fi
}

deploy_heroku() {
    print_header "Heroku Deployment"
    
    local app_name="masterspeak-$ENVIRONMENT"
    
    # Check if app exists
    if ! heroku apps:info --app "$app_name" &> /dev/null; then
        print_warning "Creating Heroku app: $app_name"
        [ "$DRY_RUN" = false ] && heroku create "$app_name"
    fi
    
    # Set buildpacks
    print_step "Configuring buildpacks..."
    if [ "$DRY_RUN" = false ]; then
        heroku buildpacks:set heroku/python --app "$app_name"
    fi
    
    # Deploy
    print_step "Deploying to Heroku $ENVIRONMENT..."
    if [ "$DRY_RUN" = false ]; then
        git push heroku "$BRANCH:main" --app "$app_name"
        DEPLOY_URL="https://$app_name.herokuapp.com"
        print_status "Deployed to: $DEPLOY_URL"
    else
        print_info "Would deploy to Heroku $ENVIRONMENT"
    fi
}

deploy_fly() {
    print_header "Fly.io Deployment"
    
    # Check if fly.toml exists
    if [ ! -f "fly.toml" ]; then
        print_warning "fly.toml not found. Creating one..."
        create_fly_config
    fi
    
    local app_name="masterspeak-$ENVIRONMENT"
    
    print_step "Deploying to Fly.io $ENVIRONMENT..."
    if [ "$DRY_RUN" = false ]; then
        flyctl deploy --app "$app_name" --config "fly.$ENVIRONMENT.toml"
        DEPLOY_URL="https://$app_name.fly.dev"
        print_status "Deployed to: $DEPLOY_URL"
    else
        print_info "Would deploy to Fly.io $ENVIRONMENT"
    fi
}

deploy_docker() {
    print_header "Docker Deployment"
    
    local compose_file="docker-compose.yml"
    if [ "$ENVIRONMENT" = "staging" ] || [ "$ENVIRONMENT" = "test" ]; then
        compose_file="docker-compose.e2e.yml"
    fi
    
    print_step "Building Docker images..."
    if [ "$DRY_RUN" = false ]; then
        docker compose -f "$compose_file" build
        
        print_step "Starting services..."
        docker compose -f "$compose_file" up -d
        
        DEPLOY_URL="http://localhost:8000"
        print_status "Services running at: $DEPLOY_URL"
    else
        print_info "Would deploy using $compose_file"
    fi
}

deploy_kubernetes() {
    print_header "Kubernetes Deployment"
    
    # Check if k8s manifests exist
    if [ ! -d "k8s" ]; then
        print_warning "Kubernetes manifests not found. Creating basic setup..."
        create_k8s_manifests
    fi
    
    print_step "Deploying to Kubernetes $ENVIRONMENT..."
    if [ "$DRY_RUN" = false ]; then
        kubectl apply -f "k8s/$ENVIRONMENT/"
        kubectl rollout status deployment/masterspeak-backend -n "$ENVIRONMENT"
        
        DEPLOY_URL=$(kubectl get ingress -n "$ENVIRONMENT" -o jsonpath='{.items[0].spec.rules[0].host}')
        print_status "Deployed to: $DEPLOY_URL"
    else
        print_info "Would deploy to Kubernetes $ENVIRONMENT"
    fi
}

deploy_vercel() {
    print_header "Vercel Deployment"
    
    print_step "Deploying frontend to Vercel..."
    if [ "$DRY_RUN" = false ]; then
        if [ "$ENVIRONMENT" = "production" ]; then
            vercel --prod
        else
            vercel
        fi
    else
        print_info "Would deploy frontend to Vercel $ENVIRONMENT"
    fi
}

# Create configuration files for platforms

create_render_config() {
    cat > render.yaml << 'EOF'
services:
  - type: web
    name: masterspeak-backend
    env: python
    buildCommand: "pip install -r backend/requirements.txt"
    startCommand: "uvicorn backend.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: masterspeak-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: ENV
        value: production

databases:
  - name: masterspeak-db
    databaseName: masterspeak
    user: masterspeak

EOF
    print_status "Created render.yaml"
}

create_fly_config() {
    cat > fly.toml << 'EOF'
app = "masterspeak"
primary_region = "ord"

[build]
  dockerfile = "backend/Dockerfile"

[env]
  PORT = "8080"
  ENV = "production"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true

[[services]]
  http_checks = []
  internal_port = 8080
  protocol = "tcp"
  script_checks = []

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

EOF
    print_status "Created fly.toml"
}

create_k8s_manifests() {
    mkdir -p k8s/production k8s/staging
    
    cat > k8s/base-deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: masterspeak-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: masterspeak-backend
  template:
    metadata:
      labels:
        app: masterspeak-backend
    spec:
      containers:
      - name: backend
        image: masterspeak-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENV
          valueFrom:
            configMapKeyRef:
              name: masterspeak-config
              key: environment
---
apiVersion: v1
kind: Service
metadata:
  name: masterspeak-backend
spec:
  selector:
    app: masterspeak-backend
  ports:
    - port: 80
      targetPort: 8000
  type: LoadBalancer

EOF
    print_status "Created Kubernetes manifests"
}

# Run tests before deployment
run_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        print_warning "Skipping tests"
        return
    fi
    
    print_step "Running tests..."
    
    # Backend tests
    if [ -d "backend" ]; then
        print_info "Running backend tests..."
        if [ "$DRY_RUN" = false ]; then
            cd backend && python -m pytest tests/ -v || {
                print_error "Backend tests failed"
                exit 1
            }
            cd ..
        fi
    fi
    
    # Frontend tests
    if [ -f "package.json" ]; then
        print_info "Running frontend tests..."
        if [ "$DRY_RUN" = false ]; then
            npm test --if-present || {
                print_warning "Frontend tests failed or not configured"
            }
        fi
    fi
    
    print_status "Tests completed"
}

# Post-deployment tasks
post_deploy() {
    print_step "Running post-deployment tasks..."
    
    # Health check
    if [ ! -z "$DEPLOY_URL" ] && [ "$DEPLOY_URL" != "No domain set" ]; then
        print_info "Checking deployment health..."
        sleep 5
        if curl -f -s "$DEPLOY_URL/health" > /dev/null 2>&1; then
            print_status "Health check passed!"
        else
            print_warning "Health check failed. Service may still be starting..."
        fi
    fi
    
    # Save configuration
    save_config
    
    # Show summary
    print_header "Deployment Summary"
    echo "Platform:    $PLATFORM"
    echo "Environment: $ENVIRONMENT"
    echo "Branch:      $(git branch --show-current)"
    if [ ! -z "$DEPLOY_URL" ]; then
        echo "URL:         $DEPLOY_URL"
    fi
    echo ""
    print_status "Deployment completed successfully!"
}

# Main execution
main() {
    print_header "MasterSpeak AI Universal Deployment"
    
    # Parse arguments
    parse_args "$@"
    
    # Load saved configuration
    load_config
    
    # Interactive mode if requested or no args
    if [ "$INTERACTIVE" = true ] || ([ -z "$PLATFORM" ] && [ -z "$ENVIRONMENT" ]); then
        interactive_mode
    fi
    
    # Validate inputs
    if [ -z "$PLATFORM" ]; then
        print_error "Platform not specified. Use --interactive or specify platform"
        show_help
        exit 1
    fi
    
    if [ -z "$ENVIRONMENT" ]; then
        ENVIRONMENT="staging"
        print_warning "Environment not specified. Using default: staging"
    fi
    
    # Set branch if not specified
    if [ -z "$BRANCH" ]; then
        BRANCH=$(git branch --show-current)
    fi
    
    # Show what we're doing
    print_info "Deploying to $PLATFORM ($ENVIRONMENT) from branch $BRANCH"
    
    if [ "$DRY_RUN" = true ]; then
        print_warning "DRY RUN MODE - No actual deployment will occur"
    fi
    
    # Check prerequisites
    check_prerequisites
    
    # Run tests
    run_tests
    
    # Deploy based on platform
    case $PLATFORM in
        railway)
            deploy_railway
            ;;
        render)
            deploy_render
            ;;
        heroku)
            deploy_heroku
            ;;
        fly)
            deploy_fly
            ;;
        docker)
            deploy_docker
            ;;
        kubernetes)
            deploy_kubernetes
            ;;
        vercel)
            deploy_vercel
            ;;
        *)
            print_error "Unknown platform: $PLATFORM"
            exit 1
            ;;
    esac
    
    # Post-deployment tasks
    post_deploy
}

# Run main function
main "$@"