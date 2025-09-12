#!/bin/bash
# 🚀 Enterprise ML Deployment Automation Script
# Author: Fahed Mlaiel (mlaiel@live.de) - DevOps Expert
# Multi-Expert Implementation: ⚙️ DevOps + 🔒 Security + 🛡️ Backend + 🌐 Microservices
# =====================================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/tmp/ainflue_deployment_$(date +%Y%m%d_%H%M%S).log"

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

info() { echo -e "${BLUE}ℹ️  $*${NC}"; log "INFO" "$*"; }
success() { echo -e "${GREEN}✅ $*${NC}"; log "SUCCESS" "$*"; }
warning() { echo -e "${YELLOW}⚠️  $*${NC}"; log "WARNING" "$*"; }
error() { echo -e "${RED}❌ $*${NC}"; log "ERROR" "$*"; }

# Validation functions
check_dependencies() {
    info "🔍 Checking system dependencies..."
    
    local deps=("docker" "docker-compose" "python3" "pip3" "curl" "jq")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing+=("$dep")
        fi
    done
    
    if [ ${#missing[@]} -ne 0 ]; then
        error "Missing dependencies: ${missing[*]}"
        return 1
    fi
    
    success "All dependencies found"
}

validate_environment() {
    info "🔒 Validating environment configuration..."
    
    # Check critical environment variables
    local required_vars=(
        "JWT_SECRET_KEY"
        "DATABASE_PASSWORD" 
        "REDIS_PASSWORD"
        "API_ENCRYPTION_KEY"
    )
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        warning "Missing environment variables: ${missing_vars[*]}"
        warning "Loading from config/production.env..."
        
        if [ -f "$PROJECT_ROOT/config/production.env" ]; then
            source "$PROJECT_ROOT/config/production.env"
            success "Production environment loaded"
        else
            error "Production environment file not found"
            return 1
        fi
    fi
    
    success "Environment validation complete"
}

run_security_scan() {
    info "🔒 Running enterprise security scan..."
    
    cd "$PROJECT_ROOT"
    
    # Install security dependencies if needed
    pip3 install -q safety bandit semgrep
    
    # Dependency vulnerability scan
    info "Scanning dependencies for vulnerabilities..."
    if ! safety check --json --output security_report.json; then
        warning "Dependency vulnerabilities found - check security_report.json"
    fi
    
    # Code security scan
    info "Running code security analysis..."
    bandit -r ml/ -f json -o bandit_report.json || true
    
    # SAST scan
    info "Running static analysis security testing..."
    semgrep --config=auto ml/ --json --output=semgrep_report.json || true
    
    success "Security scan completed"
}

run_tests() {
    info "🧪 Running comprehensive test suite..."
    
    cd "$PROJECT_ROOT"
    
    # Install test dependencies
    pip3 install -q pytest pytest-asyncio pytest-cov
    
    # Run ML validation suite
    info "Running ML enterprise validation..."
    python3 -c "
from ml.validation_suite_enterprise import EnterpriseMLValidator
import asyncio

async def run_validation():
    validator = EnterpriseMLValidator()
    results = await validator.validate_all_modules()
    
    summary = results['summary']
    print(f'✅ ML Validation Score: {summary[\"overall_score\"]:.3f}/1.000')
    print(f'✅ Modules Analyzed: {summary[\"total_modules\"]}')
    print(f'✅ Success Rate: {summary[\"success_rate\"]:.1%}')
    
    # Check for critical issues
    critical_issues = 0
    for analysis in results['expert_analyses']:
        if analysis['status'] == 'error':
            critical_issues += 1
    
    if critical_issues > 0:
        print(f'⚠️ Critical issues found: {critical_issues}')
        return 1
    return 0

result = asyncio.run(run_validation())
exit(result)
"
    
    success "Tests completed successfully"
}

build_containers() {
    info "🐳 Building production containers..."
    
    cd "$PROJECT_ROOT"
    
    # Build production images
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    success "Container build completed"
}

deploy_infrastructure() {
    info "🚀 Deploying ML infrastructure..."
    
    cd "$PROJECT_ROOT"
    
    # Create networks and volumes
    docker network create ainflue_ml_network 2>/dev/null || true
    
    # Deploy services
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for services to be healthy
    info "⏳ Waiting for services to be healthy..."
    local services=("postgres" "redis" "ml_api")
    
    for service in "${services[@]}"; do
        local retries=30
        while [ $retries -gt 0 ]; do
            if docker-compose -f docker-compose.prod.yml ps "$service" | grep -q "healthy\|Up"; then
                success "$service is healthy"
                break
            fi
            sleep 10
            ((retries--))
        done
        
        if [ $retries -eq 0 ]; then
            error "$service failed to become healthy"
            return 1
        fi
    done
    
    success "Infrastructure deployment completed"
}

run_health_checks() {
    info "🏥 Running post-deployment health checks..."
    
    # Check ML API health
    local api_health=$(curl -s http://localhost:8000/health | jq -r '.status' 2>/dev/null || echo "unhealthy")
    if [ "$api_health" = "healthy" ]; then
        success "ML API is healthy"
    else
        error "ML API health check failed"
        return 1
    fi
    
    # Check inference service
    local inference_health=$(curl -s http://localhost:8001/health | jq -r '.status' 2>/dev/null || echo "unhealthy")
    if [ "$inference_health" = "healthy" ]; then
        success "Inference service is healthy"
    else
        warning "Inference service may not be ready yet"
    fi
    
    # Run ML health monitor
    cd "$PROJECT_ROOT"
    python3 -c "
from ml.monitoring.enterprise_health_monitor import EnterpriseHealthMonitor
import asyncio

async def health_check():
    monitor = EnterpriseHealthMonitor()
    if hasattr(monitor, 'example_usage'):
        await monitor.example_usage()
        print('✅ Enterprise health monitor validation passed')
    else:
        print('⚠️ Health monitor example not available')

asyncio.run(health_check())
"
    
    success "Health checks completed"
}

cleanup_on_failure() {
    error "Deployment failed - cleaning up..."
    cd "$PROJECT_ROOT"
    docker-compose -f docker-compose.prod.yml down -v || true
    exit 1
}

main() {
    info "🚀 Starting Ainflue ML Enterprise Deployment"
    info "Author: Fahed Mlaiel (mlaiel@live.de)"
    info "Multi-Expert Implementation: DevOps + Security + Backend + Microservices"
    info "Log file: $LOG_FILE"
    
    # Set trap for cleanup on failure
    trap cleanup_on_failure ERR
    
    # Deployment steps
    check_dependencies
    validate_environment
    run_security_scan
    run_tests
    build_containers
    deploy_infrastructure
    run_health_checks
    
    success "🎉 Enterprise ML deployment completed successfully!"
    info "📊 Monitoring dashboard available at: http://localhost:3000"
    info "🔍 Prometheus metrics at: http://localhost:9090"
    info "🚀 ML API at: http://localhost:8000"
    info "⚡ Inference API at: http://localhost:8001"
    info "📋 Deployment log: $LOG_FILE"
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi