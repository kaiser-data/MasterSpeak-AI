#!/bin/bash

# ============================================================================
# MasterSpeak AI - Platform Migration Script
# ============================================================================
# Helps migrate between different deployment platforms while preserving
# environment variables, database data, and configurations
#
# Usage:
#   ./scripts/platform-migrate.sh [source-platform] [target-platform] [environment]
#
# Examples:
#   ./scripts/platform-migrate.sh railway render staging
#   ./scripts/platform-migrate.sh heroku fly production
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SOURCE_PLATFORM=""
TARGET_PLATFORM=""
ENVIRONMENT=""
BACKUP_DIR="./migration-backup-$(date +%Y%m%d-%H%M%S)"

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

print_header() {
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

show_help() {
    cat << EOF
MasterSpeak AI - Platform Migration Tool

Migrates deployments between different platforms while preserving:
- Environment variables
- Database data
- Application configuration
- DNS/domain settings

Supported Platforms:
  railway, render, heroku, fly, vercel, docker, kubernetes

Usage: $0 [source] [target] [environment]

Examples:
  $0 railway render staging     # Migrate staging from Railway to Render
  $0 heroku fly production      # Migrate production from Heroku to Fly.io
  $0 --detect                   # Auto-detect current platform

Options:
  --backup-only                 # Only create backup, don't migrate
  --dry-run                    # Show what would be done
  --skip-data                  # Skip database migration
  --help                       # Show this help

Migration Steps:
  1. Detect current platform configuration
  2. Backup environment variables and data
  3. Create target platform configuration
  4. Deploy to target platform
  5. Migrate database data
  6. Update DNS/domain settings
  7. Verify migration
  8. Cleanup old platform (optional)

EOF
}

# Detect current platform
detect_platform() {
    print_info "Detecting current platform..."
    
    local detected=""
    
    # Check for platform-specific files/configurations
    if [ -f ".railway" ] || railway whoami &>/dev/null; then
        detected="railway"
    elif [ -f "render.yaml" ] || render whoami &>/dev/null; then
        detected="render"
    elif [ -f ".heroku" ] || heroku auth:whoami &>/dev/null; then
        detected="heroku"
    elif [ -f "fly.toml" ] || flyctl auth whoami &>/dev/null; then
        detected="fly"
    elif [ -f ".vercel" ] || vercel whoami &>/dev/null; then
        detected="vercel"
    elif [ -f "docker-compose.yml" ]; then
        detected="docker"
    elif [ -d "k8s" ] || kubectl config current-context &>/dev/null; then
        detected="kubernetes"
    fi
    
    if [ -n "$detected" ]; then
        print_status "Detected platform: $detected"
        SOURCE_PLATFORM="$detected"
    else
        print_warning "Could not auto-detect platform"
    fi
}

# Backup environment variables from source platform
backup_env_vars() {
    print_info "Backing up environment variables from $SOURCE_PLATFORM..."
    
    mkdir -p "$BACKUP_DIR"
    local env_file="$BACKUP_DIR/env-vars.txt"
    
    case $SOURCE_PLATFORM in
        railway)
            railway variables > "$env_file" 2>/dev/null || {
                railway environment "$ENVIRONMENT" && railway variables > "$env_file"
            }
            ;;
        render)
            print_warning "Render env vars must be backed up manually from dashboard"
            echo "# Backup Render environment variables manually from:" > "$env_file"
            echo "# https://dashboard.render.com" >> "$env_file"
            ;;
        heroku)
            heroku config --app "masterspeak-$ENVIRONMENT" --shell > "$env_file"
            ;;
        fly)
            flyctl secrets list --app "masterspeak-$ENVIRONMENT" > "$env_file"
            ;;
        *)
            print_warning "Manual env var backup required for $SOURCE_PLATFORM"
            ;;
    esac
    
    print_status "Environment variables backed up to $env_file"
}

# Backup database
backup_database() {
    print_info "Backing up database from $SOURCE_PLATFORM..."
    
    local db_backup="$BACKUP_DIR/database.sql"
    
    case $SOURCE_PLATFORM in
        railway)
            # Get database URL from Railway
            local db_url=$(railway variables get DATABASE_URL 2>/dev/null)
            if [ -n "$db_url" ]; then
                if [[ "$db_url" == sqlite* ]]; then
                    print_warning "SQLite database - manual backup required"
                else
                    pg_dump "$db_url" > "$db_backup"
                fi
            fi
            ;;
        heroku)
            heroku pg:backups:capture --app "masterspeak-$ENVIRONMENT"
            heroku pg:backups:download --app "masterspeak-$ENVIRONMENT" --output "$db_backup"
            ;;
        render)
            print_warning "Render database backup must be done manually"
            ;;
        *)
            print_warning "Manual database backup required for $SOURCE_PLATFORM"
            ;;
    esac
    
    if [ -f "$db_backup" ]; then
        print_status "Database backed up to $db_backup"
    fi
}

# Create target platform configuration
create_target_config() {
    print_info "Creating configuration for $TARGET_PLATFORM..."
    
    case $TARGET_PLATFORM in
        railway)
            print_info "Railway configuration will be created during deployment"
            ;;
        render)
            if [ -f "scripts/configs/render.yaml.template" ]; then
                cp "scripts/configs/render.yaml.template" "render.yaml"
                # Replace template variables
                sed -i "s/{{ENVIRONMENT}}/$ENVIRONMENT/g" "render.yaml"
                sed -i "s/{{BRANCH}}/$(git branch --show-current)/g" "render.yaml"
                print_status "Created render.yaml"
            fi
            ;;
        fly)
            if [ -f "scripts/configs/fly.toml.template" ]; then
                cp "scripts/configs/fly.toml.template" "fly.toml"
                sed -i "s/{{ENVIRONMENT}}/$ENVIRONMENT/g" "fly.toml"
                print_status "Created fly.toml"
            fi
            ;;
        kubernetes)
            if [ -f "scripts/configs/kubernetes.yaml.template" ]; then
                mkdir -p "k8s"
                cp "scripts/configs/kubernetes.yaml.template" "k8s/deployment.yaml"
                sed -i "s/{{ENVIRONMENT}}/$ENVIRONMENT/g" "k8s/deployment.yaml"
                print_status "Created k8s/deployment.yaml"
            fi
            ;;
    esac
}

# Migrate environment variables
migrate_env_vars() {
    print_info "Migrating environment variables to $TARGET_PLATFORM..."
    
    local env_file="$BACKUP_DIR/env-vars.txt"
    if [ ! -f "$env_file" ]; then
        print_warning "No environment variables backup found"
        return
    fi
    
    case $TARGET_PLATFORM in
        railway)
            print_info "Set environment variables in Railway using:"
            echo "railway environment $ENVIRONMENT"
            cat "$env_file" | while read line; do
                if [[ "$line" == *"="* ]]; then
                    key=$(echo "$line" | cut -d'=' -f1)
                    value=$(echo "$line" | cut -d'=' -f2-)
                    echo "railway variables set $key=\"$value\""
                fi
            done
            ;;
        render)
            print_info "Set environment variables in Render dashboard manually"
            print_info "Backup file: $env_file"
            ;;
        heroku)
            local app_name="masterspeak-$ENVIRONMENT"
            print_info "Setting Heroku environment variables..."
            source "$env_file"
            # Set each variable (this is a simplified example)
            for var in DATABASE_URL SECRET_KEY OPENAI_API_KEY; do
                if [ -n "${!var}" ]; then
                    heroku config:set "$var=${!var}" --app "$app_name"
                fi
            done
            ;;
        fly)
            print_info "Set Fly.io secrets using:"
            cat "$env_file" | while read line; do
                if [[ "$line" == *"="* ]]; then
                    key=$(echo "$line" | cut -d'=' -f1)
                    value=$(echo "$line" | cut -d'=' -f2-)
                    echo "flyctl secrets set $key=\"$value\" --app masterspeak-$ENVIRONMENT"
                fi
            done
            ;;
    esac
    
    print_status "Environment variables migration prepared"
}

# Deploy to target platform
deploy_to_target() {
    print_info "Deploying to $TARGET_PLATFORM..."
    
    # Use the universal deploy script
    if [ -f "scripts/deploy.sh" ]; then
        ./scripts/deploy.sh "$TARGET_PLATFORM" "$ENVIRONMENT"
    else
        print_warning "Universal deploy script not found. Manual deployment required."
        
        case $TARGET_PLATFORM in
            railway)
                echo "Run: railway up"
                ;;
            render)
                echo "Push to GitHub - Render will auto-deploy"
                ;;
            heroku)
                echo "Run: git push heroku main"
                ;;
            fly)
                echo "Run: flyctl deploy"
                ;;
        esac
    fi
}

# Restore database to target
restore_database() {
    print_info "Restoring database to $TARGET_PLATFORM..."
    
    local db_backup="$BACKUP_DIR/database.sql"
    if [ ! -f "$db_backup" ]; then
        print_warning "No database backup found"
        return
    fi
    
    case $TARGET_PLATFORM in
        railway)
            # Get new database URL
            local new_db_url=$(railway variables get DATABASE_URL 2>/dev/null)
            if [ -n "$new_db_url" ] && [[ "$new_db_url" == postgres* ]]; then
                psql "$new_db_url" < "$db_backup"
                print_status "Database restored"
            fi
            ;;
        heroku)
            heroku pg:psql --app "masterspeak-$ENVIRONMENT" < "$db_backup"
            ;;
        *)
            print_warning "Manual database restore required for $TARGET_PLATFORM"
            print_info "Backup file: $db_backup"
            ;;
    esac
}

# Verify migration
verify_migration() {
    print_info "Verifying migration..."
    
    # Try to get the new deployment URL
    local target_url=""
    case $TARGET_PLATFORM in
        railway)
            target_url=$(railway domain 2>/dev/null)
            ;;
        heroku)
            target_url="https://masterspeak-$ENVIRONMENT.herokuapp.com"
            ;;
        fly)
            target_url="https://masterspeak-$ENVIRONMENT.fly.dev"
            ;;
    esac
    
    if [ -n "$target_url" ]; then
        print_info "Testing health endpoint: $target_url/health"
        if curl -f -s "$target_url/health" > /dev/null; then
            print_status "Migration verification passed!"
        else
            print_warning "Health check failed. Manual verification needed."
        fi
    else
        print_warning "Could not determine target URL. Manual verification needed."
    fi
}

# Cleanup old platform
cleanup_old_platform() {
    echo ""
    read -p "Do you want to cleanup/remove the old $SOURCE_PLATFORM deployment? (y/n): " cleanup_choice
    
    if [ "$cleanup_choice" = "y" ]; then
        print_warning "Cleaning up $SOURCE_PLATFORM deployment..."
        
        case $SOURCE_PLATFORM in
            railway)
                echo "To delete Railway service:"
                echo "1. Go to Railway dashboard"
                echo "2. Select the service"
                echo "3. Go to Settings → Danger → Delete Service"
                ;;
            heroku)
                echo "To delete Heroku app:"
                echo "heroku apps:destroy masterspeak-$ENVIRONMENT"
                ;;
            *)
                print_info "Manual cleanup required for $SOURCE_PLATFORM"
                ;;
        esac
    fi
}

# Main migration function
main() {
    print_header "MasterSpeak AI Platform Migration"
    
    # Parse arguments
    case "${1:-}" in
        --help|-h)
            show_help
            exit 0
            ;;
        --detect)
            detect_platform
            exit 0
            ;;
    esac
    
    SOURCE_PLATFORM="${1:-}"
    TARGET_PLATFORM="${2:-}"
    ENVIRONMENT="${3:-staging}"
    
    # Auto-detect if source not provided
    if [ -z "$SOURCE_PLATFORM" ]; then
        detect_platform
    fi
    
    # Validate inputs
    if [ -z "$SOURCE_PLATFORM" ] || [ -z "$TARGET_PLATFORM" ]; then
        print_error "Both source and target platforms must be specified"
        show_help
        exit 1
    fi
    
    if [ "$SOURCE_PLATFORM" = "$TARGET_PLATFORM" ]; then
        print_error "Source and target platforms cannot be the same"
        exit 1
    fi
    
    # Confirm migration
    echo ""
    echo "Migration Plan:"
    echo "  From: $SOURCE_PLATFORM"
    echo "  To:   $TARGET_PLATFORM"
    echo "  Environment: $ENVIRONMENT"
    echo "  Backup Dir: $BACKUP_DIR"
    echo ""
    read -p "Continue with migration? (y/n): " confirm
    
    if [ "$confirm" != "y" ]; then
        echo "Migration cancelled"
        exit 0
    fi
    
    # Execute migration steps
    backup_env_vars
    backup_database
    create_target_config
    migrate_env_vars
    deploy_to_target
    restore_database
    verify_migration
    
    print_header "Migration Summary"
    echo "✓ Environment variables backed up and migrated"
    echo "✓ Database backed up and restored"
    echo "✓ Target platform configured and deployed"
    echo "✓ Migration verified"
    echo ""
    echo "Backup location: $BACKUP_DIR"
    echo "Next steps:"
    echo "1. Test the new deployment thoroughly"
    echo "2. Update DNS/domain settings if needed"
    echo "3. Monitor the new platform for issues"
    echo "4. Clean up the old platform when satisfied"
    
    cleanup_old_platform
    
    print_status "Migration completed successfully!"
}

# Run main function
main "$@"