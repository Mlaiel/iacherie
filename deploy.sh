#!/bin/bash
# =============================================================================
# AINFLUE PLATFORM - AUTOMATED DEPLOYMENT SCRIPT
# =============================================================================
# Enterprise-grade deployment automation for the Ainflue platform with
# health checks, rollback capabilities, and monitoring integration.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/var/log/ainflue/deploy.log"
LOCK_FILE="/tmp/ainflue-deploy.lock"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${ENVIRONMENT:-production}"
USER_TYPE="${USER_TYPE:-}"
SERVICES="${SERVICES:-all}"
BACKUP_BEFORE_DEPLOY="${BACKUP_BEFORE_DEPLOY:-true}"
HEALTH_CHECK_TIMEOUT="${HEALTH_CHECK_TIMEOUT:-300}"
ROLLBACK_ON_FAILURE="${ROLLBACK_ON_FAILURE:-true}"

# Function to log messages
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

# Function to log info messages
info() {
    log "INFO" "${BLUE}$1${NC}"
}

# Function to log warning messages
warn() {
    log "WARN" "${YELLOW}$1${NC}"
}

# Function to log error messages
error() {
    log "ERROR" "${RED}$1${NC}"
}

# Function to log success messages
success() {
    log "SUCCESS" "${GREEN}$1${NC}"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons."
        exit 1
    fi
}

# Function to create lock file
create_lock() {
    if [[ -f "$LOCK_FILE" ]]; then
        error "Another deployment is already in progress (lock file exists: $LOCK_FILE)"
        exit 1
    fi
    echo $$ > "$LOCK_FILE"
    trap 'rm -f "$LOCK_FILE"' EXIT
}

# Function to validate environment
validate_environment() {
    info "Validating deployment environment..."
    
    # Check required tools
    local required_tools=("docker" "docker-compose" "curl" "jq")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            error "Required tool not found: $tool"
            exit 1
        fi
    done
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        exit 1
    fi
    
    # Check available disk space (minimum 10GB)
    local available_space=$(df / | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 10485760 ]]; then
        error "Insufficient disk space. At least 10GB required."
        exit 1
    fi
    
    success "Environment validation completed"
}

# Function to backup current deployment
backup_deployment() {
    if [[ "$BACKUP_BEFORE_DEPLOY" == "true" ]]; then
        info "Creating backup before deployment..."
        local backup_dir="/var/backups/ainflue/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$backup_dir"
        
        # Backup volumes
        docker run --rm -v ainflue_postgres_data:/data -v "$backup_dir":/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .
        docker run --rm -v ainflue_redis_data:/data -v "$backup_dir":/backup alpine tar czf /backup/redis_data.tar.gz -C /data .
        
        # Backup configuration
        cp -r "$PROJECT_DIR/config" "$backup_dir/"
        
        success "Backup created at: $backup_dir"
        echo "$backup_dir" > /tmp/ainflue-last-backup
    fi
}

# Function to deploy specific user type
deploy_user_type() {
    local user_type="$1"
    info "Deploying services for user type: $user_type"
    
    local compose_file="docker-compose.${user_type}.yml"
    if [[ ! -f "$PROJECT_DIR/$compose_file" ]]; then
        error "Compose file not found: $compose_file"
        return 1
    fi
    
    # Pull latest images
    docker-compose -f "$compose_file" pull
    
    # Deploy services
    docker-compose -f "$compose_file" up -d --remove-orphans
    
    # Wait for services to be healthy
    wait_for_health "$compose_file"
}

# Function to deploy all services
deploy_all_services() {
    info "Deploying all Ainflue services..."
    
    # Deploy core infrastructure first
    info "Deploying core infrastructure..."
    docker-compose -f docker/infrastructure/docker-compose.production.yml up -d
    
    # Deploy service categories
    local service_categories=("audio" "protection" "monetization")
    for category in "${service_categories[@]}"; do
        info "Deploying $category services..."
        docker-compose -f "docker/$category/docker-compose.$category.yml" up -d
    done
    
    # Deploy user-specific services if specified
    if [[ -n "$USER_TYPE" ]]; then
        deploy_user_type "$USER_TYPE"
    fi
}

# Function to wait for service health
wait_for_health() {
    local compose_file="$1"
    info "Waiting for services to become healthy..."
    
    local timeout=$HEALTH_CHECK_TIMEOUT
    local interval=10
    local elapsed=0
    
    while [[ $elapsed -lt $timeout ]]; do
        local unhealthy_services=$(docker-compose -f "$compose_file" ps --services --filter "health=unhealthy" | wc -l)
        
        if [[ $unhealthy_services -eq 0 ]]; then
            success "All services are healthy"
            return 0
        fi
        
        info "Waiting for $unhealthy_services services to become healthy... (${elapsed}/${timeout}s)"
        sleep $interval
        elapsed=$((elapsed + interval))
    done
    
    error "Health check timeout reached. Some services may not be healthy."
    return 1
}

# Function to rollback deployment
rollback_deployment() {
    warn "Rolling back deployment..."
    
    if [[ -f /tmp/ainflue-last-backup ]]; then
        local backup_dir=$(cat /tmp/ainflue-last-backup)
        info "Restoring from backup: $backup_dir"
        
        # Stop services
        docker-compose down
        
        # Restore volumes
        docker run --rm -v ainflue_postgres_data:/data -v "$backup_dir":/backup alpine tar xzf /backup/postgres_data.tar.gz -C /data
        docker run --rm -v ainflue_redis_data:/data -v "$backup_dir":/backup alpine tar xzf /backup/redis_data.tar.gz -C /data
        
        # Restart services
        docker-compose up -d
        
        success "Rollback completed"
    else
        error "No backup found for rollback"
    fi
}

# Function to run post-deployment tests
run_post_deployment_tests() {
    info "Running post-deployment tests..."
    
    # Basic connectivity tests
    local test_endpoints=(
        "http://localhost:8000/health"
        "http://localhost:8010/health"  # Audio processing
        "http://localhost:8020/health"  # Protection
        "http://localhost:8040/health"  # Revenue tracker
    )
    
    for endpoint in "${test_endpoints[@]}"; do
        if curl -f -s "$endpoint" > /dev/null; then
            success "✓ $endpoint is healthy"
        else
            error "✗ $endpoint is not responding"
            return 1
        fi
    done
    
    success "All post-deployment tests passed"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Deploy the Ainflue platform with comprehensive service orchestration.

OPTIONS:
    -e, --environment ENV     Deployment environment (production|staging|development)
    -u, --user-type TYPE      Deploy services for specific user type (musician|photographer|blogger|influencer|comedian)
    -s, --services SERVICES   Deploy specific services (all|audio|protection|monetization)
    -b, --backup BOOL         Create backup before deployment (true|false)
    -t, --timeout SECONDS     Health check timeout in seconds
    -r, --rollback BOOL       Enable rollback on failure (true|false)
    -h, --help               Show this help message

EXAMPLES:
    $0                                    # Deploy all services in production
    $0 -u musician                        # Deploy musician-specific services
    $0 -e staging -s audio                # Deploy audio services in staging
    $0 -u photographer --backup false     # Deploy for photographers without backup

ENVIRONMENT VARIABLES:
    ENVIRONMENT              Deployment environment
    USER_TYPE               Target user type
    SERVICES                Services to deploy
    BACKUP_BEFORE_DEPLOY    Create backup before deployment
    HEALTH_CHECK_TIMEOUT    Health check timeout
    ROLLBACK_ON_FAILURE     Enable rollback on failure

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -u|--user-type)
            USER_TYPE="$2"
            shift 2
            ;;
        -s|--services)
            SERVICES="$2"
            shift 2
            ;;
        -b|--backup)
            BACKUP_BEFORE_DEPLOY="$2"
            shift 2
            ;;
        -t|--timeout)
            HEALTH_CHECK_TIMEOUT="$2"
            shift 2
            ;;
        -r|--rollback)
            ROLLBACK_ON_FAILURE="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    info "Starting Ainflue platform deployment..."
    info "Environment: $ENVIRONMENT"
    info "User Type: ${USER_TYPE:-all}"
    info "Services: $SERVICES"
    
    check_root
    create_lock
    validate_environment
    backup_deployment
    
    # Change to project directory
    cd "$PROJECT_DIR"
    
    # Deploy based on configuration
    if [[ -n "$USER_TYPE" ]]; then
        deploy_user_type "$USER_TYPE"
    elif [[ "$SERVICES" == "all" ]]; then
        deploy_all_services
    else
        info "Deploying specific services: $SERVICES"
        docker-compose -f "docker/$SERVICES/docker-compose.$SERVICES.yml" up -d
    fi
    
    # Run health checks and tests
    if run_post_deployment_tests; then
        success "🎉 Deployment completed successfully!"
    else
        error "Deployment validation failed"
        if [[ "$ROLLBACK_ON_FAILURE" == "true" ]]; then
            rollback_deployment
        fi
        exit 1
    fi
    
    # Cleanup
    docker system prune -f --volumes=false
    
    success "Ainflue platform deployment completed successfully!"
}

# Execute main function
main "$@"