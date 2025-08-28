#!/bin/bash
# =============================================================================
# AINFLUE PLATFORM - PRODUCTION DEPLOYMENT SCRIPT
# =============================================================================
# Comprehensive deployment script with health checks, rollback capabilities,
# and enterprise deployment patterns.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/tmp/ainflue-deployment-$(date +%Y%m%d-%H%M%S).log"
DEPLOYMENT_ENV="${DEPLOYMENT_ENV:-production}"
ROLLBACK_ENABLED="${ROLLBACK_ENABLED:-true}"
HEALTH_CHECK_TIMEOUT="${HEALTH_CHECK_TIMEOUT:-300}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARN: $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

# Cleanup function
cleanup() {
    log "Cleaning up temporary files..."
    # Add cleanup commands here
}

# Error handler
error_handler() {
    local line_number=$1
    error "Deployment failed at line $line_number"
    if [[ "$ROLLBACK_ENABLED" == "true" ]]; then
        warn "Initiating rollback..."
        rollback_deployment
    fi
    cleanup
    exit 1
}

# Set error trap
trap 'error_handler $LINENO' ERR
trap cleanup EXIT

# Banner
echo "
===============================================================================
🚀 AINFLUE PLATFORM - PRODUCTION DEPLOYMENT
===============================================================================
Environment: $DEPLOYMENT_ENV
Timestamp: $(date)
Log File: $LOG_FILE
===============================================================================
"

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks..."
    
    # Check Docker and Docker Compose
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        exit 1
    fi
    
    # Check required environment files
    local env_files=(".env.production" "nginx/ssl/certificate.crt" "nginx/ssl/private.key")
    for file in "${env_files[@]}"; do
        if [[ ! -f "$PROJECT_ROOT/$file" ]]; then
            warn "Required file missing: $file"
            if [[ "$file" == *".crt" ]] || [[ "$file" == *".key" ]]; then
                log "Generating self-signed SSL certificates for development..."
                mkdir -p "$PROJECT_ROOT/nginx/ssl"
                openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                    -keyout "$PROJECT_ROOT/nginx/ssl/private.key" \
                    -out "$PROJECT_ROOT/nginx/ssl/certificate.crt" \
                    -subj "/C=US/ST=State/L=City/O=Ainflue/CN=localhost"
            fi
        fi
    done
    
    # Check available disk space (minimum 10GB)
    local available_space=$(df "$PROJECT_ROOT" | awk 'NR==2{printf "%.0f", $4/1024/1024}')
    if [[ $available_space -lt 10 ]]; then
        warn "Low disk space: ${available_space}GB available. Minimum 10GB recommended."
    fi
    
    # Check available memory (minimum 8GB)
    local available_memory=$(free -g | awk 'NR==2{print $2}')
    if [[ $available_memory -lt 8 ]]; then
        warn "Low memory: ${available_memory}GB available. Minimum 8GB recommended."
    fi
    
    success "Pre-deployment checks completed"
}

# Build images
build_images() {
    log "Building Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Build main application image
    log "Building main application image..."
    docker build -f Dockerfile.production -t ainflue/platform:latest \
        --build-arg BUILD_ENV=production \
        --build-arg SECURITY_SCAN=true \
        .
    
    # Build service images
    local services=("ai" "crawler" "analytics")
    for service in "${services[@]}"; do
        log "Building $service service image..."
        docker build -f "docker/${service}.dockerfile" -t "ainflue/${service}:latest" .
    done
    
    # Build monetization service
    log "Building monetization service image..."
    docker build -f "docker/Dockerfile.monetization" -t "ainflue/monetization:latest" .
    
    success "Docker images built successfully"
}

# Security scan images
security_scan() {
    log "Running security scans on images..."
    
    local images=("ainflue/platform:latest" "ainflue/ai:latest" "ainflue/crawler:latest" 
                  "ainflue/analytics:latest" "ainflue/monetization:latest")
    
    for image in "${images[@]}"; do
        log "Scanning $image for vulnerabilities..."
        
        # Run Trivy scan if available
        if command -v trivy &> /dev/null; then
            trivy image --exit-code 0 --severity HIGH,CRITICAL "$image" || warn "High/Critical vulnerabilities found in $image"
        fi
        
        # Basic image inspection
        docker inspect "$image" > /dev/null || error "Image $image not found"
    done
    
    success "Security scans completed"
}

# Deploy infrastructure
deploy_infrastructure() {
    log "Deploying infrastructure services..."
    
    cd "$PROJECT_ROOT"
    
    # Start infrastructure services first
    docker-compose -f docker-compose.production.yml up -d \
        postgres-master postgres-slave \
        redis-master redis-slave \
        redis-sentinel-1 redis-sentinel-2 redis-sentinel-3 \
        mongodb-primary mongodb-secondary mongodb-arbiter
    
    # Wait for databases to be ready
    log "Waiting for databases to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose -f docker-compose.production.yml exec -T postgres-master pg_isready -U ainflue > /dev/null 2>&1; then
            break
        fi
        log "Waiting for PostgreSQL... (attempt $attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    if [[ $attempt -gt $max_attempts ]]; then
        error "PostgreSQL failed to start within timeout"
        exit 1
    fi
    
    success "Infrastructure services deployed"
}

# Deploy application services
deploy_application() {
    log "Deploying application services..."
    
    cd "$PROJECT_ROOT"
    
    # Deploy application instances
    docker-compose -f docker-compose.production.yml up -d \
        ainflue-app-1 ainflue-app-2 ainflue-app-3
    
    # Deploy microservices
    docker-compose -f docker-compose.production.yml up -d \
        crawler-service ai-service monetization-service analytics-service
    
    # Deploy load balancer
    docker-compose -f docker-compose.production.yml up -d nginx-loadbalancer
    
    success "Application services deployed"
}

# Deploy monitoring stack
deploy_monitoring() {
    log "Deploying monitoring stack..."
    
    cd "$PROJECT_ROOT"
    
    # Deploy monitoring services
    docker-compose -f docker-compose.production.yml up -d \
        prometheus grafana alertmanager \
        elasticsearch logstash kibana
    
    success "Monitoring stack deployed"
}

# Health checks
run_health_checks() {
    log "Running comprehensive health checks..."
    
    local services=(
        "ainflue-app-1:8000"
        "ainflue-app-2:8000" 
        "ainflue-app-3:8000"
        "ainflue-crawler-service:8001"
        "ainflue-monetization-service:8002"
        "ainflue-analytics-service:8003"
        "ainflue-ai-service:8004"
    )
    
    local max_attempts=30
    local healthy_services=0
    
    for service in "${services[@]}"; do
        local container_name="${service%:*}"
        local port="${service#*:}"
        local attempt=1
        local service_healthy=false
        
        log "Checking health of $container_name..."
        
        while [[ $attempt -le $max_attempts ]]; do
            if docker exec "$container_name" curl -f "http://localhost:$port/health" > /dev/null 2>&1; then
                success "$container_name is healthy"
                service_healthy=true
                ((healthy_services++))
                break
            fi
            
            log "Waiting for $container_name to be healthy... (attempt $attempt/$max_attempts)"
            sleep 10
            ((attempt++))
        done
        
        if [[ "$service_healthy" == false ]]; then
            error "$container_name failed health check"
        fi
    done
    
    log "Health check summary: $healthy_services/${#services[@]} services healthy"
    
    if [[ $healthy_services -eq ${#services[@]} ]]; then
        success "All services are healthy"
    else
        error "Some services failed health checks"
        exit 1
    fi
}

# Rollback function
rollback_deployment() {
    warn "Rolling back deployment..."
    
    cd "$PROJECT_ROOT"
    
    # Stop all services
    docker-compose -f docker-compose.production.yml down
    
    # Remove any new images (if needed)
    # This is a simplified rollback - in production you'd restore from backup
    
    warn "Rollback completed. Please check logs and fix issues before retrying."
}

# Post-deployment tasks
post_deployment_tasks() {
    log "Running post-deployment tasks..."
    
    # Database migrations (if needed)
    log "Running database migrations..."
    docker-compose -f docker-compose.production.yml exec -T ainflue-app-1 \
        python -m alembic upgrade head || warn "Database migration failed"
    
    # Cache warmup
    log "Warming up caches..."
    docker-compose -f docker-compose.production.yml exec -T ainflue-app-1 \
        python -m scripts.cache_warmup || warn "Cache warmup failed"
    
    # Generate deployment report
    log "Generating deployment report..."
    {
        echo "=== AINFLUE PLATFORM DEPLOYMENT REPORT ==="
        echo "Deployment Time: $(date)"
        echo "Environment: $DEPLOYMENT_ENV"
        echo "Git Commit: $(git rev-parse HEAD 2>/dev/null || echo 'N/A')"
        echo ""
        echo "=== RUNNING SERVICES ==="
        docker-compose -f docker-compose.production.yml ps
        echo ""
        echo "=== RESOURCE USAGE ==="
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    } > "/tmp/deployment-report-$(date +%Y%m%d-%H%M%S).txt"
    
    success "Post-deployment tasks completed"
}

# Main deployment function
main() {
    log "Starting Ainflue Platform deployment..."
    
    pre_deployment_checks
    build_images
    security_scan
    deploy_infrastructure
    deploy_application
    deploy_monitoring
    run_health_checks
    post_deployment_tasks
    
    success "🎉 Ainflue Platform deployment completed successfully!"
    log "Access the platform at: https://localhost"
    log "Monitoring: http://localhost:3000 (Grafana)"
    log "Logs: http://localhost:5601 (Kibana)"
    log "Deployment log: $LOG_FILE"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi