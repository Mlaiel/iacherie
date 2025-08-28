#!/bin/bash
# Ainflue Platform Production Database Deployment Script
# Author: Fahed Mlaiel (mlaiel@live.de)
# 
# This script deploys the complete PostgreSQL master/slave setup with monitoring,
# backup automation, and performance optimization for the Ainflue platform.

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/tmp/ainflue-db-deployment-$(date +%Y%m%d-%H%M%S).log"

# Default values
ENVIRONMENT="production"
SKIP_BACKUP="false"
SKIP_MONITORING="false"
FORCE_RECREATE="false"

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        INFO)  echo -e "${GREEN}[INFO]${NC} $message" | tee -a "$LOG_FILE" ;;
        WARN)  echo -e "${YELLOW}[WARN]${NC} $message" | tee -a "$LOG_FILE" ;;
        ERROR) echo -e "${RED}[ERROR]${NC} $message" | tee -a "$LOG_FILE" ;;
        DEBUG) echo -e "${BLUE}[DEBUG]${NC} $message" | tee -a "$LOG_FILE" ;;
    esac
}

# Error handling
error_exit() {
    log ERROR "$1"
    log ERROR "Deployment failed. Check log file: $LOG_FILE"
    exit 1
}

# Help function
show_help() {
    cat << EOF
Ainflue Platform Database Deployment Script

Usage: $0 [OPTIONS]

OPTIONS:
    -e, --environment ENV    Environment to deploy to (default: production)
    -s, --skip-backup        Skip backup setup
    -m, --skip-monitoring    Skip monitoring setup
    -f, --force-recreate     Force recreate all containers
    -h, --help              Show this help message

EXAMPLES:
    $0                           # Deploy with default settings
    $0 -e staging               # Deploy to staging environment
    $0 --skip-backup            # Deploy without backup setup
    $0 --force-recreate         # Force recreate all containers

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -s|--skip-backup)
                SKIP_BACKUP="true"
                shift
                ;;
            -m|--skip-monitoring)
                SKIP_MONITORING="true"
                shift
                ;;
            -f|--force-recreate)
                FORCE_RECREATE="true"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                error_exit "Unknown option: $1"
                ;;
        esac
    done
}

# Check prerequisites
check_prerequisites() {
    log INFO "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        error_exit "Docker is not installed. Please install Docker first."
    fi
    
    if ! docker info &> /dev/null; then
        error_exit "Docker daemon is not running. Please start Docker first."
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error_exit "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check if required files exist
    local required_files=(
        "docker-compose.production.yml"
        "database/postgresql/master.conf"
        "database/postgresql/slave.conf"
        "database/postgresql/pg_hba.conf"
        "database/init.sql"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$PROJECT_ROOT/$file" ]]; then
            error_exit "Required file not found: $file"
        fi
    done
    
    log INFO "Prerequisites check passed ✓"
}

# Validate environment configuration
validate_environment() {
    log INFO "Validating environment configuration..."
    
    local env_file="$PROJECT_ROOT/.env.$ENVIRONMENT"
    
    if [[ ! -f "$env_file" ]]; then
        log WARN "Environment file not found: $env_file"
        log INFO "Creating from template..."
        
        if [[ -f "$PROJECT_ROOT/.env.${ENVIRONMENT}.template" ]]; then
            cp "$PROJECT_ROOT/.env.${ENVIRONMENT}.template" "$env_file"
            log WARN "Please edit $env_file with your actual configuration before proceeding"
            error_exit "Environment file needs configuration"
        else
            error_exit "No environment template found for $ENVIRONMENT"
        fi
    fi
    
    # Check for required environment variables
    local required_vars=(
        "POSTGRES_PASSWORD"
        "POSTGRES_REPLICATION_PASSWORD"
    )
    
    source "$env_file"
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            error_exit "Required environment variable $var is not set in $env_file"
        fi
    done
    
    log INFO "Environment configuration validated ✓"
}

# Setup Docker networks
setup_networks() {
    log INFO "Setting up Docker networks..."
    
    # Create network if it doesn't exist
    if ! docker network ls | grep -q "ainflue-network"; then
        docker network create ainflue-network
        log INFO "Created ainflue-network"
    fi
    
    if [[ "$SKIP_MONITORING" == "false" ]]; then
        if ! docker network ls | grep -q "ainflue-monitoring"; then
            docker network create ainflue-monitoring
            log INFO "Created ainflue-monitoring network"
        fi
    fi
    
    log INFO "Docker networks setup completed ✓"
}

# Deploy database infrastructure
deploy_database() {
    log INFO "Deploying database infrastructure..."
    
    cd "$PROJECT_ROOT"
    
    # Set environment file
    export ENV_FILE=".env.$ENVIRONMENT"
    
    # Stop existing containers if force recreate
    if [[ "$FORCE_RECREATE" == "true" ]]; then
        log INFO "Force recreating containers..."
        docker-compose -f docker-compose.production.yml --env-file "$ENV_FILE" down -v
    fi
    
    # Pull latest images
    log INFO "Pulling latest Docker images..."
    docker-compose -f docker-compose.production.yml --env-file "$ENV_FILE" pull
    
    # Deploy PostgreSQL master/slave setup
    log INFO "Starting PostgreSQL master/slave deployment..."
    docker-compose -f docker-compose.production.yml --env-file "$ENV_FILE" up -d postgres-master
    
    # Wait for master to be ready
    log INFO "Waiting for PostgreSQL master to be ready..."
    local retries=0
    local max_retries=30
    
    while [[ $retries -lt $max_retries ]]; do
        if docker-compose -f docker-compose.production.yml --env-file "$ENV_FILE" exec -T postgres-master pg_isready -U ainflue; then
            log INFO "PostgreSQL master is ready ✓"
            break
        fi
        
        retries=$((retries + 1))
        log INFO "Waiting for master... ($retries/$max_retries)"
        sleep 10
    done
    
    if [[ $retries -eq $max_retries ]]; then
        error_exit "PostgreSQL master failed to start within expected time"
    fi
    
    # Start slave
    log INFO "Starting PostgreSQL slave..."
    docker-compose -f docker-compose.production.yml --env-file "$ENV_FILE" up -d postgres-slave
    
    # Wait for slave to be ready
    log INFO "Waiting for PostgreSQL slave to be ready..."
    retries=0
    
    while [[ $retries -lt $max_retries ]]; do
        if docker-compose -f docker-compose.production.yml --env-file "$ENV_FILE" exec -T postgres-slave pg_isready -U ainflue; then
            log INFO "PostgreSQL slave is ready ✓"
            break
        fi
        
        retries=$((retries + 1))
        log INFO "Waiting for slave... ($retries/$max_retries)"
        sleep 10
    done
    
    if [[ $retries -eq $max_retries ]]; then
        error_exit "PostgreSQL slave failed to start within expected time"
    fi
    
    # Start other database services
    log INFO "Starting Redis and MongoDB..."
    docker-compose -f docker-compose.production.yml --env-file "$ENV_FILE" up -d redis mongodb
    
    log INFO "Database infrastructure deployment completed ✓"
}

# Setup monitoring
setup_monitoring() {
    if [[ "$SKIP_MONITORING" == "true" ]]; then
        log INFO "Skipping monitoring setup as requested"
        return
    fi
    
    log INFO "Setting up monitoring infrastructure..."
    
    cd "$PROJECT_ROOT"
    
    # Deploy monitoring stack
    docker-compose -f docker-compose.monitoring.yml --env-file ".env.$ENVIRONMENT" up -d
    
    # Wait for Prometheus to be ready
    log INFO "Waiting for monitoring services to be ready..."
    sleep 30
    
    # Check if services are healthy
    local services=("prometheus" "grafana" "alertmanager")
    
    for service in "${services[@]}"; do
        if docker-compose -f docker-compose.monitoring.yml ps "$service" | grep -q "Up"; then
            log INFO "$service is running ✓"
        else
            log WARN "$service may not be running properly"
        fi
    done
    
    log INFO "Monitoring setup completed ✓"
    log INFO "Access URLs:"
    log INFO "  - Prometheus: http://localhost:9090"
    log INFO "  - Grafana: http://localhost:3000 (admin/admin)"
    log INFO "  - AlertManager: http://localhost:9093"
}

# Run database optimization
run_optimization() {
    log INFO "Running database optimization..."
    
    cd "$PROJECT_ROOT"
    
    # Run the production deployment script
    if [[ -f "database/production_deployment.py" ]]; then
        log INFO "Running Python optimization script..."
        if command -v python3 &> /dev/null; then
            python3 database/production_deployment.py || log WARN "Python optimization script had issues"
        else
            log WARN "Python3 not found, skipping optimization script"
        fi
    fi
    
    log INFO "Database optimization completed ✓"
}

# Verify deployment
verify_deployment() {
    log INFO "Verifying deployment..."
    
    cd "$PROJECT_ROOT"
    
    # Check database connectivity
    log INFO "Testing database connectivity..."
    
    # Test master connection
    if docker-compose -f docker-compose.production.yml --env-file ".env.$ENVIRONMENT" exec -T postgres-master psql -U ainflue -d ainflue_platform -c "SELECT version();" > /dev/null; then
        log INFO "PostgreSQL master connection: OK ✓"
    else
        log ERROR "PostgreSQL master connection: FAILED ✗"
    fi
    
    # Test slave connection
    if docker-compose -f docker-compose.production.yml --env-file ".env.$ENVIRONMENT" exec -T postgres-slave psql -U ainflue -d ainflue_platform -c "SELECT version();" > /dev/null; then
        log INFO "PostgreSQL slave connection: OK ✓"
    else
        log ERROR "PostgreSQL slave connection: FAILED ✗"
    fi
    
    # Test replication
    log INFO "Testing replication..."
    local test_table="deployment_test_$(date +%s)"
    
    # Create test table on master
    docker-compose -f docker-compose.production.yml --env-file ".env.$ENVIRONMENT" exec -T postgres-master psql -U ainflue -d ainflue_platform -c "CREATE TABLE $test_table (id SERIAL PRIMARY KEY, created_at TIMESTAMP DEFAULT NOW());"
    
    # Insert test data
    docker-compose -f docker-compose.production.yml --env-file ".env.$ENVIRONMENT" exec -T postgres-master psql -U ainflue -d ainflue_platform -c "INSERT INTO $test_table DEFAULT VALUES;"
    
    # Wait for replication
    sleep 5
    
    # Check if data exists on slave
    if docker-compose -f docker-compose.production.yml --env-file ".env.$ENVIRONMENT" exec -T postgres-slave psql -U ainflue -d ainflue_platform -c "SELECT COUNT(*) FROM $test_table;" | grep -q "1"; then
        log INFO "Replication test: OK ✓"
    else
        log ERROR "Replication test: FAILED ✗"
    fi
    
    # Cleanup test table
    docker-compose -f docker-compose.production.yml --env-file ".env.$ENVIRONMENT" exec -T postgres-master psql -U ainflue -d ainflue_platform -c "DROP TABLE $test_table;"
    
    log INFO "Deployment verification completed ✓"
}

# Show deployment summary
show_summary() {
    log INFO "🎉 Ainflue Database Deployment Summary"
    log INFO "======================================"
    log INFO "Environment: $ENVIRONMENT"
    log INFO "PostgreSQL Master: postgres-master:5432"
    log INFO "PostgreSQL Slave: postgres-slave:5432"
    log INFO "Redis: redis:6379"
    log INFO "MongoDB: mongodb:27017"
    
    if [[ "$SKIP_MONITORING" == "false" ]]; then
        log INFO ""
        log INFO "Monitoring URLs:"
        log INFO "- Prometheus: http://localhost:9090"
        log INFO "- Grafana: http://localhost:3000"
        log INFO "- AlertManager: http://localhost:9093"
    fi
    
    log INFO ""
    log INFO "Next Steps:"
    log INFO "1. Access Grafana and import dashboards"
    log INFO "2. Configure alert notifications"
    log INFO "3. Run application services"
    log INFO "4. Perform load testing"
    log INFO ""
    log INFO "Log file: $LOG_FILE"
}

# Main deployment function
main() {
    log INFO "🚀 Starting Ainflue Database Production Deployment"
    log INFO "=================================================="
    
    parse_args "$@"
    
    check_prerequisites
    validate_environment
    setup_networks
    deploy_database
    setup_monitoring
    run_optimization
    verify_deployment
    show_summary
    
    log INFO "✅ Deployment completed successfully!"
}

# Trap errors and cleanup
trap 'error_exit "Script interrupted"' INT TERM

# Run main function with all arguments
main "$@"